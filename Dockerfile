FROM python:3.10 as requirements

WORKDIR /tmp

RUN pip install poetry==1.5.1
COPY ./pyproject.toml ./poetry.lock* ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.10

WORKDIR /tmp

COPY --from=requirements /tmp/requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./rdf_prettifier /rdf_prettifier
COPY ./log_conf.yaml /rdf_prettifier

WORKDIR /

EXPOSE 80
CMD ["uvicorn", "rdf_prettifier.main:app", "--host", "0.0.0.0", "--port", "80", "--log-config", "log_conf.conf"]
