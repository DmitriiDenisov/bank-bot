build: ## Build the container
	docker build -t worker_base -f Dockerfile_base_worker .
run: ## Run main API (frontend)
	python3 api_queries.py