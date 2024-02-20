import dayjs, { Dayjs } from 'dayjs'

export type VideoId = {
    video_id: string
    source_name: string
}

// export type VideoInfo = {
//     title: string
//     description: string
//     publish_ts: Dayjs
//     tags: string[]
//     source_name: string
//     video_id: string
//     thumbnail_url: string
// }

export type VideoInfo = {
    source_name: string
    video_id: string
    title: string
    description: string
    account_name: string
    publish_ts: string // Assuming datetime is serialized as string in ISO format
    tags: string // Assuming tags is an array of strings
    live_broadcast: string | null
    definition: string | null
    caption: string | null
    licensed_content: boolean | null
    projection: string | null
    thumbnail_url: string | null
    highres_thumbnail_url: string | null
    view_count: number | null
    like_count: number | null
    favorite_count: number | null
    comment_count: number | null
    insert_ts: string
    last_update_ts: string 
}


export type VideoInfoResponse = {
    video_infos: VideoInfo[]
}


export type VideoObjectRanking = {
    source_name: string
    video_id: string
    object_names: string[]
}

export type VideoData = {
    videoId: VideoId
    videoInfo: VideoInfo | null
    videoObjectRanking:  VideoObjectRanking | null
}

export type ObjectRanking = {
    object_name: string
    avg_num_objects: number
    rank: number
}

export type ObjectFilter = string

export type VideoObjectsStats = {
    source_name: string
    video_id: string
    object_name: string
    min_num_objects: number
    stddev_num_objects: number
    spark_epoch_id: number
    detector_name: string
    start: string
    end: string
    detector_version: string
    avg_num_objects: number
    max_num_objects: number
    record_count: number
}

export type VideoObjectCounts = {
    source_name: string
    video_id: string
    object_name: string
    object_rank: string
    video_times: string[]
    avg_num_objects: number[]
}    
