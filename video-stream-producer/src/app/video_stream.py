import dataclasses
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

from confluent_kafka import Producer

from urllib.parse import urlunsplit, urlencode

from .kafka import kafka_producer_config, raw_video_frames_topic_name

STREAM_RESOLUTION = "360p"


def log_kafka_message_delivery(err, msg):
    """ Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush(). """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()}. Partition: [{msg.partition()}]')


@dataclasses.dataclass #(config=Config)
class VideoStream:
    streaming_service: str
    video_id: str
    capture_fps: float
    url: str = None
    stream: CamGear = None

    def __post_init__(self):
        base_url = "http://youtube.com"

        params = {'v': self.video_id,}
        self.url = f'{base_url}/watch?{urlencode(params)}'
        self._init_stream()

    def _init_stream(self):
        self.stream = CamGear(
                source=self.url,  
                stream_mode = True,
                # backend=cv2.CAP_GSTREAMER 
                # logging=True
                **{"STREAM_RESOLUTION": STREAM_RESOLUTION}
            )


    def _start_stream(self):

        print(self.stream.framerate)
        # self.stream.ytv_metadata
        frame_period_ms = int(1e3 / self.stream.framerate)

        capture_period_ms = int(1e3 / self.capture_fps)

        self.stream.start()
        next_capture_time = datetime.datetime.now()


        while True:
            frame = self.stream.read()
            if frame is None:
                break

            now = datetime.datetime.now()

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

        
        
        producer = Producer(kafka_producer_config)
        
        producer.produce(
            topic=raw_video_frames_topic_name,
            value=bytes_writer.getvalue(),
            key=f"{self.video_id}_{timestamp.isoformat()}",
            on_delivery=log_kafka_message_delivery
        )

        producer.flush()

        producer.poll(0)


    def start_stream(self):
        try:
            self._start_stream()
        except Exception as e:
            raise e
        finally:
            self.stream.stop()


    def stop_stream(self):
        self.stream.stop()

    def __enter__(self):
        self.start_stream()
    
    def __exit__(self):
        self.stop_stream()
