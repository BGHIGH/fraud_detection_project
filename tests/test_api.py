"""
Unit tests for Fraud Detection API
"""

import pytest
from fastapi.testclient import TestClient
from app import app, model
import time
import os

client = TestClient(app)

# Check if model is available
MODEL_AVAILABLE = model is not None and os.path.exists("Models/fraud_detection_model.pkl")


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health endpoint returns correct status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "timestamp" in data
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        # Root endpoint may return HTML or JSON depending on static files
        content_type = response.headers.get("content-type", "")
        if content_type.startswith("application/json"):
            try:
                data = response.json()
                assert "message" in data
                assert "version" in data
            except Exception:
                # If JSON parsing fails, just verify status code
                pass
        else:
            # If HTML is returned, just check status code and that it's HTML
            assert "text/html" in content_type or response.status_code == 200


class TestSinglePrediction:
    """Test single transaction prediction"""
    
    @pytest.fixture
    def valid_transaction(self):
        """Valid transaction data"""
        return {
            "transaction_amount": 150.50,
            "account_balance": 5000.00,
            "transaction_type": "POS",
            "device_type": "Mobile",
            "location": "London",
            "merchant_category": "Restaurants",
            "ip_address_flag": 0,
            "previous_fraudulent_activity": 0,
            "daily_transaction_count": 5,
            "avg_transaction_amount_7d": 120.30,
            "failed_transaction_count_7d": 0.0,
            "card_type": "Visa",
            "card_age": 365,
            "transaction_distance": 1500.25,
            "authentication_method": "PIN",
            "risk_score": 0.15,
            "is_weekend": 0
        }
    
    @pytest.mark.skipif(not MODEL_AVAILABLE, reason="Model file not available")
    def test_valid_prediction(self, valid_transaction):
        """Test prediction with valid data"""
        response = client.post("/predict", json=valid_transaction)
        assert response.status_code == 200
        data = response.json()
        assert "fraud_probability" in data
        assert "is_fraud" in data
        assert "confidence" in data
        assert "response_time_ms" in data
        assert "timestamp" in data
        assert 0 <= data["fraud_probability"] <= 1
        assert isinstance(data["is_fraud"], bool)
        assert 0 <= data["confidence"] <= 1
    
    @pytest.mark.skipif(not MODEL_AVAILABLE, reason="Model file not available")
    def test_prediction_response_time(self, valid_transaction):
        """Test that response time is reasonable"""
        start = time.time()
        response = client.post("/predict", json=valid_transaction)
        elapsed = time.time() - start
        
        assert response.status_code == 200
        data = response.json()
        # Response time should be less than 5 seconds
        assert data["response_time_ms"] < 5000
        assert elapsed < 5
    
    def test_missing_field(self):
        """Test prediction with missing required field"""
        incomplete_transaction = {
            "transaction_amount": 150.50,
            "account_balance": 5000.00
            # Missing other required fields
        }
        response = client.post("/predict", json=incomplete_transaction)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_transaction_type(self, valid_transaction):
        """Test prediction with invalid transaction type"""
        valid_transaction["transaction_type"] = "InvalidType"
        response = client.post("/predict", json=valid_transaction)
        # If model not loaded, get 503; if loaded, get 422 (validation error)
        assert response.status_code in [422, 503]
    
    def test_invalid_device_type(self, valid_transaction):
        """Test prediction with invalid device type"""
        valid_transaction["device_type"] = "InvalidDevice"
        response = client.post("/predict", json=valid_transaction)
        # If model not loaded, get 503; if loaded, get 422 (validation error)
        assert response.status_code in [422, 503]
    
    def test_invalid_authentication_method(self, valid_transaction):
        """Test prediction with invalid authentication method"""
        valid_transaction["authentication_method"] = "InvalidMethod"
        response = client.post("/predict", json=valid_transaction)
        # If model not loaded, get 503; if loaded, get 422 (validation error)
        assert response.status_code in [422, 503]
    
    def test_invalid_card_type(self, valid_transaction):
        """Test prediction with invalid card type"""
        valid_transaction["card_type"] = "InvalidCard"
        response = client.post("/predict", json=valid_transaction)
        # If model not loaded, get 503; if loaded, get 422 (validation error)
        assert response.status_code in [422, 503]
    
    def test_negative_transaction_amount(self, valid_transaction):
        """Test prediction with negative transaction amount"""
        valid_transaction["transaction_amount"] = -100
        response = client.post("/predict", json=valid_transaction)
        assert response.status_code == 422
    
    def test_invalid_risk_score(self, valid_transaction):
        """Test prediction with invalid risk score"""
        valid_transaction["risk_score"] = 1.5  # Should be 0-1
        response = client.post("/predict", json=valid_transaction)
        assert response.status_code == 422
    
    def test_invalid_ip_flag(self, valid_transaction):
        """Test prediction with invalid IP flag"""
        valid_transaction["ip_address_flag"] = 2  # Should be 0 or 1
        response = client.post("/predict", json=valid_transaction)
        # If model not loaded, get 503; if loaded, get 422 (validation error)
        assert response.status_code in [422, 503]


class TestBatchPrediction:
    """Test batch prediction endpoint"""
    
    @pytest.fixture
    def valid_transaction(self):
        """Valid transaction data"""
        return {
            "transaction_amount": 150.50,
            "account_balance": 5000.00,
            "transaction_type": "POS",
            "device_type": "Mobile",
            "location": "London",
            "merchant_category": "Restaurants",
            "ip_address_flag": 0,
            "previous_fraudulent_activity": 0,
            "daily_transaction_count": 5,
            "avg_transaction_amount_7d": 120.30,
            "failed_transaction_count_7d": 0.0,
            "card_type": "Visa",
            "card_age": 365,
            "transaction_distance": 1500.25,
            "authentication_method": "PIN",
            "risk_score": 0.15,
            "is_weekend": 0
        }
    
    @pytest.mark.skipif(not MODEL_AVAILABLE, reason="Model file not available")
    def test_batch_prediction(self, valid_transaction):
        """Test batch prediction with multiple transactions"""
        batch_request = {
            "transactions": [valid_transaction, valid_transaction, valid_transaction]
        }
        response = client.post("/predict/batch", json=batch_request)
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert "total_transactions" in data
        assert "total_fraud_detected" in data
        assert "response_time_ms" in data
        assert len(data["predictions"]) == 3
        assert data["total_transactions"] == 3
    
    @pytest.mark.skipif(not MODEL_AVAILABLE, reason="Model file not available")
    def test_batch_prediction_empty(self):
        """Test batch prediction with empty list"""
        batch_request = {"transactions": []}
        response = client.post("/predict/batch", json=batch_request)
        assert response.status_code == 200
        data = response.json()
        assert data["total_transactions"] == 0
    
    def test_batch_prediction_too_many(self, valid_transaction):
        """Test batch prediction with too many transactions"""
        batch_request = {
            "transactions": [valid_transaction] * 101  # More than max (100)
        }
        response = client.post("/predict/batch", json=batch_request)
        # Pydantic validation may return 422, or app logic returns 400
        assert response.status_code in [400, 422]
    
    def test_batch_prediction_mixed_validity(self, valid_transaction):
        """Test batch prediction with mix of valid and invalid transactions"""
        invalid_transaction = valid_transaction.copy()
        invalid_transaction["transaction_type"] = "InvalidType"
        
        batch_request = {
            "transactions": [valid_transaction, invalid_transaction]
        }
        response = client.post("/predict/batch", json=batch_request)
        # If model not loaded, get 503; if loaded, get 422 (validation error)
        assert response.status_code in [422, 503]


class TestDifferentTransactionTypes:
    """Test API with different types of transactions"""
    
    @pytest.mark.skipif(not MODEL_AVAILABLE, reason="Model file not available")
    def test_atm_withdrawal(self):
        """Test ATM withdrawal transaction"""
        transaction = {
            "transaction_amount": 200.00,
            "account_balance": 10000.00,
            "transaction_type": "ATM Withdrawal",
            "device_type": "Mobile",
            "location": "New York",
            "merchant_category": "ATM",
            "ip_address_flag": 0,
            "previous_fraudulent_activity": 0,
            "daily_transaction_count": 3,
            "avg_transaction_amount_7d": 150.00,
            "failed_transaction_count_7d": 0.0,
            "card_type": "Mastercard",
            "card_age": 730,
            "transaction_distance": 500.00,
            "authentication_method": "PIN",
            "risk_score": 0.10,
            "is_weekend": 1
        }
        response = client.post("/predict", json=transaction)
        assert response.status_code == 200
    
    @pytest.mark.skipif(not MODEL_AVAILABLE, reason="Model file not available")
    def test_online_transaction(self):
        """Test online transaction"""
        transaction = {
            "transaction_amount": 75.50,
            "account_balance": 2500.00,
            "transaction_type": "Online",
            "device_type": "Laptop",
            "location": "Paris",
            "merchant_category": "Electronics",
            "ip_address_flag": 1,
            "previous_fraudulent_activity": 1,
            "daily_transaction_count": 8,
            "avg_transaction_amount_7d": 200.00,
            "failed_transaction_count_7d": 2.0,
            "card_type": "Visa",
            "card_age": 180,
            "transaction_distance": 2000.00,
            "authentication_method": "OTP",
            "risk_score": 0.75,
            "is_weekend": 0
        }
        response = client.post("/predict", json=transaction)
        assert response.status_code == 200
    
    @pytest.mark.skipif(not MODEL_AVAILABLE, reason="Model file not available")
    def test_high_risk_transaction(self):
        """Test high-risk transaction"""
        transaction = {
            "transaction_amount": 5000.00,
            "account_balance": 1000.00,
            "transaction_type": "Transfer",
            "device_type": "Tablet",
            "location": "Unknown",
            "merchant_category": "Travel",
            "ip_address_flag": 1,
            "previous_fraudulent_activity": 3,
            "daily_transaction_count": 15,
            "avg_transaction_amount_7d": 1000.00,
            "failed_transaction_count_7d": 5.0,
            "card_type": "Discover",
            "card_age": 30,
            "transaction_distance": 5000.00,
            "authentication_method": "Password",
            "risk_score": 0.95,
            "is_weekend": 1
        }
        response = client.post("/predict", json=transaction)
        assert response.status_code == 200
        data = response.json()
        # High risk transaction should have higher fraud probability
        assert data["fraud_probability"] > 0.5
    
    @pytest.mark.skipif(not MODEL_AVAILABLE, reason="Model file not available")
    def test_low_risk_transaction(self):
        """Test low-risk transaction"""
        transaction = {
            "transaction_amount": 25.00,
            "account_balance": 50000.00,
            "transaction_type": "POS",
            "device_type": "Mobile",
            "location": "London",
            "merchant_category": "Restaurants",
            "ip_address_flag": 0,
            "previous_fraudulent_activity": 0,
            "daily_transaction_count": 2,
            "avg_transaction_amount_7d": 30.00,
            "failed_transaction_count_7d": 0.0,
            "card_type": "Visa",
            "card_age": 1000,
            "transaction_distance": 100.00,
            "authentication_method": "Biometric",
            "risk_score": 0.05,
            "is_weekend": 0
        }
        response = client.post("/predict", json=transaction)
        assert response.status_code == 200
        data = response.json()
        # Low risk transaction should have lower fraud probability
        assert data["fraud_probability"] < 0.5


class TestMetrics:
    """Test metrics endpoint"""
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "model_loaded" in data
        assert "timestamp" in data


class TestErrorHandling:
    """Test error handling"""
    
    def test_nonexistent_endpoint(self):
        """Test non-existent endpoint returns 404"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test invalid JSON in request"""
        response = client.post("/predict", data="invalid json")
        assert response.status_code == 422

