PYTHON   := python3
VENV_DIR := .venv
ACTIVATE := source $(VENV_DIR)/bin/activate
FILE     ?= add

.PHONY: venv install lint run clean

venv:
	$(PYTHON) -m venv $(VENV_DIR)

install: venv
	@$(ACTIVATE) && pip install --upgrade pip
	@$(ACTIVATE) && [ -f requirements.txt ] && pip install -r requirements.txt || true

lint: install
	@$(ACTIVATE) && flake8 src

run: install
	@$(ACTIVATE) && \
	$(PYTHON) - << 'EOF'
import sys
from src.csemachine import get_result
get_result("$(FILE)")
EOF

clean:
	find . -name "*.pyc"   -delete
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +

