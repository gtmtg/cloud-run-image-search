screen -S server -dm pipenv run authbind uvicorn --host 0.0.0.0 --port 80 --workers 1 server:app
