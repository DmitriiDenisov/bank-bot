docker pull dmitrydenisov/worker_base
docker run --entrypoint python3 -d --net="host" --name $1 worker_base -u rabbitmq_utils/worker_transactions.py
