import requests
import json
import boto3
import os

from data_models import VideoStreamInfo

YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"

secret_arn = "arn:aws:secretsmanager:us-east-1:117819748843:secret:youtube_api_key"

youtube_api_token = json.loads(
        boto3.client("secretsmanager", 'us-east-1')
        .get_secret_value(SecretId=secret_arn)
        ["SecretString"]
    )['key']

def get_youtube_video_info(video_id: str):
    url = f"{YOUTUBE_API_BASE_URL}/videos?part=snippet%2CcontentDetails%2Cstatistics&id={video_id}&key={youtube_api_token}"
    resp = requests.get(
        url=url,
        # headers={
        #     "Authorization": f"Bearer {youtube_api_token}",
        #     "Accept": "application/json"
        # }
    )
    resp.raise_for_status()

    return VideoStreamInfo.from_youtube_api_response(resp.json())