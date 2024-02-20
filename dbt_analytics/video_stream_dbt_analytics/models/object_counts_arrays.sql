WITH
arrays as (
    select
        source_name,
        video_id,
        object_name,
        ARRAY_AGG(video_time order by video_time asc) as video_times,
        ARRAY_AGG(avg_num_objects order by video_time asc) as avg_num_objects
    from {{ ref('prefiltered_object_counts') }}
    group by source_name, video_id, object_name
)
,
top_n_ranks as (
	select source_name, video_id, object_name, object_rank, avg_num_objects
	from {{ ref('object_ranking') }}
	where object_rank <= 100
)
,
joined as (
    select 
        arrays.source_name,
    	arrays.video_id,
        arrays.object_name,
        top_n_ranks.object_rank,
        arrays.video_times,
        arrays.avg_num_objects
    from arrays	
    inner join top_n_ranks
    on arrays.object_name = top_n_ranks.object_name
        and arrays.source_name = top_n_ranks.source_name
    	and arrays.video_id = top_n_ranks.video_id
    order by arrays.video_id, top_n_ranks.object_rank asc
)
select * from joined