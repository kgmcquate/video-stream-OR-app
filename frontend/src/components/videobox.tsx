// import { useState, useMemo, useEffect } from 'react';
import { Button } from "./button"
import { PlusIcon } from "./icons"
import { Badge } from "./badge"
import { VideoId, VideoInfo, VideoObjectRanking } from "../models"
import { VideoStatsBox } from "./videoStatsBox"

// import { API_BASE_URL } from "../App"
import { getPrettyTime } from "./utils"

import dayjs from "dayjs"

export function VideoBox({
    // key,
    videoId,
    videoInfo,
    videoObjectRanking
  }: {
    // key: string, 
    videoId: VideoId, 
    videoInfo: VideoInfo | null,
    videoObjectRanking: VideoObjectRanking | null
  }) {

    // const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null)
    // const [videoObjectRanking, setVideoObjectRanking] = useState<VideoObjectRanking | null>(null)

    const currentTime = dayjs()
    const runTime = currentTime.diff(videoInfo?.publish_ts, 'seconds')

    var tags: string[] = []
    if (videoInfo?.tags !== null && videoInfo?.tags !== undefined) {
      tags = (JSON.parse(videoInfo.tags) as string[]) ?? []
    }

    // console.log(videoObjectRanking)

    var objects: string[] = []
    if(videoObjectRanking !== undefined && videoObjectRanking?.object_names !== undefined) {
      objects = videoObjectRanking?.object_names
    }
  
    return (
    <div className="relative">
      <div >
      <VideoStatsBox videoId={videoId} className="absolute "></VideoStatsBox>
        <a href={`https://www.youtube.com/watch?v=${videoInfo?.video_id}`} target="_blank">
          <img
            alt={videoInfo?.title}
            className="rounded-lg object-cover"
            height="150"
            src={videoInfo?.highres_thumbnail_url ? videoInfo?.highres_thumbnail_url : ""}
            style={{
              aspectRatio: "300/150",
              objectFit: "cover",
            }}
            width="300"
          />
        </a>
        
      </div>
      <h3 className="font-semibold mt-2">{videoInfo?.title}</h3>
      <div className=" ">
        
        <p className="text-sm text-gray-500">Started {getPrettyTime(runTime)}</p>
        
        <div className="flex flex-wrap gap-1 mt-2">
          <p className="text-sm text-gray-500 ">Objects:</p>
          {objects.map((object) => <Badge key={object}>{object}</Badge>)}
        </div>
      </div>
    </div>
    )
  }
