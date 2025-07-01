run-pure:
	uvicorn pure:app --host 0.0.0.0 --port 8000 --app-dir naive

run-lang:
	uvicorn lang:app --host 0.0.0.0 --port 8000 --app-dir naive

run-pure-celery:
	uvicorn pure:app --host 0.0.0.0 --port 8000 --app-dir queue

run-lang-celery:
	uvicorn lang:app --host 0.0.0.0 --port 8000 --app-dir queue

loadtest:
	locust -f locust/locustfile.py --host=http://localhost:8000

loadtest-celery:
	locust -f locust/locustfile_celery.py --host=http://localhost:8000

run-redis:
	docker run --name redis -d -p 6379:6379 redis:6-alpine

run-celery-pure:
	cd queue && celery -A tasks_pure worker --loglevel=info

run-celery-lang:
	cd queue && celery -A tasks_lang worker --loglevel=info
