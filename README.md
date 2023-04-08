# NK TOLMIN - backend

!!! The latest version of this repository is now hosted on a private GitLab server. As a reference to my work, I have cloned the repository to my personal GitHub profile.

## start database:
`docker-compose up -d`

## create and install virtual environment:
`copy .env file`<br/>
`python3 -m venv venv`<br/>
`. venv/bin/activate`<br/>
`python3 -m pip install -r requirements.txt`

## create database
`python3 schema.py`

## run project
`python3 app.py`<br/>
## in new console tab run worker 
`rq worker` <br/>

if you get an error `rq: command not found` run <br/>
`pip uninstall virtualenv` <br/>
`sudo pip install virtualenv` <br/>
