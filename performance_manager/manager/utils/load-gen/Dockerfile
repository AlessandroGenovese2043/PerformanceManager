FROM python:3.11-slim as base

FROM base as builder

COPY requirements.txt .

RUN pip install --prefix="/install" -r requirements.txt

FROM base

WORKDIR /loadgen

COPY --from=builder /install /usr/local

COPY locustfile.py .
COPY input_conf.txt .
# enable gevent support in debugger
ENV GEVENT_SUPPORT=True

ENTRYPOINT locust --host="http://${TARGET_ADDR}" -u "${USERS:-10}" 2>&1
