FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    iproute2 \
    iptables \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY victim.py .

CMD ["python", "victim.py"]