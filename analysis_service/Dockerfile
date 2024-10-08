FROM python:3

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY utils .
COPY analysis/analysis_main.py.py .

CMD [ "python", "analysis_main.py" ]