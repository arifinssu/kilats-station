.PHONY: install run clean
VENV = env
PYTHON = python3
PIP = $(VENV)/bin/pip3

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -r requirements.txt

run:
	source $(VENV)/bin/activate
	$(PYTHON) main.py

clean:
	rm -rf __pycache__
	rm -rf $(VENV)