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
# from vidgear.gears import CamGear
import cv2
import numpy as np
import fastavro

from .kafka import kafka_config, raw_video_frames_topic_name, processed_video_frames_topic_name

from classifiers import HAARClassifier, BaseObjectDetector, ProcessedImage

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


from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, StringType, BinaryType

from fastavro import writer, reader, parse_schema
import io

from .classifiers import RawImageRecord

spark = SparkSession.builder.getOrCreate()

def bytes_with_schema_to_avro(binary, avro_read_schema=parse_schema(avro_schema)):
    with io.BytesIO(binary) as bytes_io:
        reader = fastavro.reader(bytes_io, avro_read_schema)
        return next(reader)



stream = (
    spark
    .readStream
    .format("kafka")
    .options(
        **{f"kafka.{k}": v for k, v in kafka_config.items()}
    )
    .option("subscribe", raw_video_frames_topic_name)
    .load()
    .select("key", "value")
    .rdd
    .mapValues(bytes_with_schema_to_avro)
    .map(lambda key, record: RawImageRecord(key=key, **record))
    .flatMapValues(lambda record: record.process_image())
    .map(lambda key, image: {
            "key": f"{key}_{image.detector_name}_{image.object_name}",
            "value": image.to_json()
        }
    )
)

write_schema = StructType([
    StructField("key", StringType()),
    StructField("value", StringType())
])

(
    spark.createDataFrame(stream, schema=write_schema)
    .writeStream
    .format('kafka')
    .options(
        **{f"kafka.{k}": v for k, v in kafka_config.items()}
    )
    .option("topic", processed_video_frames_topic_name)
    .save()

)