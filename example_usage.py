"""
Example usage of the Fraud Detection API
Demonstrates how to make predictions using the API
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"


def example_single_prediction():
    """Example: Single transaction prediction"""
    print("=" * 60)
    print("Example: Single Transaction Prediction")
    print("=" * 60)
    
    transaction = {
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
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=transaction,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Prediction successful!")
            print(f"\nTransaction Details:")
            print(f"  Amount: ${transaction['transaction_amount']}")
            print(f"  Type: {transaction['transaction_type']}")
            print(f"  Location: {transaction['location']}")
            
            print(f"\nPrediction Results:")
            print(f"  Fraud Probability: {result['fraud_probability']:.4f} ({result['fraud_probability']*100:.2f}%)")
            print(f"  Is Fraud: {'Yes' if result['is_fraud'] else 'No'}")
            print(f"  Confidence: {result['confidence']:.4f} ({result['confidence']*100:.2f}%)")
            print(f"  Response Time: {result['response_time_ms']:.2f} ms")
            print(f"  Timestamp: {result['timestamp']}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.json())
    
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the API is running: python app.py or ./start_api.sh")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def example_batch_prediction():
    """Example: Batch transaction prediction"""
    print("\n" + "=" * 60)
    print("Example: Batch Transaction Prediction")
    print("=" * 60)
    
    transactions = [
        {
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
        },
        {
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
    ]
    
    batch_request = {"transactions": transactions}
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict/batch",
            json=batch_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Batch prediction successful!")
            print(f"\nBatch Results:")
            print(f"  Total Transactions: {result['total_transactions']}")
            print(f"  Fraud Detected: {result['total_fraud_detected']}")
            print(f"  Response Time: {result['response_time_ms']:.2f} ms")
            
            print(f"\nIndividual Predictions:")
            for i, pred in enumerate(result['predictions'], 1):
                print(f"\n  Transaction {i}:")
                print(f"    Amount: ${transactions[i-1]['transaction_amount']}")
                print(f"    Fraud Probability: {pred['fraud_probability']:.4f}")
                print(f"    Is Fraud: {'Yes' if pred['is_fraud'] else 'No'}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.json())
    
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the API is running: python app.py or ./start_api.sh")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def example_health_check():
    """Example: Health check"""
    print("\n" + "=" * 60)
    print("Example: Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ API is healthy!")
            print(f"  Status: {result['status']}")
            print(f"  Model Loaded: {result['model_loaded']}")
            print(f"  Timestamp: {result['timestamp']}")
        else:
            print(f"\n❌ Error: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the API is running: python app.py or ./start_api.sh")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def example_metrics():
    """Example: Get metrics"""
    print("\n" + "=" * 60)
    print("Example: API Metrics")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/metrics", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Metrics retrieved!")
            print(json.dumps(result, indent=2))
        else:
            print(f"\n❌ Error: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the API is running: python app.py or ./start_api.sh")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Fraud Detection API - Example Usage")
    print("=" * 60)
    print("\nMake sure the API is running on http://localhost:8000")
    print("Start it with: python app.py or ./start_api.sh\n")
    
    # Run examples
    example_health_check()
    example_single_prediction()
    example_batch_prediction()
    example_metrics()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nFor interactive API documentation, visit: http://localhost:8000/docs")

