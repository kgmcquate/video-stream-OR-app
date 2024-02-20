WITH
filtered as (
    select 
        --DATE_TRUNC('hour', start) as video_time,
        source_name,
        video_id,
        date_trunc('day', start) + floor(extract(hour from start) / 6.0) * 6 * interval '1 hour' as video_time,
        avg_num_objects,
        object_name 
    from {{ source('video_stream', 'video_stream_objects_stats') }}
    where detector_name <> 'haar_classifier'
        and start >= (current_timestamp - interval '14 days')
)
,
agg as (
    SELECT 
        source_name, video_id, object_name, video_time,
        avg(avg_num_objects) as avg_num_objects
    from filtered
    group by source_name, video_id, object_name, video_time
)
select * from agg
