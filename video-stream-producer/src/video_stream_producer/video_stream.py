import dataclasses
from enum import Enum

import fastavro
from fastavro import writer, reader, parse_schema

from vidgear.gears import CamGear
import cv2
import numpy as np
import datetime
import time
import io
import json
import boto3
import socket
import os
import logging
from concurrent.futures import Future

# from confluent_kafka import Producer

from urllib.parse import urlunsplit, urlencode

# from .kafka import kafka_producer_config, raw_video_frames_topic_name
from pulsar_config import broker_url, token, user, broker_host, pulsar_port, raw_video_frames_topic_name

import pulsar

logger = logging.getLogger()

STREAM_RESOLUTION = "360p"


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
    streaming_service: str
    video_id: str
    capture_fps: float
    url: str = None
    stream: CamGear = None


    def __post_init__(self):
        base_url = "http://youtube.com"

        # client.close()

        params = {'v': self.video_id,}
        self.url = f'{base_url}/watch?{urlencode(params)}'
        # self._init_stream()
        self.stream: CamGear = None

    def _init_stream(self):
        self.stream = CamGear(
                source=self.url,  
                stream_mode = True,
                # backend=cv2.CAP_GSTREAMER 
                # logging=True
                **{"STREAM_RESOLUTION": STREAM_RESOLUTION}
            )
        
        
        self.pulsar_client = pulsar.Client(
            broker_url,
            authentication = pulsar.AuthenticationToken(token)
        )

        self.producer = self.pulsar_client.create_producer(raw_video_frames_topic_name)

    def _start_stream(self):
        if self.stream is None:
            self._init_stream()

        # print(self.stream.framerate)
        # self.stream.ytv_metadata
        frame_period_ms = int(1e3 / self.stream.framerate)

        capture_period_ms = int(1e3 / self.capture_fps)

        self.stream.start()
        self.status = StreamStatus.RUNNING

        next_capture_time = datetime.datetime.now(datetime.timezone.utc)


        while True:
            frame = self.stream.read()
            if frame is None:
                break

            now = datetime.datetime.now(datetime.timezone.utc)

            if now > next_capture_time:
                # read frame
                self.write_frame_to_kafka(frame, now)

                next_capture_time = next_capture_time + datetime.timedelta(milliseconds=capture_period_ms)

                # do something with frame here
                # processed_frames = self.process_frame(frame)
                
                # cv2.imshow("Output Frame", frame)
                # cv2.imshow(processed_frames[0].detector_name, processed_frames[0].image)

                # cv2.waitKey(1)
                time.sleep(0.001)
            else:
                pass


    def write_frame_to_kafka(self, frame: np.array, timestamp: datetime.datetime):

        avro_schema = """
{
    "type": "record",
    "namespace": "com.mycorp.mynamespace",
    "name": "sampleRecord",
    "doc": "Sample schema to help you get started.",
    "fields": [
        {
            "name": "video_stream_id",
            "type": "string",
            "doc": "id for video stream taken from source"
        },
        {
            "name": "frame_ts",
            "type": "string",
            "doc": "timestamp of when the frame was initially ingested"
        },
        {
            "name": "jpeg_image",
            "type": "bytes",
            "doc": "jpeg image"
        },
        {
            "name": "metadata_json",
            "type": "string",
            "doc": "Any additional information in json format"
        }
    ]
}
        """



        # schema = avro.schema.parse(avro_schema)
        # avro_writer = avro.io.DatumWriter(schema)

        schema = parse_schema(json.loads(avro_schema))

        bytes_writer = io.BytesIO()

        success, encoded_image = cv2.imencode('.jpeg', frame)
        jpeg_bytes = encoded_image.tobytes()

        fastavro.writer(bytes_writer, 
                        schema=schema, 
                        records=[{
                            # "key": f"{self.video_id}_{timestamp.isoformat()}",
                            "video_stream_id": self.video_id,
                            "frame_ts": timestamp.isoformat(),
                            "jpeg_image": jpeg_bytes,
                            "metadata_json": json.dumps({})
                        }]
        )

        logger.warn("writing ")
        # raise Exception("here")
        self.producer.send(
            bytes_writer.getvalue(),
            event_timestamp=int(timestamp.timestamp() * 1e3),
            # sequence_id=
            partition_key=f"{self.video_id}-{timestamp.isoformat()}",
            # ordering_key=str(int(timestamp.timestamp() * 1e3))
        )

            #         properties=None,
            #  partition_key=None,
            #  ordering_key=None,
            #  sequence_id=None,
            #  replication_clusters=None,
            #  disable_replication=False,
            #  event_timestamp=None,
            #  deliver_at=None,
            #  deliver_after=None,
        self.producer.flush()

        
        
        # producer = Producer(kafka_producer_config)
        
        # producer.produce(
        #     topic=raw_video_frames_topic_name,
        #     value=bytes_writer.getvalue(),
        #     key=f"{self.video_id}_{timestamp.isoformat()}",
        #     on_delivery=log_kafka_message_delivery
        # )

        # producer.flush()

        # producer.poll(0)


    def start_stream(self):
        try:
            self._start_stream()
        except Exception as e:
            raise e
        finally:
            self.stop_stream()


    def stop_stream(self):
        # self.pulsar_client.close()
        self.stream.stop()

    def __enter__(self):
        self.start_stream()
    
    def __exit__(self):
        self.stop_stream()



@dataclasses.dataclass
class StreamManager:
    video_stream: VideoStream
    future: Future = None
    start_time: datetime.datetime = dataclasses.field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    status: StreamStatus = StreamStatus.PENDING
    last_failure_time: datetime.datetime = None
    failures: dict[datetime.datetime, Exception] = dataclasses.field(default_factory=lambda: {})
    

    def check_failure(self):
        if self.future is not None and not self.future.running():
            if self.future.exception():
                logger.exception(f"Stream failed with exception: {self.future.exception()}")
                self.status = StreamStatus.FAILED
                now = datetime.datetime.now(datetime.timezone.utc)
                self.last_failure_time = now
                self.failures[now] = self.future.exception()
                self.future = None
                # return True
            else:
                raise NotImplementedError(f"Stream completed but isn't failed: {self.result()}")

        # return False

    def recreate_stream(self):
        new_video_stream = VideoStream(
            self.video_stream.streaming_service,
            self.video_stream.video_id,
            self.video_stream.capture_fps
        )

        self.video_stream = new_video_stream