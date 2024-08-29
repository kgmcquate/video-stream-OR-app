package com.kgmcquate.video.livestream.reader

object KafkaConfig {
  private val secretName = "arn:aws:secretsmanager:us-east-1:117819748843:secret:main_kafka_api_key-beAUbS"
  private val region = "us-east-1"

  private val secrets = SecretsManagerUtil.getSecret(secretName, region)

  val bootstrapServers: String = secrets("bootstrap_servers")
  val kafkaApiSecret: String = secrets("secret")
  val kafkaApiKey: String = secrets("key")

}
