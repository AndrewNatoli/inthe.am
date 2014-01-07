from fabric.api import task, run, local, sudo, cd, env
from fabric.context_managers import settings

env.hosts = [
    'acodding@eugene.adamcoddington.net:22424',
]

def virtualenv(command):
    run('source /var/www/envs/twweb/bin/activate && ' + command)

@task
def deploy():
    local('git push origin master')
    with cd('/var/www/twweb'):
        with settings(warn_only=True):
            sudo('mkdir logs')
            sudo('chmod -R 777 logs')
        with settings(warn_only=True):
            sudo('mkdir email')
            sudo('chmod -R 777 email')
        run('git pull')
        virtualenv('pip install -r /var/www/twweb/requirements.txt')
        virtualenv('python manage.py collectstatic --noinput')
        virtualenv('python manage.py migrate')
        sudo('service twweb restart')
