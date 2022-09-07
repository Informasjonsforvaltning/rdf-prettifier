FROM python:3.10 as requirements

WORKDIR /tmp

RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.10

WORKDIR /app

COPY --from=requirements /tmp/requirements.txt ./

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./rdf-diff-store /app

WORKDIR /

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
