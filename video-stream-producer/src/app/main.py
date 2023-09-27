from typing import Callable, Any

# from pytube import YouTube
from pydantic.dataclasses import dataclass

import os
import json
import boto3
import socket


from .video_stream import VideoStream


class Config:
    arbitrary_types_allowed = True
    

def main():
    from .database import get_jdbc_options

    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()

    # video_ids = [
    #     # "DHUnz4dyb54",
    #     "w_DfTc7F5oQ"
    # ]

    video_ids = (
        spark.read
        .option("dbtable", "video_streams")
        .options(**get_jdbc_options())
        .format("jdbc")
        .load()
        .where("source_name = 'youtube' ")
        .select(
            # "source_name",
            "id"
        )
        .distinct()
        .rdd
        .map(lambda row: row.id)
        .collect()
    )

    print(f"{video_ids}")

    (
        spark.sparkContext
        .parallelize(video_ids, len(video_ids))
        .map(lambda id: VideoStream(
                streaming_service="youtube",
                video_id=id,
                capture_fps=0.5,
            )
        )
        .map(lambda stream: stream.start_stream())
        .collect()
    )

    # for video_id in video_ids:
    #     stream = VideoStream(
    #         streaming_service="youtube",
    #         video_id=video_id,
    #         capture_fps=0.5,
    #     )
    #     stream.start_stream()



if __name__ == "__main__":
    main()