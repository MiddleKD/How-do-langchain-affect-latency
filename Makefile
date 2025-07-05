run-pure:
	uvicorn pure:app --host 0.0.0.0 --port 8000 --app-dir naive

run-lang:
	uvicorn lang:app --host 0.0.0.0 --port 8000 --app-dir naive

run-pure-queue:
	uvicorn pure:app --host 0.0.0.0 --port 8000 --app-dir queue

run-lang-queue:
	uvicorn lang:app --host 0.0.0.0 --port 8000 --app-dir queue

run-redis:
	docker run --name redis -d -p 6379:6379 redis:6-alpine

run-celery-pure:
	cd queue && celery -A tasks_pure worker --loglevel=info

run-celery-lang:
	cd queue && celery -A tasks_lang worker --loglevel=info

loadtest:
	locust -f locust/locustfile.py --host=http://localhost:8000 -u 300 -r 10 -t 3m

loadtest-celery:
	locust -f locust/locustfile_celery.py --host=http://localhost:8000 -u 300 -r 10 -t 3m

run-ollama:
	docker run --rm --gpus=all -v /home/middlek/Desktop/mnt/sda/models/ollama:/root/.ollama -v ./modelfiles:/root/modelfiles -p 11434:11434 -e OLLAMA_KV_CACHE_TYPE=1 -e OLLAMA_NUM_PARALLEL=16 --name ollama ollama/ollama
