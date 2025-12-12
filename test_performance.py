"""
Performance testing script for Fraud Detection API
Measures response times and tests with different transaction types
"""

import requests
import time
import statistics
from typing import List, Dict
import json

API_BASE_URL = "http://localhost:8000"


def create_transaction(
    transaction_amount: float = 150.50,
    account_balance: float = 5000.00,
    transaction_type: str = "POS",
    device_type: str = "Mobile",
    location: str = "London",
    merchant_category: str = "Restaurants",
    ip_address_flag: int = 0,
    previous_fraudulent_activity: int = 0,
    daily_transaction_count: int = 5,
    avg_transaction_amount_7d: float = 120.30,
    failed_transaction_count_7d: float = 0.0,
    card_type: str = "Visa",
    card_age: int = 365,
    transaction_distance: float = 1500.25,
    authentication_method: str = "PIN",
    risk_score: float = 0.15,
    is_weekend: int = 0
) -> Dict:
    """Create a transaction dictionary"""
    return {
        "transaction_amount": transaction_amount,
        "account_balance": account_balance,
        "transaction_type": transaction_type,
        "device_type": device_type,
        "location": location,
        "merchant_category": merchant_category,
        "ip_address_flag": ip_address_flag,
        "previous_fraudulent_activity": previous_fraudulent_activity,
        "daily_transaction_count": daily_transaction_count,
        "avg_transaction_amount_7d": avg_transaction_amount_7d,
        "failed_transaction_count_7d": failed_transaction_count_7d,
        "card_type": card_type,
        "card_age": card_age,
        "transaction_distance": transaction_distance,
        "authentication_method": authentication_method,
        "risk_score": risk_score,
        "is_weekend": is_weekend
    }


def test_single_prediction(transaction: Dict, iterations: int = 100) -> Dict:
    """Test single prediction endpoint performance"""
    print(f"\n{'='*60}")
    print(f"Testing Single Prediction Endpoint ({iterations} iterations)")
    print(f"{'='*60}")
    
    response_times = []
    errors = 0
    
    for i in range(iterations):
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/predict",
                json=transaction,
                timeout=10
            )
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200:
                response_times.append(elapsed)
                data = response.json()
                if i == 0:  # Print first response
                    print(f"\nFirst Response:")
                    print(f"  Fraud Probability: {data['fraud_probability']:.4f}")
                    print(f"  Is Fraud: {data['is_fraud']}")
                    print(f"  Confidence: {data['confidence']:.4f}")
                    print(f"  Response Time: {data['response_time_ms']:.2f} ms")
            else:
                errors += 1
                print(f"Error on iteration {i+1}: {response.status_code}")
        except Exception as e:
            errors += 1
            print(f"Exception on iteration {i+1}: {str(e)}")
    
    if response_times:
        stats = {
            "mean": statistics.mean(response_times),
            "median": statistics.median(response_times),
            "min": min(response_times),
            "max": max(response_times),
            "stdev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
            "p95": sorted(response_times)[int(len(response_times) * 0.95)],
            "p99": sorted(response_times)[int(len(response_times) * 0.99)],
            "errors": errors,
            "success_rate": (iterations - errors) / iterations * 100
        }
        
        print(f"\nPerformance Statistics:")
        print(f"  Mean Response Time: {stats['mean']:.2f} ms")
        print(f"  Median Response Time: {stats['median']:.2f} ms")
        print(f"  Min Response Time: {stats['min']:.2f} ms")
        print(f"  Max Response Time: {stats['max']:.2f} ms")
        print(f"  Standard Deviation: {stats['stdev']:.2f} ms")
        print(f"  95th Percentile: {stats['p95']:.2f} ms")
        print(f"  99th Percentile: {stats['p99']:.2f} ms")
        print(f"  Errors: {stats['errors']}")
        print(f"  Success Rate: {stats['success_rate']:.2f}%")
        
        return stats
    else:
        print("No successful responses!")
        return None


def test_batch_prediction(batch_size: int = 10, iterations: int = 10) -> Dict:
    """Test batch prediction endpoint performance"""
    print(f"\n{'='*60}")
    print(f"Testing Batch Prediction Endpoint (batch_size={batch_size}, {iterations} iterations)")
    print(f"{'='*60}")
    
    transaction = create_transaction()
    batch_request = {"transactions": [transaction] * batch_size}
    
    response_times = []
    errors = 0
    
    for i in range(iterations):
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/predict/batch",
                json=batch_request,
                timeout=30
            )
            elapsed = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                response_times.append(elapsed)
                data = response.json()
                if i == 0:
                    print(f"\nFirst Response:")
                    print(f"  Total Transactions: {data['total_transactions']}")
                    print(f"  Fraud Detected: {data['total_fraud_detected']}")
                    print(f"  Response Time: {data['response_time_ms']:.2f} ms")
            else:
                errors += 1
        except Exception as e:
            errors += 1
            print(f"Exception on iteration {i+1}: {str(e)}")
    
    if response_times:
        stats = {
            "mean": statistics.mean(response_times),
            "median": statistics.median(response_times),
            "min": min(response_times),
            "max": max(response_times),
            "stdev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
            "errors": errors,
            "success_rate": (iterations - errors) / iterations * 100,
            "avg_time_per_transaction": statistics.mean(response_times) / batch_size
        }
        
        print(f"\nPerformance Statistics:")
        print(f"  Mean Response Time: {stats['mean']:.2f} ms")
        print(f"  Median Response Time: {stats['median']:.2f} ms")
        print(f"  Min Response Time: {stats['min']:.2f} ms")
        print(f"  Max Response Time: {stats['max']:.2f} ms")
        print(f"  Avg Time per Transaction: {stats['avg_time_per_transaction']:.2f} ms")
        print(f"  Errors: {stats['errors']}")
        print(f"  Success Rate: {stats['success_rate']:.2f}%")
        
        return stats
    else:
        print("No successful responses!")
        return None


def test_different_transaction_types():
    """Test API with different types of transactions"""
    print(f"\n{'='*60}")
    print("Testing Different Transaction Types")
    print(f"{'='*60}")
    
    test_cases = [
        {
            "name": "Low Risk - Small POS Transaction",
            "transaction": create_transaction(
                transaction_amount=25.00,
                account_balance=50000.00,
                transaction_type="POS",
                risk_score=0.05,
                previous_fraudulent_activity=0,
                failed_transaction_count_7d=0.0
            )
        },
        {
            "name": "Medium Risk - Online Purchase",
            "transaction": create_transaction(
                transaction_amount=200.00,
                account_balance=2000.00,
                transaction_type="Online",
                device_type="Laptop",
                risk_score=0.45,
                ip_address_flag=1,
                authentication_method="OTP"
            )
        },
        {
            "name": "High Risk - Large Transfer",
            "transaction": create_transaction(
                transaction_amount=5000.00,
                account_balance=1000.00,
                transaction_type="Transfer",
                risk_score=0.95,
                previous_fraudulent_activity=3,
                failed_transaction_count_7d=5.0,
                transaction_distance=5000.00
            )
        },
        {
            "name": "ATM Withdrawal - Weekend",
            "transaction": create_transaction(
                transaction_amount=300.00,
                account_balance=10000.00,
                transaction_type="ATM Withdrawal",
                device_type="Mobile",
                is_weekend=1,
                authentication_method="PIN"
            )
        },
        {
            "name": "High Value - Travel Category",
            "transaction": create_transaction(
                transaction_amount=2000.00,
                account_balance=15000.00,
                transaction_type="Payment",
                merchant_category="Travel",
                card_type="Mastercard",
                risk_score=0.60
            )
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/predict",
                json=test_case['transaction'],
                timeout=10
            )
            elapsed = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "name": test_case['name'],
                    "fraud_probability": data['fraud_probability'],
                    "is_fraud": data['is_fraud'],
                    "confidence": data['confidence'],
                    "response_time_ms": elapsed
                }
                results.append(result)
                
                print(f"  Fraud Probability: {result['fraud_probability']:.4f}")
                print(f"  Is Fraud: {result['is_fraud']}")
                print(f"  Confidence: {result['confidence']:.4f}")
                print(f"  Response Time: {result['response_time_ms']:.2f} ms")
            else:
                print(f"  Error: {response.status_code}")
        except Exception as e:
            print(f"  Exception: {str(e)}")
    
    return results


def check_health():
    """Check API health"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"API Health: {data['status']}")
            print(f"Model Loaded: {data['model_loaded']}")
            return data['model_loaded']
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Health check error: {str(e)}")
        return False


def main():
    """Main performance testing function"""
    print("="*60)
    print("Fraud Detection API Performance Testing")
    print("="*60)
    
    # Check health first
    if not check_health():
        print("API is not healthy. Please start the API first.")
        return
    
    # Test with standard transaction
    standard_transaction = create_transaction()
    single_stats = test_single_prediction(standard_transaction, iterations=100)
    
    # Test batch prediction
    batch_stats = test_batch_prediction(batch_size=10, iterations=10)
    
    # Test different transaction types
    type_results = test_different_transaction_types()
    
    # Summary
    print(f"\n{'='*60}")
    print("Performance Testing Summary")
    print(f"{'='*60}")
    
    if single_stats:
        print(f"\nSingle Prediction:")
        print(f"  Average Response Time: {single_stats['mean']:.2f} ms")
        print(f"  95th Percentile: {single_stats['p95']:.2f} ms")
        print(f"  Success Rate: {single_stats['success_rate']:.2f}%")
    
    if batch_stats:
        print(f"\nBatch Prediction (10 transactions):")
        print(f"  Average Response Time: {batch_stats['mean']:.2f} ms")
        print(f"  Avg Time per Transaction: {batch_stats['avg_time_per_transaction']:.2f} ms")
        print(f"  Success Rate: {batch_stats['success_rate']:.2f}%")
    
    print(f"\nDifferent Transaction Types Tested: {len(type_results)}")
    for result in type_results:
        print(f"  {result['name']}: {result['fraud_probability']:.4f} probability")


if __name__ == "__main__":
    main()

