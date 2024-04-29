FROM python:3.12-slim

ADD requirements.txt .

RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org -r requirements.txt

ADD . .

CMD ["python", "./cli.py", "fetch"]
