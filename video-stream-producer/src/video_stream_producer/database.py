import json
import os
import boto3
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

secret_arn = os.environ.get("DB_CREDS_SECRET_ARN", "arn:aws:secretsmanager:us-east-1:117819748843:secret:main-rds-db-creds-3Izrf2")

db_endpoint = os.environ.get("DB_ENDPOINT" , "main-db.cu0bcthnum69.us-east-1.rds.amazonaws.com")


print("getting creds from sm")
secret = json.loads(
        boto3.client("secretsmanager", 'us-east-1')
        .get_secret_value(SecretId=secret_arn)
        ["SecretString"]
)

db_username = secret["username"]

db_password = secret["password"]

def get_jdbc_options():
    # from .database import db_endpoint, db_password, db_username
    jdbc_url = f"jdbc:postgresql://{db_endpoint}:5432/"

    # logger.debug(jdbc_url)

    return {
        "url": jdbc_url,
        "user": db_username,
        "password": db_password,
        "driver": "org.postgresql.Driver"
    }

sqlalchemy_url = f'postgresql+psycopg2://{db_username}:{db_password}@{db_endpoint}'

print("creating engine")
engine = sqlalchemy.create_engine(sqlalchemy_url) #/lake_freeze

video_streams_table = "video_streams"


metadata = MetaData(bind=engine)
Base = declarative_base(metadata=metadata)

