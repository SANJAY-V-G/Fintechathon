from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
from typing import List, Optional
import uvicorn

from src.models.fraud_detector import FraudDetector
from src.data_preprocessing.preprocessor import TransactionPreprocessor

app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection system for financial transactions",
    version="1.0.0"
)

# Initialize models
fraud_detector = FraudDetector()
preprocessor = TransactionPreprocessor()

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
    
@app.post("/predict", response_model=TransactionResponse)
async def predict_fraud(transaction: Transaction):
    try:
        # Convert transaction to DataFrame
        transaction_df = pd.DataFrame([transaction.dict()])
        
        # Preprocess transaction data
        processed_data = preprocessor.prepare_features(transaction_df)
        
        # Make prediction
        is_fraud = fraud_detector.predict(processed_data)[0]
        fraud_prob = fraud_detector.predict_proba(processed_data)[0][1]
        
        # Get feature importance for explanation
        explanation = fraud_detector.explain_prediction(processed_data)
        risk_factors = [
            {"feature": feat, "importance": imp}
            for feat, imp in explanation.as_list()
        ]
        
        return TransactionResponse(
            transaction_id=str(transaction.timestamp.timestamp()),
            is_fraudulent=bool(is_fraud),
            fraud_probability=float(fraud_prob),
            risk_factors=risk_factors
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
