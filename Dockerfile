FROM python:3.8

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY .env ./
COPY log_config.json ./
COPY db.sqlite ./
COPY main.py ./
COPY src/ ./src/
CMD python main.py
