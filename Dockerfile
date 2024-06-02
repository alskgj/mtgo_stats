FROM python:3.12-slim

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD . .

CMD ["python", "./cli.py", "fetch"]
