FROM python:3

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY utils .
COPY monitor/monitor_main.py .

CMD [ "python", "monitor_main.py" ]