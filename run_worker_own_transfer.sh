docker pull dmitrydenisov/worker_base
docker run -v $(pwd)/credentials:/app/credentials --entrypoint python3 -d --net="host" --name $1 dmitrydenisov/worker_base -u rabbitmq_utils/worker_own_transfer.py
