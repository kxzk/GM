.PHONY: setup test test-all lint run help

setup:
## make setup: install requirements
	pip3 install -r requirements.txt

test:
## make test: make test token=xxx (skip slow tests)
	pytest -v --no-header --no-summary -m "not slow" -rs --token $(token) test_gm.py

test-all:
## make test-all: make test-all token=xxx (run slow tests)
	pytest -v --no-header --no-summary -rs --token $(token) test_gm.py

lint:
## make lint: run black and ruff on all python files
	black .
	ruff .

run:
## make run: make run username=xxx token=xxx org=xxx
	python3 gm.py -u $(username) -t $(token) -o $(org)

help:
	@echo "Usage: \n"
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^/-/'
