.PHONY: start test venv

venv:
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1

start: venv
	.\.venv\Scripts\Activate.ps1 && python run.py

test: venv
	.\.venv\Scripts\Activate.ps1 && pytest -v tests/
