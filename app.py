"""
Fraud Detection REST API
FastAPI application for fraud detection predictions
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import time
import os
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for model and preprocessing
model = None
label_encoders = {}
feature_names = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup"""
    global model, label_encoders, feature_names
    
    try:
        model_path = os.path.join("Models", "fraud_detection_model.pkl")
        logger.info(f"Loading model from {model_path}")
        model = joblib.load(model_path)
        logger.info("Model loaded successfully")
        
        # Try to get feature names from model if available
        if hasattr(model, 'feature_names_in_'):
            feature_names = list(model.feature_names_in_)
        else:
            # Default feature names based on dataset structure
            feature_names = [
                'Transaction_Amount', 'Account_Balance', 'Previous_Fraudulent_Activity',
                'Daily_Transaction_Count', 'Avg_Transaction_Amount_7d',
                'Failed_Transaction_Count_7d', 'Card_Age', 'Transaction_Distance',
                'Risk_Score', 'Is_Weekend', 'Transaction_Type', 'Device_Type',
                'Location', 'Merchant_Category', 'IP_Address_Flag', 'Card_Type',
                'Authentication_Method'
            ]
        
        logger.info(f"Feature names: {feature_names}")
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Fraud Detection API",
    description="REST API for fraud detection using machine learning",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {str(e)}")


# Request/Response Models
class TransactionRequest(BaseModel):
    """Transaction data for fraud prediction - only essential features"""
    transaction_amount: float = Field(..., gt=0, description="Transaction amount")
    avg_transaction_amount_7d: float = Field(..., ge=0, description="Average transaction amount in last 7 days")
    failed_transaction_count_7d: float = Field(..., ge=0, description="Failed transaction count in last 7 days")
    daily_transaction_count: int = Field(..., gt=0, description="Daily transaction count (must be > 0)")
    risk_score: float = Field(..., ge=0, le=1, description="Risk score (0-1)")
    card_age: int = Field(..., ge=0, description="Card age in days")
    hour: Optional[int] = Field(None, ge=0, le=23, description="Hour of day (0-23), defaults to current hour")
    month: Optional[int] = Field(None, ge=1, le=12, description="Month (1-12), defaults to current month")
    
    # Optional derived features (can be sent from frontend or calculated on backend)
    high_failure_flag: Optional[int] = Field(None, description="High failure flag (auto-calculated)")
    failure_rate: Optional[float] = Field(None, description="Failure rate (auto-calculated)")
    amount_deviation: Optional[float] = Field(None, description="Amount deviation (auto-calculated)")
    risk_amount_interaction: Optional[float] = Field(None, description="Risk-amount interaction (auto-calculated)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_amount": 150.50,
                "avg_transaction_amount_7d": 120.30,
                "failed_transaction_count_7d": 0.0,
                "daily_transaction_count": 5,
                "risk_score": 0.15,
                "card_age": 365,
                "hour": 14,
                "month": 12
            }
        }


class PredictionResponse(BaseModel):
    """Prediction response"""
    fraud_probability: float = Field(..., description="Probability of fraud (0-1)")
    is_fraud: bool = Field(..., description="Fraud prediction (True/False)")
    confidence: float = Field(..., description="Confidence score")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    timestamp: str = Field(..., description="Prediction timestamp")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    timestamp: str


class BatchPredictionRequest(BaseModel):
    """Batch prediction request"""
    transactions: List[TransactionRequest] = Field(..., max_items=100, description="List of transactions (max 100)")


class BatchPredictionResponse(BaseModel):
    """Batch prediction response"""
    predictions: List[PredictionResponse]
    total_transactions: int
    total_fraud_detected: int
    response_time_ms: float


# Helper function to preprocess transaction data
def preprocess_transaction(transaction: TransactionRequest) -> pd.DataFrame:
    """Convert transaction request to DataFrame with proper feature order"""
    from datetime import datetime
    
    # Get Hour and Month (use provided values or current time)
    now = datetime.now()
    hour = transaction.hour if transaction.hour is not None else now.hour
    month = transaction.month if transaction.month is not None else now.month
    
    # Calculate derived features (use provided values if sent, otherwise calculate)
    failed_count = transaction.failed_transaction_count_7d
    daily_count = transaction.daily_transaction_count
    
    # High_Failure_Flag: 1 if failed transactions > 0, else 0
    high_failure_flag = transaction.high_failure_flag if transaction.high_failure_flag is not None else (1 if failed_count > 0 else 0)
    
    # Failure_Rate: failed transactions / daily transactions (avoid division by zero)
    failure_rate = transaction.failure_rate if transaction.failure_rate is not None else (failed_count / daily_count if daily_count > 0 else 0.0)
    
    # Amount_Deviation: difference between current and average
    amount_deviation = transaction.amount_deviation if transaction.amount_deviation is not None else abs(transaction.transaction_amount - transaction.avg_transaction_amount_7d)
    
    # Risk_Amount_Interaction: interaction between risk score and amount
    risk_amount_interaction = transaction.risk_amount_interaction if transaction.risk_amount_interaction is not None else (transaction.risk_score * transaction.transaction_amount)
    
    # Build feature dictionary matching model expectations (exact order)
    data = {
        'Failed_Transaction_Count_7d': [failed_count],
        'Risk_Score': [transaction.risk_score],
        'High_Failure_Flag': [high_failure_flag],
        'Transaction_Amount': [transaction.transaction_amount],
        'Avg_Transaction_Amount_7d': [transaction.avg_transaction_amount_7d],
        'Risk_Amount_Interaction': [risk_amount_interaction],
        'Amount_Deviation': [amount_deviation],
        'Failure_Rate': [failure_rate],
        'Hour': [hour],
        'Card_Age': [transaction.card_age],
        'Month': [month]
    }
    
    df = pd.DataFrame(data)
    
    # Reorder columns to match model expectations if feature_names is available
    if feature_names:
        # Ensure all required features are present
        missing_features = [f for f in feature_names if f not in df.columns]
        if missing_features:
            logger.warning(f"Missing features: {missing_features}. Using defaults.")
            # Add missing features with default values
            for feat in missing_features:
                df[feat] = 0.0
        
        # Reorder to match model's expected feature order
        df = df[feature_names]
    
    return df


# Middleware to measure response time
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Serve favicon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve favicon"""
    return Response(content="", media_type="image/svg+xml")

# Serve web interface at root
@app.get("/", tags=["Web Interface"], include_in_schema=False)
async def serve_web_interface():
    """Serve the web interface"""
    try:
        return FileResponse("static/index.html")
    except Exception:
        return {
            "message": "Fraud Detection API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
            "note": "Web interface not available. Please check static files."
        }

# API root endpoint
@app.get("/api", tags=["General"])
async def api_root():
    """API root endpoint"""
    return {
        "message": "Fraud Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "web_interface": "/"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        timestamp=datetime.now().isoformat()
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_fraud(transaction: TransactionRequest):
    """
    Predict fraud for a single transaction
    
    **Required Features:**
    - **transaction_amount**: Amount of the transaction
    - **avg_transaction_amount_7d**: Average transaction amount in last 7 days
    - **failed_transaction_count_7d**: Failed transactions in last 7 days
    - **daily_transaction_count**: Number of transactions today (used to calculate failure rate)
    - **risk_score**: Risk score (0-1)
    - **card_age**: Age of card in days
    
    **Optional Features (auto-calculated if not provided):**
    - **hour**: Hour of day (0-23), defaults to current hour
    - **month**: Month (1-12), defaults to current month
    
    **Derived Features (calculated automatically):**
    - High_Failure_Flag: 1 if failed_transaction_count_7d > 0, else 0
    - Failure_Rate: failed_transaction_count_7d / daily_transaction_count
    - Amount_Deviation: |transaction_amount - avg_transaction_amount_7d|
    - Risk_Amount_Interaction: risk_score * transaction_amount
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    start_time = time.time()
    
    try:
        # Preprocess transaction
        df = preprocess_transaction(transaction)
        
        # Make prediction
        fraud_probability = model.predict_proba(df)[0][1]
        is_fraud = model.predict(df)[0] == 1
        confidence = abs(fraud_probability - 0.5) * 2  # Normalize to 0-1
        
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return PredictionResponse(
            fraud_probability=float(fraud_probability),
            is_fraud=bool(is_fraud),
            confidence=float(confidence),
            response_time_ms=round(response_time, 2),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_fraud_batch(batch_request: BatchPredictionRequest):
    """
    Predict fraud for multiple transactions (batch processing)
    
    Maximum 100 transactions per batch
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if len(batch_request.transactions) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 transactions per batch")
    
    start_time = time.time()
    predictions = []
    total_fraud = 0
    
    try:
        for transaction in batch_request.transactions:
            df = preprocess_transaction(transaction)
            fraud_probability = model.predict_proba(df)[0][1]
            is_fraud = model.predict(df)[0] == 1
            confidence = abs(fraud_probability - 0.5) * 2
            
            if is_fraud:
                total_fraud += 1
            
            predictions.append(PredictionResponse(
                fraud_probability=float(fraud_probability),
                is_fraud=bool(is_fraud),
                confidence=float(confidence),
                response_time_ms=0,  # Individual time not tracked in batch
                timestamp=datetime.now().isoformat()
            ))
        
        response_time = (time.time() - start_time) * 1000
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_transactions=len(predictions),
            total_fraud_detected=total_fraud,
            response_time_ms=round(response_time, 2)
        )
    
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Get API metrics"""
    return {
        "model_loaded": model is not None,
        "model_type": type(model).__name__ if model else None,
        "feature_count": len(feature_names) if feature_names else 0,
        "timestamp": datetime.now().isoformat()
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    import os
    # Use PORT environment variable (for Heroku) or default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

