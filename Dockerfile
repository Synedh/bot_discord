FROM python:3.5

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP routes.py
ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0"]

# CMD [ "python", "./routes.py" ]
