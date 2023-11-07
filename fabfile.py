import os

from fabric import Connection, task

repo_path = os.path.join('/root/airflow_gitub_actions')

@task
def deploy(context):
    with Connection('85.209.9.101') as conn:
        with conn.cd(repo_path):
            conn.run('git pull')

                