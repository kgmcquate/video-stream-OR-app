from typing import Annotated
import functools

from fastapi import FastAPI, BackgroundTasks, Response, Query
from fastapi.responses import HTMLResponse
# from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware

from sqlmodel import Session, select, text
from sqlalchemy.sql.operators import is_, or_, and_
from sqlalchemy.dialects.postgresql import insert
from mangum import Mangum
import json
import boto3
from typing import Optional
import datetime
import logging

from data_models import VideoStream, VideoStreamsResponse, VideoStreamInfo, VideoStreamObjectsStats, VideoRankings, OverallObjectRanking, ObjectCountsArrays, ObjectRankingArrays
from youtube_api import get_youtube_video_info
from database import engine


from sqlmodel import SQLModel
SQLModel.metadata.create_all(engine)

app = FastAPI()


@app.get("/home", response_class=HTMLResponse)
def get_home_page():
    return """
    <html>
        <body>
         Hello World
        </body>
    </html>
    """

@app.get("/video_stream")
def get_video_streams(
        limit: int = 50,
        active: bool = True # only return active streams
    ) -> VideoStreamsResponse:
    with Session(engine) as session:
        is_active_sql = "true" if active else "false"
        statement = text(f"""
                         SELECT source_name, video_id, is_active, insert_ts, last_update_ts, avg_num_objects
                         FROM {VideoRankings.__tablename__} 
                         WHERE is_active = {is_active_sql} 
                         LIMIT {limit}""")

        video_streams = session.exec(statement).all()

        print(video_streams)

    video_streams = [VideoRankings(*row) for row in video_streams]

    return VideoStreamsResponse(video_streams)


@app.get("/video_stream_info")
def get_video_streams_info(
        ids: str = None,
        limit: int = 50
    ) -> dict:
    # TODO doesn't return aything if no ids given
    ids_list = []
    
    with Session(engine) as session:
        statement = select(VideoStreamInfo)

        if ids:
            ids_list = ids.split(",")
            statement = statement.where(VideoStreamInfo.video_id.in_(ids_list))
        
        statement = statement.limit(limit)
        
        existing_video_streams = session.exec(statement).all()

    existing_ids = [video.video_id for video in existing_video_streams]

    # print(f"{existing_ids=}")

    video_ids_to_fetch_info = [
        id
        for id
        in ids_list
        if id not in existing_ids
    ]

    print(f"{video_ids_to_fetch_info=}")

    new_video_streams: list[VideoStreamInfo] = []
    for id in video_ids_to_fetch_info:
        new_video_streams.append(
            get_youtube_video_info(id)
        )

    print(f"{new_video_streams=}")

    with engine.connect() as conn:
        for stream in new_video_streams:
            stmt = insert(VideoStreamInfo).values(stream.dict())
            stmt = stmt.on_conflict_do_nothing()  #left anti join for insert
            result = conn.execute(stmt)
        conn.commit()

    # return streams in the original order
    video_streams = []
    for id in ids_list:
        stream_ = [stream for stream in existing_video_streams + new_video_streams if stream.video_id == id]
        assert len(stream_) == 1

        video_streams.append(
            stream_[0]
        )

    # return VideoInfosResponse(video_streams)
    return {
        "video_infos": video_streams
    }
    

@app.get("/video_stream/objects_stats")
def get_video_objects_stats(
        ids: str = None,
        start_time: datetime.datetime | None = datetime.datetime.now() - datetime.timedelta(days=3),
        end_time: datetime.datetime | None = None,
        min_num_objects: float = 0,
        limit: int = 50
    ): # -> list[VideoStreamObjectsStats]

    # print(ids)

    with Session(engine) as session:
        statement = select(VideoStreamObjectsStats)

        print(statement)

        if ids:
            ids_list = ids.split(",")
            statement = statement.where(VideoStreamObjectsStats.video_id.in_(ids_list))

        statement = statement.where(VideoStreamObjectsStats.start >= start_time)

        if end_time:
            statement = statement.where(VideoStreamObjectsStats.end <= end_time)

        statement = statement.where(VideoStreamObjectsStats.avg_num_objects > min_num_objects)

        statement = statement.limit(limit)

        # print(statement)

        stats = session.exec(statement).all()

        # print(stats)

    return stats


@app.get("/video_stream/object_counts")
def get_objects(
        ids: str = None,
        start_time: datetime.datetime = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=10),
        end_time: datetime.datetime = datetime.datetime.now(datetime.timezone.utc),
        # min_num_objects: float = 0,
        top_n_objects: int = 10,
        limit: int = 200
    ) -> list[ObjectCountsArrays]:

    statement = select(ObjectCountsArrays)

    ids_list = []
    if ids:
        ids_list = ids.split(',')
        statement = statement.where(ObjectCountsArrays.video_id.in_(ids_list))

    statement = statement.where(ObjectCountsArrays.object_rank <= top_n_objects)

    statement = statement.limit(limit)

    with Session(engine) as session:
        rankings = session.exec(statement).all()

    new_rankings = []
    for ranking in rankings:
        assert isinstance(ranking, ObjectCountsArrays)
        new_times, new_counts = [], []
        for i, ts in enumerate(ranking.video_times):
            ts_utc = ts.astimezone(datetime.timezone.utc)
            if ts_utc >= start_time and ts_utc <= end_time:
                new_times.append(ts)
                new_counts.append(ranking.avg_num_objects[i])
        ranking.video_times = new_times
        ranking.avg_num_objects = new_counts
        new_rankings.append(ranking)

    return new_rankings


@app.get("/video_stream/overall_object_rankings")
def get_overall_object_count_ranks(
        start_time: datetime.datetime | None = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3),
        limit: int = 50
    ) -> list[OverallObjectRanking]:

    with Session(engine) as session:
        statement = select(OverallObjectRanking).limit(limit)

        rankings = session.exec(statement).all()
    return rankings


@app.get("/video_stream/object_rankings")
def get_objects(
        ids: str = None,
        start_time: datetime.datetime = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3),
        end_time: datetime.datetime = datetime.datetime.now(datetime.timezone.utc),
        # min_num_objects: float = 0,
        top_n_objects: int = 3,
        limit: int = 200
    ) -> list[ObjectRankingArrays]:

    statement = select(ObjectRankingArrays)

    ids_list = []
    if ids:
        ids_list = ids.split(',')
        statement = statement.where(ObjectRankingArrays.video_id.in_(ids_list))

    # statement = statement.where(ObjectRankingArrays.object_rank <= top_n_objects)

    statement = statement.limit(limit)

    with Session(engine) as session:
        rankings = session.exec(statement).all()

    for ranking in rankings:
        assert isinstance(ranking, ObjectRankingArrays)
        ranking.object_names = ranking.object_names[:top_n_objects]

    return rankings
# ObjectRankingArrays

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="localhost", port=8000, reload=True, workers=4) 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    
handler = Mangum(app, lifespan="off")
