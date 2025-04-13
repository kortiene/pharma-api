ifneq (,$(wildcard ./.env))
    include .env
    export
endif

.DEFAULT_GOAL := help

.PHONY: help
help:	## Show this help
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build:  ## Build Docker images
	docker build -t $(CONTAINER_REPO):main .

.PHONY: push
push:	## Push the image
	echo "Pushing the image"

.PHONY: pull
pull:	## Pull the latest images
	echo "Pulling the latest images"

.PHONY: apply
run:	## Run all services
	echo "Running the services"

.PHONY: logs
logs:	## View logs from one/all containers
	docker compose logs -f $(s)

.PHONY: tests
tests:	## Run tests
	echo "Running tests"