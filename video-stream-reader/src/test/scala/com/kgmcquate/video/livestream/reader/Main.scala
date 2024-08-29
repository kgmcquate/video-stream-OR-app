package com.kgmcquate.video.livestream.reader

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions.{col, lit, struct, to_json}
import org.apache.spark.sql.streaming.Trigger
import KafkaConfig._

object Main {
  def main(args: Array[String]): Unit = {
    val url = "https://www.youtube.com/watch?v=ydYDqZQpim8"
    val spark = SparkSession.builder().appName("VideoStreamReader").getOrCreate()
    import spark.implicits._
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
      .trigger(Trigger.ProcessingTime((15L*1e3).toLong))
      .format("kafka")
      .option("kafka.bootstrap.servers", bootstrapServers)
      .option("kafka.security.protocol", "SASL_SSL")
      .option("kafka.sasl.jaas.config", s"org.apache.kafka.common.security.plain.PlainLoginModule required username='${kafkaApiKey}' password='${kafkaApiSecret}';")
      .option("kafka.sasl.mechanism", "PLAIN")
      .option("topic", "raw-video-frames")
      .option("checkpointLocation", "./checkpoints")
      .start()
      .awaitTermination()
  }
}
