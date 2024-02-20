from datetime import datetime 

from cosmos import DbtDag, ExecutionMode, ExecutionConfig, ProjectConfig, ProfileConfig 
from cosmos.profiles import PostgresUserPasswordProfileMapping 

profile_config = ProfileConfig( 
    profile_name="default", 
    target_name="dev", 
    profile_mapping=PostgresUserPasswordProfileMapping( 
        conn_id="postgres", 
        profile_args={"schema": "public"}, 
    ), 
)


basic_cosmos_dag = DbtDag( 
    # dbt/cosmos-specific parameters 
    project_config=ProjectConfig( 
        dbt_project_path="/opt/airflow/dags/video_stream_dbt_analytics",
        project_name="video_stream_dbt_analytics"
    ), 
    profile_config=profile_config, 
    # execution_config=ExecutionConfig(
    #     execution_mode=ExecutionMode.DOCKER,
    #     # dbt_executable_path="/home/airflow/.local/bin/dbt"
    # ),
    # operator_args={
    #     "image": "ghcr.io/dbt-labs/dbt-postgres:1.5.8",
    #     # "network_mode": "bridge",
    # },
    # operator_args={ 
    #     "install_deps": True,
    #     "py_system_site_packages": False,
    #     "py_requirements": [
    #         "dbt-postgres==1.7.8",
    #         "dbt-core==1.7.8",
    #         "click"
    #     ],
    #     # "full_refresh": True,  # used only in dbt commands that support this flag 
    # }, 
    # normal dag parameters 
    schedule_interval="*/15 * * * *",
    max_active_runs=1,
    start_date=datetime(2024, 1, 1),
    catchup=False, 
    dag_id="video_stream_dbt_analytics", 
    default_args={"retries": 2}, 
)

