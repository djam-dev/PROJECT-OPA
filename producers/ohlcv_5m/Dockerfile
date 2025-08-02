FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY producer_trade_ohlcv.py .

CMD ["python", "producer_trade_ohlcv.py"]