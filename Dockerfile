FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./ /code/

CMD ["gunicorn", "-b", "0.0.0.0:8000", "main:app", "-k", "uvicorn.workers.UvicornWorker"]