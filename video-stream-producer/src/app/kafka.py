import os, json, socket, boto3

KAFKA_CREDS_SECRET_ARN = os.environ.get("KAFKA_CREDS_SECRET_ARN", "arn:aws:secretsmanager:us-east-1:117819748843:secret:kafka-video-stream-creds-LauWmm")


kafka_secret = json.loads(
        boto3.client("secretsmanager", 'us-east-1')
        .get_secret_value(SecretId=KAFKA_CREDS_SECRET_ARN)
        ["SecretString"]
)


kafka_producer_config = {
    'bootstrap.servers': kafka_secret['bootstrap_servers'],
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': kafka_secret["key"],
    'sasl.password': kafka_secret["secret"],
    'client.id': socket.gethostname()
}

raw_video_frames_topic_name = "raw-livestream-frames"