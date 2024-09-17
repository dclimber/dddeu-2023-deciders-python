.PHONY: setup test coverage html-report

setup:
	python3 -m venv .venv
	.venv/bin/pip install coverage

test:
	PYTHONPATH=src/ .venv/bin/python -m unittest discover tests

coverage:
	PYTHONPATH=src/ .venv/bin/coverage run -m unittest discover tests \
	&& .venv/bin/coverage report --include "src/*.py"

html-report:
	PYTHONPATH=src/ .venv/bin/coverage html \
	&& .venv/bin/python -m webbrowser -t htmlcov/index.html
