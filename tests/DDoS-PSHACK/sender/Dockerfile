FROM python:3.13-slim

RUN apt-get update && apt-get install -y tcpdump && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir requests scapy

COPY pktSender.py .

CMD ["python", "pktSender.py"]