import os, json, socket, boto3

PULSAR_CREDS_SECRET_ARN = os.environ.get("PULSAR_CREDS_SECRET_ARN", "arn:aws:secretsmanager:us-east-1:117819748843:secret:pulsar_video_stream_superuser_token-LGXnks")


secret = json.loads(
        boto3.client("secretsmanager", 'us-east-1')
        .get_secret_value(SecretId=PULSAR_CREDS_SECRET_ARN)
        ["SecretString"]
)

token = secret["token"]
user = secret["user"]
broker_host = secret["broker_host"]
pulsar_port = secret["pulsar_port"]

broker_url = f'pulsar://{broker_host}:{pulsar_port}'

raw_video_frames_topic_name = "video_stream/video_stream/raw-livestream-frames"  # "non-persistent://video_stream/video_stream/raw-livestream-frames"
processed_video_frames_topic_name = "video_stream/video_stream/processed-livestream-frames" #non-persistent://video_stream/video_stream/processed-livestream-frames"

# kafka_producer_config = {
#     'bootstrap.servers': kafka_secret['bootstrap_servers'],
#     'security.protocol': 'SASL_SSL',
#     'sasl.mechanism': 'PLAIN',
#     'sasl.username': kafka_secret["key"],
#     'sasl.password': kafka_secret["secret"],
#     'client.id': socket.gethostname()
# }

