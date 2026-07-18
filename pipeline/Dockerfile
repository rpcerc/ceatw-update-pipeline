# Python 3.12.13 (slim)
FROM python@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de
WORKDIR /app

COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

CMD [ "python", "-m", "ceatw_update_pipeline.main" ]