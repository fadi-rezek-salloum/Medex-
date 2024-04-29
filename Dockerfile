FROM python:3.10-alpine

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt
RUN python3 manage.py makemigrations --noinput
RUN python3 manage.py migrate --noinput
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]