from typing import List
from typing import Optional
from sqlalchemy import MetaData, ForeignKey, func
from sqlalchemy import  Column, String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
import datetime

from . import database

class VideoStreams(database.Base):
    __tablename__ = database.video_streams_table

    source_name: Mapped[str] = Column(String(30), primary_key=True)
    video_id: Mapped[str] = Column(String, primary_key=True)
    is_active: Mapped[bool] = Column(Boolean, server_default="true")
    insert_ts: Mapped[datetime.datetime] = Column(DateTime(timezone=True), server_default=func.now())
    last_update_ts: Mapped[datetime.datetime] = Column(DateTime(timezone=True), server_default=func.now())


    # addresses: Mapped[List["Address"]] = relationship(
    #     back_populates="user", cascade="all, delete-orphan"
    # )

