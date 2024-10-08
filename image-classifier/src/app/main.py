from typing import List
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, posexplode, explode
from pyspark.sql.types import IntegerType, BinaryType, ArrayType
import logging

from .kafka_config import bootstrap_servers, kafka_api_key, kafka_api_secret, processed_video_frames_topic_name
from .records import RawImageRecord, ProcessedImage

data_bucket = "data-zone-117819748843-us-east-1"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# log4jLogger = sc._jvm.org.apache.log4j
# logger = log4jLogger.LogManager.getLogger(__name__)
# logger.error('Hello, world!')

@udf(returnType=ArrayType(BinaryType()))
# @udf(returnType='list[bytes]', useArrow=True) # added in spark 3.5
def run_processing(key, avro_bytes) -> List[bytes]:
    raw_image = RawImageRecord.from_avro(key, avro_bytes)

    processed_images: List[ProcessedImage] = raw_image.process_image()

    avro_images: List[bytes] = [img.to_avro() for img in processed_images]

    return avro_images


def main(spark = SparkSession.builder.getOrCreate()):
    df = (
        spark
        .readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", bootstrap_servers)
        .option("kafka.security.protocol", "SASL_SSL")
        .option("kafka.sasl.jaas.config", f"org.apache.kafka.common.security.plain.PlainLoginModule required username='{kafka_api_key}' password='{kafka_api_secret}';")
        .option("kafka.sasl.mechanism", "PLAIN")
        .load()
    )

    (
        df
        # .where("__key IS NOT NULL")
        # .repartition(4)
        .withColumn("processed_avro_records", run_processing(col("__key"), col("value")) )
        # .select("__key", "__eventTime", posexplode(col("processed_avro_records")) )
        # .selectExpr("concat(__key, '__', pos) AS __key", "col AS value", "__eventTime")
        .select("__key", "__eventTime", explode(col("processed_avro_records")).alias("value") )
        # .selectExpr("concat(__key, '__', pos) AS __key", "col AS value", "__eventTime")
        .writeStream
        .trigger(processingTime='30 seconds')
        .format("kafka")
        .option("kafka.bootstrap.servers", bootstrap_servers)
        .option("kafka.security.protocol", "SASL_SSL")
        .option("kafka.sasl.jaas.config", f"org.apache.kafka.common.security.plain.PlainLoginModule required username='{kafka_api_key}' password='{kafka_api_secret}';")
        .option("kafka.sasl.mechanism", "PLAIN")
        .option("topic", processed_video_frames_topic_name)
        .option("checkpointLocation", f"s3://{data_bucket}/video_streams/processed_images/_checkpoints/")
        .start()
        .awaitTermination()
    )

if __name__ == "__main__":
    main()
