WITH
top_n_ranks as (
	select source_name, 
        video_id, 
        object_name, 
        object_rank, 
        avg_num_objects
	from {{ ref('object_ranking') }}
	where object_rank <= 100
)
,
agg as (
    SELECT 
        source_name,
        video_id,
        ARRAY_AGG(object_name order by object_rank asc) as object_names
    from top_n_ranks
    group by source_name, video_id
)
select * from agg