FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY . .

FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --from=builder /app /app
ENV PYTHONPATH=/app
USER nonroot:nonroot
ENTRYPOINT ["/usr/bin/python3", "cmd/detector/main.py"]
