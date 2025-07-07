from fastapi import FastAPI
from pydantic import BaseModel
from predict import predict_price

app = FastAPI()

class TradeInput(BaseModel):
    price: float
    quantity: float

@app.post("/predict")
def get_prediction(trade: TradeInput):
    predicted_price = predict_price(trade.price, trade.quantity)
    return {"predicted_price": predicted_price}
