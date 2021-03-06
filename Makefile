SHELL := /usr/bin/env bash

APP_NAME := scalesec-gcp-workload-identity

VERSION ?= 1.0.0

.PHONY: dev setup test clean dist

setup:
	python3 -m venv .venv

dev: 
	source .venv/bin/activate && pip install -r dev_requirements.txt

test: 
	@source .env && PYTHONPATH=$(shell pwd) pytest --log-cli-level=10

clean:
	rm -rf dist/*
	rm -rf build/*

dist: clean test
	source .venv/bin/activate && PKGVERSION=$(VERSION) python -m build
	source .venv/bin/activate && python -m twine upload dist/*