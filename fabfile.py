import os

from fabric import Connection, task

home = os.path.expanduser('~')
dags_path = os.path.join(home, 'airflow', 'dags')
repo_path = os.path.join(home, 'repositories', 'dataeng_dags')
env_path = os.path.join(home, 'venvs', '.airflow', 'bin', 'activate')

@task
def deploy(context):
    with Connection('85.209.9.101') as conn:
        with conn.cd(repo_path):
            conn.run('git pull')

                