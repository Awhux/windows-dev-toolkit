.PHONY: run build clean install-dev scaffold venv check-venv

run:
	python3 main.py

build:
	python3 build_script.py

clean:
	rm -rf build dist *.spec venv

install:
	pip install -r requirements.txt

scaffold:
	python3 main.py scaffold $(name)

check-venv:
	@which python3-venv > /dev/null 2>&1 || (echo "python3-venv is not installed. Please run: sudo apt install python3-venv" && exit 1)

venv:
	python3 -m venv venv
	. ./venv/bin/activate && pip install --upgrade pip
	. ./venv/bin/activate && pip install -r requirements.txt
	. ./venv/bin/activate && pip install -e .

run-venv:
	. ./venv/bin/activate && python3 main.py