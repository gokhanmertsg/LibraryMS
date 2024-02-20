FROM python:3.10

#WORKDIR /code

#COPY . /code

#COPY pyproject.toml .
#COPY poetry.lock .

#RUN pip install poetry
#RUN poetry install

ENV POSTGRES_HOST=db
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=test1234
ENV POSTGRES_DB=libraryms_db

#CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
 