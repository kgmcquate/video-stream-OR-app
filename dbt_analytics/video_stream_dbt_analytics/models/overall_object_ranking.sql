WITH 
agg as (
    select 
        object_name,
        avg(avg_num_objects) AS avg_num_objects
    from {{ ref('prefiltered_object_counts') }}
    group by object_name
)
,
ranked as (
    select
        object_name,
        row_number() OVER(order by avg_num_objects DESC) as object_rank,
        avg_num_objects
    from agg 
    order by object_rank asc
)
SELECT * FROM ranked 