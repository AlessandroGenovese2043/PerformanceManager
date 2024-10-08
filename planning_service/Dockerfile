FROM python:3

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY utils .
COPY planning/planning_main.py .

CMD [ "python", "planning_main.py" ]