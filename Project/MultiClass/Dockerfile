FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY multiClass_api.py .
COPY model_multi.pkl .

EXPOSE 5002

CMD ["python", "multiClass_api.py"]