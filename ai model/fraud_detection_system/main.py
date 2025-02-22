from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
from typing import List, Optional
import uvicorn
import numpy as np
from sklearn.ensemble import RandomForestClassifier

app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection system for financial transactions",
    version="1.0.0"
)

# Simple model for demonstration
model = RandomForestClassifier(n_estimators=100, random_state=42)

class Transaction(BaseModel):
    user_id: str
    merchant_id: str
    merchant_category: str
    amount: float
    latitude: float
    longitude: float
    timestamp: datetime

class TransactionResponse(BaseModel):
    transaction_id: str
    is_fraudulent: bool
    fraud_probability: float
    risk_factors: List[dict]

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Fraud Detection API",
        "endpoints": {
            "predict": "/predict - POST endpoint for fraud detection",
            "health": "/health - GET endpoint for health check",
            "docs": "/docs - API documentation"
        }
    }

@app.post("/predict", response_model=TransactionResponse)
async def predict_fraud(transaction: Transaction):
    try:
        # Convert transaction to feature vector (simplified for demonstration)
        features = np.array([[
            transaction.amount,
            float(hash(transaction.user_id) % 1000),  # Simple user ID encoding
            float(hash(transaction.merchant_id) % 1000),  # Simple merchant ID encoding
            float(hash(transaction.merchant_category) % 100),  # Simple category encoding
            transaction.latitude,
            transaction.longitude
        ]])
        
        # Generate random prediction for demonstration
        is_fraud = bool(np.random.random() < 0.1)  # 10% chance of fraud
        fraud_prob = np.random.random()
        
        # Generate risk factors
        risk_factors = [
            {"feature": "amount", "importance": np.random.random()},
            {"feature": "location", "importance": np.random.random()},
            {"feature": "merchant_category", "importance": np.random.random()}
        ]
        
        return TransactionResponse(
            transaction_id=str(transaction.timestamp.timestamp()),
            is_fraudulent=is_fraud,
            fraud_probability=float(fraud_prob),
            risk_factors=risk_factors
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    print("Starting Fraud Detection API...")
    print("Access the API at: http://127.0.0.1:8002")
    print("API documentation at: http://127.0.0.1:8002/docs")
    uvicorn.run(app, host="127.0.0.1", port=8002)
