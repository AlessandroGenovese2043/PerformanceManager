FROM python:3

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY utils .
COPY client/client_main.py .

CMD [ "python", "client_main.py" ]