from typing import Callable, Any

# from pytube import YouTube
from pydantic.dataclasses import dataclass

import os
import json
import boto3
import socket
import time
from concurrent.futures import ThreadPoolExecutor, Future
import sqlalchemy

import database
from video_stream import VideoStream, RunningStream


VIDEO_ID_REFRESH_PERIOD = 10
MAX_NUMBER_OF_STREAMS = 20
CAPTURE_FPS = 0.5
    
def test():
    from video_stream import VideoStream
    video_ids = [
        "3LXQWU67Ufk"
    ]

    for video_id in video_ids:
        stream = VideoStream(
            streaming_service="youtube",
            video_id=video_id,
            capture_fps=0.5,
        )
        stream.start_stream()

def spark_main():
    from .database import get_jdbc_options
    from .video_stream import VideoStream

    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()

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





def main():
    # Main thread, monitor table

    # TODO log failures in table, don't start streams that have failed x times
    # TODO add update_timestamp to video table, so you can query recent changes

    running_streams: RunningStream = []
    failed_streams: RunningStream = []
    with ThreadPoolExecutor(max_workers=MAX_NUMBER_OF_STREAMS) as executor:
        while True:
            with database.engine.connect() as conn:
                result = conn.execute(
                    sqlalchemy.text(f"SELECT id, source_name FROM {database.video_streams_table}")
                )
            
            streams = [
                VideoStream(
                    streaming_service=row.source_name,
                    video_id=row.id,
                    capture_fps=CAPTURE_FPS,
                ) for row 
                in result
            ]

            streams_to_run = [
                stream
                for stream
                in streams
                if stream.video_id not in [s.video_stream.video_id for s in running_streams]
            ]

            print(f"{len(streams_to_run)} new streams to run")

            for stream in streams_to_run:
                future = executor.submit(lambda stream: stream.start_stream(), stream)
                running_streams.append(
                    RunningStream(stream, future)
                )


            still_running_streams = []
            for running_stream in running_streams:
                assert isinstance(running_stream, RunningStream)
                if not running_stream.future.running:
                    if running_stream.future.exception():
                        print(f"Stream failed with exception: {running_stream.future.exception()}")
                        failed_streams.append(running_stream)
                    else:
                        raise NotImplementedError(f"Stream completed but isn't failed: {running_stream}")
                else:
                    still_running_streams.append(running_stream)
                
            running_streams = still_running_streams
                    

            time.sleep(VIDEO_ID_REFRESH_PERIOD)


if __name__ == "__main__":
    # test()
    main()