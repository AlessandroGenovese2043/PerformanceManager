FROM python:3.10

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH=/app
WORKDIR /app

CMD [ "python", "analysis/analysis_main.py" ]