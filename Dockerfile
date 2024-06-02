FROM python:3.12-alpine

WORKDIR /code/app

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/app

CMD ["uvicorn", "rest:app", "--host", "0.0.0.0", "--port", "80"]
