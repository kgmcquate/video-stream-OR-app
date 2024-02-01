# Databricks notebook source
import json
import io
# from .kafka import kafka_config, raw_video_frames_topic_name, processed_video_frames_topic_name

from pulsar_config import token, broker_url, user, broker_host, pulsar_port, raw_video_frames_topic_name, processed_video_frames_topic_name

from classifiers import RawImageRecord, ProcessedImage
# from .image_stream_processor import ImageStreamProcessor

# from confluent_kafka import Consumer

from fastavro.types import AvroMessage
import fastavro

from avro_schemas import raw_image_avro_schema, processed_image_avro_schema

from concurrent.futures import ThreadPoolExecutor, wait, FIRST_EXCEPTION

from pyspark.sql import SparkSession
from fastavro import writer, reader, parse_schema

spark = SparkSession.builder.getOrCreate()

# COMMAND ----------

df = (
    spark
    .readStream
    .format("pulsar")
    .option("service.url", broker_url)
    .option("pulsar.client.authPluginClassName","org.apache.pulsar.client.impl.auth.AuthenticationToken")
    .option("pulsar.client.authParams", f"token:{token}")
    .option("topic", raw_video_frames_topic_name)
    .load()
    # .selectExpr("CAST(__key AS STRING)", "value")
)

# COMMAND ----------

from pyspark.sql.functions import udf, col, posexplode, explode
from pyspark.sql.types import IntegerType, BinaryType, ArrayType

@udf(returnType=ArrayType(BinaryType()))
def run_processing(key, avro_bytes):
    with io.BytesIO(avro_bytes) as bytes_io:
        reader = fastavro.reader(bytes_io, raw_image_avro_schema)
        messages = [msg for msg in reader]
    assert len(messages) == 1
    message = messages[0]

    raw_image = RawImageRecord(
        id=key,
        **message
    )

    processed_images = raw_image.process_image()

    avro_images = []
    for img in processed_images:
        bytes_writer = io.BytesIO()
        img_dict = img.to_record()
        fastavro.writer(bytes_writer, 
                        schema=processed_image_avro_schema, 
                        records=[img_dict]
        )
        avro_images.append(
            bytes_writer.getvalue()
        )

    return avro_images
(
    df
    .where("__key IS NOT NULL")
    .withColumn("processed_avro_records", run_processing(col("__key"), col("value")) )
    # .select("__key", "__eventTime", posexplode(col("processed_avro_records")) )
    # .selectExpr("concat(__key, '__', pos) AS __key", "col AS value", "__eventTime")
    .select("__key", "__eventTime", explode(col("processed_avro_records")).alias("value") )
    # .selectExpr("concat(__key, '__', pos) AS __key", "col AS value", "__eventTime")
    .writeStream
    .format("pulsar")
    .option("service.url", broker_url)
    .option("pulsar.client.authPluginClassName","org.apache.pulsar.client.impl.auth.AuthenticationToken")
    .option("pulsar.client.authParams", f"token:{token}")
    .option("topic", processed_video_frames_topic_name)
    .option("checkpointLocation", "./test")
    .start()
)

