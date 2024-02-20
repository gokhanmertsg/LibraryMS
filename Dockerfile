FROM python:3.10

WORKDIR /app

COPY . /app

COPY pyproject.toml .
COPY poetry.lock .

RUN pip install poetry
RUN poetry install

COPY . .

EXPOSE 5432

ENV POSTGRES_HOST=db
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=test1234
ENV POSTGRES_DB=libraryms_db

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5432"]
