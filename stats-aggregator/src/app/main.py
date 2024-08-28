from typing import List
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, lit, posexplode, explode, window, cast, avg, count
import pyspark.sql.functions as F
from pyspark.sql.types import IntegerType, BinaryType, ArrayType, StructType, StructField, StringType, TimestampType
import time 

from .records import ProcessedImageRecord
from .kafka_config import bootstrap_servers, kafka_api_key, kafka_api_secret, processed_video_frames_topic_name
from . import database

data_bucket = "data-zone-117819748843-us-east-1"


@udf(returnType=StructType([
    StructField("source_name", StringType()),
    StructField("video_id", StringType()),
    StructField("frame_ts", StringType()),
    StructField("detector_name", StringType()),
    StructField("detector_version", StringType()),
    StructField("object_name", StringType()),
    StructField("num_objects", IntegerType())
]))
def deserialize(avro_bytes) -> List[bytes]:
    img = ProcessedImageRecord.from_avro(avro_bytes)

    num_objects = len(json.loads(img.object_bounding_boxes_json))

    return {
        "source_name": img.source_name,
        "video_id": img.video_stream_id,
        "frame_ts": img.frame_ts,
        "detector_name": img.detector_name,
        "detector_version": img.detector_version,
        "object_name": img.object_name,
        "num_objects": num_objects
    }

def write_to_stats_table(df, epoch_id, jdbc_opts=database.get_jdbc_options(), tablename=database.video_stream_objects_stats_table ):
    df.persist()
    cnt = df.count()
    print(f"writing {cnt} to table")
    if cnt > 0:
        (
            df
            .withColumn("spark_epoch_id", lit(epoch_id))
            .write
            .format("jdbc")
            .mode("append")
            .options(**jdbc_opts)
            .option("dbtable", tablename)
            .save()
        )
        # (
        #     df
        #     .withColumn("spark_epoch_id", lit(epoch_id))
        #     .write
        #     .format("parquet")
        #     .mode("append")
        #     .save(f"s3://{data_bucket}/video_streams/{database.video_stream_objects_stats_table}/")
        # )
    df.unpersist()


def run_object_counts(df):
    object_counts_df = (
        df
        .withWatermark("frame_ts", "6 minutes") \
        .groupBy(
            window(col("frame_ts"), "5 minute").alias("time_window"),
            col("source_name"),
            col("video_id"),
            col("detector_name"),
            col("detector_version"),
            col("object_name")
        ) \
        .agg(
            F.avg(col("num_objects")).alias("avg_num_objects"),
            F.min(col("num_objects")).alias("min_num_objects"),
            F.max(col("num_objects")).alias("max_num_objects"),
            F.stddev(col("num_objects")).alias("stddev_num_objects"),
            count(lit("1")).alias("record_count")
        ) \
        .select(
            col("time_window.*"),
            col("source_name"),
            col("video_id"),
            col("detector_name"),
            col("detector_version"),
            col("object_name"),
            col("avg_num_objects"),
            col("min_num_objects"),
            col("max_num_objects"),
            col("stddev_num_objects"),
            col("record_count")
        )
    ) #.persist()


    (
        object_counts_df
        # .coalesce(1)
        .writeStream
        .option("checkpointLocation", f"s3://{data_bucket}/video_streams/{database.video_stream_objects_stats_table}/_checkpoints/")
        .outputMode("append") # will only write completed aggregations
        .trigger(processingTime='2 minutes')
        .foreachBatch(write_to_stats_table)
        .start()
        .awaitTermination()
    )

    # (
    #     object_counts_df
    #     .withColumn("seconds", )
    # )

def main(spark = SparkSession.builder.getOrCreate()):
    df = (
        spark
        .readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", bootstrap_servers)
        .option("kafka.security.protocol", "SASL_SSL")
        .option("kafka.sasl.jaas.config", f"org.apache.kafka.common.security.plain.PlainLoginModule required username='{kafka_api_key}' password='{kafka_api_secret}';")
        .option("kafka.sasl.mechanism", "PLAIN")
        .option("topic", processed_video_frames_topic_name)
        .load()
        .withColumn("frame_info_struct", deserialize(col("value")) )
        .select(col("frame_info_struct.*"))
        .withColumn("frame_ts", col("frame_ts").cast(TimestampType()))
    )

    run_object_counts(df)
