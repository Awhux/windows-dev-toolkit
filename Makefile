.PHONY: clean build test lint run all help

# Python interpreter to use
PYTHON := python
# Output directory for the built executable
DIST_DIR := dist
# Name of the executable
EXE_NAME := WinDevToolkit.exe

help:
	@echo "Windows Developer Utilities Toolkit"
	@echo "Make targets:"
	@echo "  clean       - Remove build artifacts and temporary files"
	@echo "  build       - Build the executable using PyInstaller"
	@echo "  test        - Run test suite"
	@echo "  lint        - Run code linters (black, flake8, mypy)"
	@echo "  run         - Run the toolkit directly using Python"
	@echo "  all         - Run lint, test, and build"
	@echo "  help        - Show this help message"

clean:
	@echo "Cleaning up..."
	rm -rf build/ dist/ __pycache__/ *.spec
	rm -rf .pytest_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "Cleanup complete."

build:
	@echo "Building executable..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install pyinstaller
	$(PYTHON) -m PyInstaller --onefile --clean --add-data "windows_dev_toolkit/resources/*;windows_dev_toolkit/resources/" \
		--name $(EXE_NAME) --icon windows_dev_toolkit/resources/icon.ico \
		--uac-admin --hidden-import win32api --hidden-import win32con \
		--hidden-import winreg --hidden-import psutil \
		windows_dev_toolkit/main.py
	@echo "Build complete. Executable created in $(DIST_DIR)/"

test:
	@echo "Running tests..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"
	$(PYTHON) -m pytest --cov=windows_dev_toolkit tests/ -v
	@echo "Tests complete."

lint:
	@echo "Running linters..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"
	$(PYTHON) -m black windows_dev_toolkit tests
	$(PYTHON) -m flake8 windows_dev_toolkit tests
	$(PYTHON) -m isort windows_dev_toolkit tests
	$(PYTHON) -m mypy windows_dev_toolkit
	@echo "Linting complete."

run:
	@echo "Running toolkit..."
	$(PYTHON) -m windows_dev_toolkit.main

all: lint test build
	@echo "All tasks completed successfully."

# Windows-specific targets
ifeq ($(OS),Windows_NT)
clean-windows:
	@echo "Cleaning up on Windows..."
	if exist build rmdir /s /q build
	if exist dist rmdir /s /q dist
	if exist __pycache__ rmdir /s /q __pycache__
	if exist *.spec del /f /q *.spec
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist .coverage del /f /q .coverage
	if exist htmlcov rmdir /s /q htmlcov
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	for /d /r . %%d in (*.egg-info) do @if exist "%%d" rmdir /s /q "%%d"
	for /r . %%f in (*.pyc *.pyo *.pyd .coverage coverage.xml) do @if exist "%%f" del /f /q "%%f"
	for /d /r . %%d in (.mypy_cache) do @if exist "%%d" rmdir /s /q "%%d"
	@echo "Cleanup complete."
endif