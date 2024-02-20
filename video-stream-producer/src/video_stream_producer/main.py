from typing import Callable, Any

# from pytube import YouTube
from pydantic.dataclasses import dataclass

import logging
import os
import json
import boto3
import socket
import time
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, Future
import sqlalchemy

from . import database
from .video_stream import VideoStream, StreamManager, StreamStatus


VIDEO_ID_REFRESH_PERIOD = 10
MAX_NUMBER_OF_STREAMS = 20
CAPTURE_FPS = 1 / 120
VIDEO_SEGMENT_FPS = 1

# MAX_FAILURES_BEFORE_PAUSE = 5
RETRY_PAUSE_TIME = timedelta(seconds=40)
MAX_NUMBER_FAILURES = 5

logger = logging.getLogger()

logger.setLevel(logging.INFO)
    
def test():
    from video_stream import VideoStream
    video_ids = [
        "3LXQWU67Ufk"
    ]

    for video_id in video_ids:
        stream = VideoStream(
            source_name="youtube",
            video_id=video_id,
            capture_fps=0.5,
        )
        stream.start_stream()



def main():
    # Main thread, monitor table

    from .sql_models import VideoStreams
    database.Base.metadata.create_all(database.engine)

    # TODO log failures in table, don't start streams that have failed x times
    # TODO add update_timestamp to video table, so you can query recent changes

    stream_managers: StreamManager = []
    
    with ThreadPoolExecutor(max_workers=MAX_NUMBER_OF_STREAMS) as executor:
        last_query_timestamp: datetime = None
        while True:
            now = datetime.now(timezone.utc)

            num_running_videos = len([sm for sm in stream_managers if sm.status == StreamStatus.RUNNING])
            if num_running_videos > MAX_NUMBER_OF_STREAMS:
                logger.error(f"Reached max number of streams: {num_running_videos}")

            logger.warn(f"{num_running_videos} videos running.")

            with database.engine.connect() as conn:
                stmt = sqlalchemy.select(VideoStreams).where(VideoStreams.is_active == True)
                # TODO implement and test on timezones
                if last_query_timestamp is not None:
                    stmt = stmt.where(VideoStreams.last_update_ts >= last_query_timestamp)
                result = conn.execute(stmt)
            
            # Get new streams
            new_stream_managers = [
                StreamManager(
                    VideoStream(
                        row.source_name,
                        row.video_id,
                        CAPTURE_FPS,
                        VIDEO_SEGMENT_FPS
                    )
                )
                for row 
                in result if row.video_id not in [m.video_stream.video_id for m in stream_managers]
            ]

            stream_managers += new_stream_managers

            for stream_manager in stream_managers:

                stream_manager.check_failure()

                if stream_manager.status == StreamStatus.FAILED and now - stream_manager.last_failure_time > RETRY_PAUSE_TIME:
                    stream_manager.recreate_stream()
                    stream_manager.status = StreamStatus.PENDING
                    print(f"Restarting stream {stream_manager.video_stream.video_id}")

                if len(stream_manager.failures) > MAX_NUMBER_FAILURES and stream_manager.status != StreamStatus.REMOVED:
                    stream_manager.status = StreamStatus.REMOVED
                    # Update streams table so it doesn't run again
                    with database.engine.connect() as conn:
                        conn.execute(
                            sqlalchemy.update(VideoStreams) \
                                .where(VideoStreams.source_name == stream_manager.video_stream.source_name) \
                                .where(VideoStreams.video_id == stream_manager.video_stream.video_id) \
                                .values(is_active=False, last_update_ts=datetime.now(timezone.utc))
                        )

                if stream_manager.status == StreamStatus.PENDING:
                    print(f"Starting new stream: {stream_manager.video_stream.video_id}")
                    future = executor.submit(
                        lambda video_stream: video_stream.start_stream(), 
                        stream_manager.video_stream
                    )
                    stream_manager.status = StreamStatus.RUNNING
                    stream_manager.future = future

                    time.sleep(VIDEO_ID_REFRESH_PERIOD / len(stream_managers)) # avoid api rate limiting
                
            time.sleep(VIDEO_ID_REFRESH_PERIOD)


if __name__ == "__main__":
    # test()
    main()