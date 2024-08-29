package com.kgmcquate.video.livestream.reader

import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.services.secretsmanager.SecretsManagerClient
import software.amazon.awssdk.services.secretsmanager.model.GetSecretValueRequest
import software.amazon.awssdk.services.secretsmanager.model.SecretsManagerException
import spray.json._

object SecretsManagerUtil {
  def getSecret(secretName: String, region: String): Map[String, String] = {
    val client = SecretsManagerClient.builder()
      .region(Region.of(region))
      .credentialsProvider(DefaultCredentialsProvider.create())
      .build()

    try {
      val getSecretValueRequest = GetSecretValueRequest.builder()
        .secretId(secretName)
        .build()

      val getSecretValueResponse = client.getSecretValue(getSecretValueRequest)
      val secretString = getSecretValueResponse.secretString()

      secretString.parseJson.convertTo[Map[String, String]]
    } catch {
      case e: SecretsManagerException =>
        throw new RuntimeException(s"Failed to retrieve secret: ${e.awsErrorDetails().errorMessage()}", e)
    } finally {
      client.close()
    }
  }
}