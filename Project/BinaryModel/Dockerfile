FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY binary_api.py .
COPY model_binary.pkl .

EXPOSE 5001

CMD ["python", "binary_api.py"]