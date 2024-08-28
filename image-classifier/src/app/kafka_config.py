import json, boto3

secret_arn = "arn:aws:secretsmanager:us-east-1:117819748843:secret:main_kafka_api_key-beAUbS"

secret = json.loads(
        boto3.client("secretsmanager", 'us-east-1')
        .get_secret_value(SecretId=secret_arn)
        ["SecretString"]
)

kafka_api_key = secret["key"]
kafka_api_secret = secret["secret"]
bootstrap_servers = secret["bootstrap_servers"]




