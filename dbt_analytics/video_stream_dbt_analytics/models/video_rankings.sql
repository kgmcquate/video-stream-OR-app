{{
    config(
        materialization='view'
    )
}}

select
	vs.source_name,
	vs.video_id,
	vs.is_active,
    vs.insert_ts,
    vs.last_update_ts,
	t.avg_num_objects
from {{ source('video_stream', 'video_streams') }} vs 
left join {{ ref('video_total_object_counts') }} t
on vs.source_name = t.source_name
	and vs.video_id = t.video_id
order by avg_num_objects desc NULLS LAST
