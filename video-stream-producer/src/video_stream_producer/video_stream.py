import dataclasses
from enum import Enum

import fastavro
from fastavro import writer, reader, parse_schema

# from vidgear.gears import CamGear
import cv2
import numpy as np
from datetime import datetime, timedelta, timezone
import time
import io
import json
import boto3
import socket
import os
import logging
from concurrent.futures import Future
# import pulsar
import av
import m3u8
import streamlink
# from confluent_kafka import Producer
import requests
import traceback
import pprint

from confluent_kafka import Producer

from urllib.parse import urlunsplit, urlencode
from urllib.error import HTTPError

# from .kafka import kafka_producer_config, raw_video_frames_topic_name
# from .pulsar_config import broker_url, token, raw_video_frames_topic_name
# from .kafka_config import raw_video_frames_topic_name, kafka_api_key, kafka_api_secret, bootstrap_servers
from .avro_schemas import raw_image_avro_schema


logger = logging.getLogger()

STREAM_RESOLUTIONS = ["720p", "480p", "360p"] # in order of priority
EMPTY_FRAMES_TIMEOUT_MINUTES = 15
LOG_AFTER_N_FRAMES = 10
VIDEO_SEGMENT_NUM_FRAMES_LIMIT = 2

# def log_kafka_message_delivery(err, msg):
#     """ Called once for each message produced to indicate delivery result.
#     Triggered by poll() or flush(). """
#     if err is not None:
#         print(f'Message delivery failed: {err}')
#     else:
#         print(f'Message delivered to {msg.topic()}. Partition: [{msg.partition()}]')


class StreamStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    # STOPPED = "STOPPED"
    REMOVED = "REMOVED"



@dataclasses.dataclass #(config=Config)
class VideoStream:
    source_name: str
    video_id: str
    capture_fps: float
    segment_fps: float
    url: str = None


    def __post_init__(self):
        base_url = "http://youtube.com"

        # client.close()
        self.frame_time = timedelta(microseconds=int(1e6/self.capture_fps) )

        params = {'v': self.video_id,}
        self.url = f'{base_url}/watch?{urlencode(params)}'

        
        import socket

        # conf = {'bootstrap.servers': bootstrap_servers,
        #         'client.id': socket.gethostname()}

        # producer = Producer(conf)

        # self.kafka_client = 

        # self.producer = self.kafka_client.create_producer(raw_video_frames_topic_name)


    def get_frames_from_segment(self, video_bytes, segment_start_time: datetime):
        with av.open(io.BytesIO(video_bytes)) as container:
            # print(container.duration)
            # framerate
            stream = container.streams.video[0]

            num_frames = 0
            for frame in container.decode(stream):
                segment_framerate = stream.codec_context.framerate # this is None until container.decode(stream) is called
                skip_n_frames = int(segment_framerate / self.segment_fps)

                index = frame.index
                get_frame = index % skip_n_frames == 0
                if get_frame:
                    num_frames += 1
                    microsec_offset = int(index * (1/segment_framerate) * 1e6)
                    frame_ts = segment_start_time + timedelta(microseconds=microsec_offset)
                    self.write_frame_to_broker(frame.to_ndarray(), frame_ts)

                if num_frames >= VIDEO_SEGMENT_NUM_FRAMES_LIMIT:
                    break
                
            self.producer.flush()
            print(f"{self.video_id}: wrote {num_frames} frames for {int(container.duration / 1e6)}s video segment")

    def _start_stream(self):
        # print(f"{self.frame_time.total_seconds()=}")
        last_segment_start_time = datetime.now(timezone.utc) - self.frame_time - self.frame_time
        while True:
            new_segment_requests = 0
            while True:
                processing_start_time = datetime.now(timezone.utc)

                next_segment_wait_time = (self.frame_time - (processing_start_time - last_segment_start_time - self.frame_time)).total_seconds()
                # print(f"{next_segment_wait_time=}")
                if next_segment_wait_time > 0:# Check if the next segment needs to be read at all
                    print(f"{self.video_id}: waiting for next segment: {next_segment_wait_time} s")
                    time.sleep(next_segment_wait_time)

                # Run until there is a new segment
                streams = streamlink.streams(self.url)
                new_segment_requests += 1
                # pprint(f"{streams=}")

                stream_url = None
                for resolution in STREAM_RESOLUTIONS:
                    if resolution in streams.keys():
                        stream_url = streams[resolution]
                        break
                if stream_url is None:
                    raise Exception(f"No appropriate resolution found for {self.video_id}: {list(streams.keys())}")
                # pprint(f"{stream_url=}")

                try:
                    m3u8_obj = m3u8.load(stream_url.args['url'])
                except HTTPError as e:
                    logger.error(f"{self.video_id} raised HTTP exception: {e}")
                    if "HTTP Error 429: Too Many Requests" in str(e):
                        time.sleep(5)
                    raise e
                    #HTTP Error 429: Too Many Requests

                stream_segment = m3u8_obj.segments[0] # try different segments

                # Poll for a new segment to be available
                segment_start_time = stream_segment.program_date_time
                if segment_start_time != last_segment_start_time: # checking that this is a new segment
                    last_segment_start_time = segment_start_time
                    if new_segment_requests > 1:
                        logger.warning(f"{self.video_id}: requested new segment {new_segment_requests} times")
                    break
                else:
                    time.sleep(0.05)
                    continue
        
            resp = requests.get(stream_segment.uri)
            resp.raise_for_status()
            video_bytes = resp.content

            self.get_frames_from_segment(video_bytes, segment_start_time)
            
            # wait until next segment should be available
            processing_end_time = datetime.now(timezone.utc)
            processing_seconds = (processing_end_time - processing_start_time).total_seconds()
            # print(f"{processing_seconds=}")
            sleep_time = stream_segment.duration - processing_seconds - 0.1 # fudge factor
            # print(stream_segment.duration)
            # print(sleep_time)

            if sleep_time > 0:
                print(f"{self.video_id}: sleep for {sleep_time}")
                time.sleep(sleep_time)
            # else:
            #     logger.warning(f"{self.video_id}: video segment processing time greater than segment duration: {processing_seconds=} {stream_segment.duration=} ")

    def write_frame_to_broker(self, frame: np.array, timestamp: datetime):

        bytes_writer = io.BytesIO()

        success, encoded_image = cv2.imencode('.jpeg', frame)
        if not success:
            raise Exception(f"Error encoding frame as jpeg: {self}")
        jpeg_bytes = encoded_image.tobytes()

        fastavro.writer(bytes_writer, 
                        schema=raw_image_avro_schema, 
                        records=[{
                            # "key": f"{self.video_id}_{timestamp.isoformat()}",
                            "source_name": self.source_name,
                            "video_stream_id": self.video_id,
                            "frame_ts": timestamp.isoformat(),
                            "jpeg_image": jpeg_bytes,
                            "metadata_json": json.dumps({})
                        }]
        )

        # logger.warn(f"writing {self.video_id}")
        # raise Exception("here")
        print(bytes_writer.getvalue())
        # self.producer.send(
        #     bytes_writer.getvalue(),
        #     event_timestamp=int(timestamp.timestamp() * 1e3),
        #     # sequence_id=
        #     partition_key=f"{self.video_id}-{timestamp.isoformat()}",
        #     # ordering_key=str(int(timestamp.timestamp() * 1e3))
        # )
        

    def start_stream(self):
        print(f"{self.video_id}: starting stream...")
        try:
            self._start_stream()
        except Exception as e:
            raise e
        finally:
            self.stop_stream()


    def stop_stream(self):
        pass
        # self.producer.flush()
        # self.kafka_client.close()
        # self.stream.stop()

    def __enter__(self):
        self.start_stream()
    
    def __exit__(self):
        self.stop_stream()



@dataclasses.dataclass
class StreamManager:
    video_stream: VideoStream
    future: Future = None
    start_time: datetime = dataclasses.field(default_factory=lambda: datetime.now(timezone.utc))
    status: StreamStatus = StreamStatus.PENDING
    last_failure_time: datetime = None
    failures: dict[datetime, Exception] = dataclasses.field(default_factory=lambda: {})
    

    def check_failure(self):
        if self.future is not None and not self.future.running():
            if self.future.exception():
                traceback_msg = ''.join(traceback.TracebackException.from_exception(self.future.exception()).format())
                logger.exception(f"Stream failed with exception: {self.future.exception()} \n{traceback_msg}")
                self.status = StreamStatus.FAILED
                now = datetime.now(timezone.utc)
                self.last_failure_time = now
                self.failures[now] = self.future.exception()
                self.future = None
                # return True
            else:
                raise NotImplementedError(f"Stream completed but isn't failed: {self.future.result()}")


    def recreate_stream(self):
        new_video_stream = VideoStream(
            self.video_stream.source_name,
            self.video_stream.video_id,
            self.video_stream.capture_fps,
            self.video_stream.segment_fps
        )

        self.video_stream = new_video_stream