WITH 
agg AS (
    SELECT
        source_name,
        video_id,
        object_name,
        AVG(avg_num_objects) as avg_num_objects
    from {{ ref('prefiltered_object_counts') }}
    group by source_name, video_id, object_name
)
,
ranked as (
    select 
        source_name,
        video_id,
        object_name,
        row_number() OVER(partition by video_id order by avg_num_objects DESC) as object_rank,
        avg_num_objects
    from agg
    order by source_name, video_id, object_rank asc
)
SELECT * FROM ranked