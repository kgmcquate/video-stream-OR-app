from airflow.decorators import dag, task
from airflow.exceptions import AirflowSkipException
from airflow.models.baseoperator import chain
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule


 from airflow import DAG
 from airflow.operators.empty import EmptyOperator


@dag(schedule=None, catchup=False)
def video_stream_producer_dag():

    @task.virtualenv(
        task_id="run_video_stream_producer", 
        requirements=[
            "pydantic",
            "urllib3",
            "boto3",
            "vidgear",
            "fastavro",
            "numpy",
            "opencv-python",
            "yt_dlp",
            "pulsar-client[avro]",
            "sqlalchemy",
            "psycopg2-binary",
        ], 
        system_site_packages=False
    )
    def callable_virtualenv():
        """
        Example function that will be performed in a virtual environment.

        Importing at the module level ensures that it will not attempt to import the
        library before it is installed.
        """
        from time import sleep

        from colorama import Back, Fore, Style

        print(Fore.RED + "some red text")
        print(Back.GREEN + "and with a green background")
        print(Style.DIM + "and in dim text")
        print(Style.RESET_ALL)
        for _ in range(4):
            print(Style.DIM + "Please wait...", flush=True)
            sleep(1)
        print("Finished")

        from .video_stream_producer.main import main
        
        main()


    virtualenv_task = callable_virtualenv()