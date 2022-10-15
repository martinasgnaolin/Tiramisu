FROM python:3.8

WORKDIR /home/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY telegram_apikey.py .

EXPOSE 5000
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload" ]