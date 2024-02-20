from airflow.decorators import dag, task
from datetime import datetime, timedelta

@dag(schedule="@continuous",
      max_active_runs=1, 
      start_date=datetime(2024, 1, 1, 12, 00), 
      catchup=False,
    #   retry_delay=timedelta(minutes=2)
)
def video_stream_producer_dag():

    @task(retries=5, retry_delay=timedelta(minutes=2)) 
    def run():
        import importlib
        # importlib.import_module("opencv-python")

        from video_stream_producer.main import main
        
        main()

    run()

video_stream_producer_dag()