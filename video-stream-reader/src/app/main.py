from typing import List
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, lit, posexplode, explode, window, cast, avg, count, to_json, struct
from pyspark.sql.types import IntegerType, BinaryType, ArrayType, StructType, StructField, StringType, TimestampType
import time 

from .records import ProcessedImageRecord
from .kafka_config import bootstrap_servers, kafka_api_key, kafka_api_secret, processed_video_frames_topic_name
from . import database


def main(spark: SparkSession = SparkSession.builder.getOrCreate()):
    url = "https://www.youtube.com/watch?v=ydYDqZQpim8"

    (
        spark
        .readStream
        .format("com.kgmcquate.spark.livestream.LivestreamReader")
        .option("url", url)
        .option("resolution", "1920x1080")
        .load()
        .select(
            to_json(
                struct(
                    lit(url).alias("url"),
                    col("ts")
                )
            ).alias("key"),
            col("frame_data").alias("value")
        )
        .writeStream
        .trigger(processingTime='10 seconds')
        .format("kafka")
        .option("kafka.bootstrap.servers", bootstrap_servers)
        .option("kafka.security.protocol", "SASL_SSL")
        .option("kafka.sasl.jaas.config", f"org.apache.kafka.common.security.plain.PlainLoginModule required username='{kafka_api_key}' password='{kafka_api_secret}';")
        .option("kafka.sasl.mechanism", "PLAIN")
        .option("topic", "raw-video-frames")
        .option("checkpointLocation", "./checkpoints")
        .start()
        .awaitTermination()
    )

