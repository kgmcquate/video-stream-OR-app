
import json

from .kafka import kafka_config, raw_video_frames_topic_name, processed_video_frames_topic_name

from image_stream_processor import ImageStreamProcessor

from confluent_kafka import Consumer

from fastavro.types import AvroMessage
from fastavro import parse_schema

from kafka import kafka_config, raw_video_frames_topic_name, processed_video_frames_topic_name

from avro_schemas import raw_image_avro_schema, processed_image_avro_schema


from concurrent.futures import ThreadPoolExecutor, wait, FIRST_EXCEPTION

from pyspark.sql import SparkSession
from fastavro import writer, reader, parse_schema


def main():
    kafka_config['group.id'] = 'emr-serverless'

    src_partitions = Consumer(kafka_config).list_topics().topics[raw_video_frames_topic_name].partitions.keys()


    spark = SparkSession.builder.getOrCreate()

    (
        spark.parallelize(src_partitions, len(src_partitions))
        .map(lambda src_partition: ImageStreamProcessor(
                src_topic=raw_video_frames_topic_name,
                src_partition=src_partition,
                src_avro_schema=parse_schema(json.loads(raw_image_avro_schema)),
                tgt_topic=processed_video_frames_topic_name,
                tgt_avro_schema=parse_schema(json.loads(processed_image_avro_schema)),
                kafka_config=kafka_config
            )
        )
        .map(lambda processor: processor.consume())
        .collect()
    )


def test():
    src_partitions = Consumer(kafka_config).list_topics().topics[raw_video_frames_topic_name].partitions.keys()

    processors = [
        ImageStreamProcessor(
            src_topic=raw_video_frames_topic_name,
            src_partition=0,
            src_avro_schema=parse_schema(json.loads(raw_image_avro_schema)),
            tgt_topic=processed_video_frames_topic_name,
            tgt_avro_schema=parse_schema(json.loads(processed_image_avro_schema)),
            kafka_config=kafka_config
        )
        for partition 
        in src_partitions
    ]

    with ThreadPoolExecutor(max_workers=len(src_partitions)) as executor:
        futures = [
            executor.submit(lambda processor: processor.consume(), processor)
            for processor in processors
        ]

        completed_futures, uncompleted_futures = wait(
            futures,
            return_when=FIRST_EXCEPTION
        )

        for future in uncompleted_futures:
            future.result()
        