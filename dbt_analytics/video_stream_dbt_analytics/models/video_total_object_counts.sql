select 
	source_name, video_id,
	avg(avg_num_objects) as avg_num_objects
from {{ ref('prefiltered_object_counts') }}
group by source_name, video_id

