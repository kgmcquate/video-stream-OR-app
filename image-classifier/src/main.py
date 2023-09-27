from typing import Callable, Any

# from pytube import YouTube
from urllib.parse import urlunsplit, urlencode
from pydantic.dataclasses import dataclass
import dataclasses
import datetime
import time
import os
import json
import boto3
import socket

# import libraries
from vidgear.gears import CamGear
import cv2
import numpy as np

KAFKA_CREDS_SECRET_ARN = os.environ.get("KAFKA_CREDS_SECRET_ARN", "arn:aws:secretsmanager:us-east-1:117819748843:secret:kafka-video-stream-creds-LauWmm")

kafka_secret = json.loads(
        boto3.client("secretsmanager", 'us-east-1')
        .get_secret_value(SecretId=KAFKA_CREDS_SECRET_ARN)
        ["SecretString"]
)


kafka_producer_config = {
    'bootstrap.servers': kafka_secret['bootstrap_servers'],
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': kafka_secret["key"],
    'sasl.password': kafka_secret["secret"],
    'client.id': socket.gethostname()
}

raw_video_frames_topic_name = "raw-livestream-frames"




from classifiers import HAARClassifier, BaseObjectDetector, ProcessedImage

class Config:
    arbitrary_types_allowed = True


@dataclasses.dataclass #(config=Config)
class VideoStream:
    streaming_service: str
    video_id: str
    capture_fps: float
    url: str = None
    stream: CamGear = None
    object_detectors: list[BaseObjectDetector] = None

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
                **{"STREAM_RESOLUTION": "360p"}
            )
        
    #TODO make async
    # @staticmethod
    def process_frame(self, frame) -> list[ProcessedImage]:
        processed_frames = [
            detector.process(image=frame) 
            for detector in self.object_detectors
        ]

        return processed_frames


    def start_stream(self):

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
        def log_kafka_message_delivery(err, msg):
            """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """
            if err is not None:
                print('Message delivery failed: {}'.format(err))
            else:
                print('Message delivered to {}. Partition: [{}]'.format(msg.topic(), msg.partition()))

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

        import fastavro
        from fastavro import writer, reader, parse_schema
        import avro.schema
        import io
        from avro.datafile import DataFileReader, DataFileWriter
        from avro.io import DatumReader, DatumWriter

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
                            "jpeg_image": jpeg_bytes,
                            "metadata_json": json.dumps({})
                        }]
        )

        
        from confluent_kafka import Producer
        producer = Producer(kafka_producer_config)
        
        producer.poll(0)

        producer.produce(
            topic=raw_video_frames_topic_name,
            value=bytes_writer.getvalue(),
            key=f"{self.video_id}_{timestamp.isoformat()}",
            on_delivery=log_kafka_message_delivery
        )

        producer.flush()

        producer.poll(0)


    def stop_stream(self):
        self.stream.stop()

    def __enter__(self):
        self.start_stream()
    
    def __exit__(self):
        self.stop_stream()



video_ids = [
    # "DHUnz4dyb54",
    "w_DfTc7F5oQ"
]

for video_id in video_ids:
    stream = VideoStream(
        streaming_service="youtube",
        video_id=video_id,
        capture_fps=0.5,
        object_detectors=[
            #HAARClassifier(bounding_box_color=(0, 255,   0), haar_cascade_file = cv2.data.haarcascades + "haarcascade_fullbody.xml")
        ]
    )

    try:
        stream.start_stream()
    except Exception as e:
        raise e
    finally:
        stream.stop_stream()

cv2.destroyAllWindows()