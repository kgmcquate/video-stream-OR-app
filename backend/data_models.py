from sqlmodel import SQLModel, Field
from typing import Optional
import datetime
import json

from sqlmodel import Session, select
from pydantic.dataclasses import dataclass
import dataclasses

from sqlalchemy import Column, DateTime, Float, String
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


class VideoStream(SQLModel, table=True):
    __tablename__ = "video_streams"

    source_name: str = Field(default=None, primary_key=True)
    video_id: str = Field(default=None, primary_key=True)
    is_active: bool
    insert_ts: Optional[datetime.datetime] = Field(default=datetime.datetime.now(datetime.timezone.utc))
    last_update_ts: Optional[datetime.datetime] = Field(default=datetime.datetime.now(datetime.timezone.utc))

@dataclass
class VideoRankings:
    __tablename__ = "video_rankings"

    source_name: str
    video_id: str 
    is_active: bool
    insert_ts: Optional[datetime.datetime] 
    last_update_ts: Optional[datetime.datetime]
    avg_num_objects: Optional[float | int]

@dataclass
class VideoStreamsResponse:
    video_streams: list[VideoRankings]


class VideoStreamInfo(SQLModel, table=True):
    __tablename__ = "video_streams_info"

    source_name: str = Field(default=None, primary_key=True)
    video_id: str = Field(default=None, primary_key=True)
    title: str
    description: str
    account_name: str
    publish_ts: datetime.datetime
    tags: str = Field(default=None, sa_column=Column(JSONB))
    live_broadcast: Optional[str]
    definition: Optional[str]
    caption: Optional[str]
    licensed_content: Optional[bool]
    projection: Optional[str]
    thumbnail_url: Optional[str]
    highres_thumbnail_url: Optional[str]
    view_count: Optional[int]
    like_count: Optional[int]
    favorite_count: Optional[int]
    comment_count: Optional[int]
    insert_ts: Optional[datetime.datetime] = Field(default=datetime.datetime.now(datetime.timezone.utc))
    last_update_ts: Optional[datetime.datetime] = Field(default=datetime.datetime.now(datetime.timezone.utc))

    @staticmethod
    def from_youtube_api_response(api_response_json: dict) -> "VideoStreamInfo":
        assert len(api_response_json['items']) == 1

        video = api_response_json['items'][0]

        snip = video['snippet']
        content = video['contentDetails']
        stats = video['contentDetails']

        def cast_to_int(string):
            if string is None:
                return None
            try:
                return int(string)
            except Exception as e:
                return None

        return VideoStreamInfo(
            source_name="youtube",
            video_id=video['id'],
            title=snip['title'],
            description=snip['description'],
            account_name=snip['channelTitle'],
            publish_ts=datetime.datetime.fromisoformat(snip.get('publishedAt')) if snip.get('publishedAt') is not None else None,
            tags=json.dumps(snip.get('tags')),
            live_broadcast=snip.get('liveBroadcastContent'),
            caption=content.get('caption'),
            definition=content.get('definition'),
            licensed_content=content.get('licensedContent'),
            projection=content.get('projection'),
            thumbnail_url=snip.get('thumbnails', {}).get('default', {}).get('url'),
            highres_thumbnail_url=snip.get('thumbnails', {}).get('high', {}).get('url'),
            view_count=cast_to_int(stats.get('viewCount')),
            like_count=cast_to_int(stats.get('likeCount')),
            favorite_count=cast_to_int(stats.get('favoriteCount')),
            comment_count=cast_to_int(stats.get('commentCount'))
        )

# @dataclasses.dataclass
# class VideoInfosResponse:
#     video_infos: list[VideoStreamInfo]
    

class VideoStreamObjectsStats(SQLModel, table=True):
    __tablename__ = "video_stream_objects_stats"

    start: datetime.datetime = Field(primary_key=True)
    end: datetime.datetime = Field(primary_key=True)
    source_name: str = Field(primary_key=True)
    video_id: str = Field(primary_key=True)
    detector_name: str = Field(primary_key=True)
    detector_version: str = Field(primary_key=True)
    object_name: str = Field(primary_key=True)
    avg_num_objects: float = Field(nullable=True)
    min_num_objects: int = Field(nullable=True)
    max_num_objects: int = Field(nullable=True)
    stddev_num_objects: float = Field(nullable=True)
    record_count: int
    spark_epoch_id: int


class ObjectRanking(SQLModel, table=True):
    __tablename__ = "object_ranking"

    source_name: str = Field(primary_key=True)
    video_id: str = Field(primary_key=True)
    object_name: str = Field(primary_key=True)
    object_rank: int
    avg_num_objects: float


class ObjectRankingArrays(SQLModel, table=True):
    __tablename__ = "object_ranking_arrays"

    source_name: str = Field(primary_key=True)
    video_id: str = Field(primary_key=True)
    object_names: list[str] = Field(default=None, sa_column=Column(ARRAY(String)))


class OverallObjectRanking(SQLModel, table=True):
    __tablename__ = "overall_object_ranking"

    object_name: str = Field(primary_key=True)
    object_rank: int
    avg_num_objects: float


class ObjectCountsArrays(SQLModel, table=True):
    __tablename__ = "object_counts_arrays"

    source_name: str = Field(primary_key=True)
    video_id: str = Field(primary_key=True)
    object_name: str = Field(primary_key=True)
    object_rank: int
    video_times: list[datetime.datetime] = Field(default=None, sa_column=Column(ARRAY(DateTime)))
    avg_num_objects: list[float] = Field(default=None, sa_column=Column(ARRAY(Float)))


