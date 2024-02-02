from typing import Callable, Any

# from pytube import YouTube
from pydantic.dataclasses import dataclass

import logging
import os
import json
import boto3
import socket
import time
import datetime
from concurrent.futures import ThreadPoolExecutor, Future
import sqlalchemy

import database
from video_stream import VideoStream, StreamManager, StreamStatus


VIDEO_ID_REFRESH_PERIOD = 10
MAX_NUMBER_OF_STREAMS = 20
CAPTURE_FPS = 0.5

# MAX_FAILURES_BEFORE_PAUSE = 5
RETRY_PAUSE_TIME = datetime.timedelta(seconds=40)
MAX_NUMBER_FAILURES = 25

logger = logging.getLogger()

logger.setLevel(logging.INFO)
    
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



def main():
    # Main thread, monitor table

    # TODO log failures in table, don't start streams that have failed x times
    # TODO add update_timestamp to video table, so you can query recent changes

    stream_managers: StreamManager = []
    with ThreadPoolExecutor(max_workers=MAX_NUMBER_OF_STREAMS) as executor:
        while True:
            now = datetime.datetime.now(datetime.timezone.utc)

            logger.warn(f"Starting event loop {now}")
            
            with database.engine.connect() as conn:
                result = conn.execute(
                    sqlalchemy.text(f"SELECT id, source_name FROM {database.video_streams_table}")
                )
            
            # Get new streams
            new_stream_managers = [
                StreamManager(
                    VideoStream(
                        row.source_name,
                        row.id,
                        CAPTURE_FPS
                    )
                )
                for row 
                in result if row.id not in [m.video_stream.video_id for m in stream_managers]
            ]

            stream_managers += new_stream_managers

            for stream_manager in stream_managers:

                stream_manager.check_failure()

                if stream_manager.status == StreamStatus.FAILED and now - stream_manager.last_failure_time > RETRY_PAUSE_TIME:
                    stream_manager.recreate_stream()
                    stream_manager.status = StreamStatus.PENDING
                    print(f"Restarting stream {stream_manager.video_stream.video_id}")

                if len(stream_manager.failures) > MAX_NUMBER_FAILURES:
                    stream_manager.status = StreamStatus.REMOVED

                if stream_manager.status == StreamStatus.PENDING:
                    future = executor.submit(
                        lambda video_stream: video_stream.start_stream(), 
                        stream_manager.video_stream
                    )
                    stream_manager.status = StreamStatus.RUNNING
                    stream_manager.future = future
                
            time.sleep(VIDEO_ID_REFRESH_PERIOD)


if __name__ == "__main__":
    # test()
    main()