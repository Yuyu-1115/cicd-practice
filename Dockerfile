FROM python:3.12

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src .
RUN chmod 775 src/user_data.sqlite

ENV FLASK_APP=app.py

EXPOSE 8080

RUN useradd app
USER app

CMD ["flask", "run", "--host=0.0.0.0", "--port", "8080"]