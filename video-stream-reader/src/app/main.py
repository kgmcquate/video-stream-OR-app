from typing import List
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, lit, posexplode, explode, window, cast, avg, count
import pyspark.sql.functions as F
from pyspark.sql.types import IntegerType, BinaryType, ArrayType, StructType, StructField, StringType, TimestampType
import time 

from .records import ProcessedImageRecord
from .pulsar_config import token, broker_url, processed_video_frames_topic_name
from . import database


def main(spark = SparkSession.builder.getOrCreate()):
    df = (
        spark
        .readStream
        .format("com.kgmcquate.spark.livestream.LivestreamReader")
        .option("url", "https://www.youtube.com/watch?v=ydYDqZQpim8")
        .option("resolution", "1920x1080")
        .load()
        .select(
            to_json(
            struct(
                lit(url).as("url"),
                col("ts")
            )
            ).as("key"),
            col("frame_data").as("value")
        )
        .writeStream
        .trigger()
        .format("kafka")
        .option("kafka.bootstrap.servers", "pkc-p11xm.us-east-1.aws.confluent.cloud:9092")
        .option("kafka.security.protocol", "SASL_SSL")
        .option("kafka.sasl.jaas.config", s"org.apache.kafka.common.security.plain.PlainLoginModule required username='$confluent_cloud_api_key' password='$confluent_cloud_api_secret';")
        .option("kafka.sasl.mechanism", "PLAIN")
        .option("topic", "raw-video-frames")
        .option("checkpointLocation", "./checkpoints")
    )

    run_object_counts(df)
