rm -rf venv
virtualenv -p python3.5 venv
venv/bin/pip install -U pip==9.0.1
venv/bin/pip install -U setuptools==38.2.3
venv/bin/pip install -r requirements.txt
