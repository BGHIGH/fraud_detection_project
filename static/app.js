// Fraud Detection System - Frontend JavaScript

const API_BASE_URL = window.location.origin || 'http://localhost:8000';
let fraudChart = null;
let predictionHistory = [];
let apiStatus = 'unknown';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Link risk score slider to input
    const slider = document.getElementById('risk_score_slider');
    const input = document.getElementById('risk_score');
    
    if (slider && input) {
        slider.addEventListener('input', function() {
            input.value = this.value;
        });
        
        input.addEventListener('input', function() {
            slider.value = this.value;
        });
    }
    
    // Form submission
    const form = document.getElementById('prediction-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit, false);
        // Also prevent default on form element itself
        form.onsubmit = function(e) {
            e.preventDefault();
            return false;
        };
    }
    
    // Check API health on load
    checkAPIHealth();
    
    // Check API health every 30 seconds
    setInterval(checkAPIHealth, 30000);
    
    // Add form validation feedback
    if (form) {
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    }
});

// Validate individual field
function validateField(field) {
    if (field.checkValidity()) {
        field.classList.remove('border-red-500', 'ring-red-500');
        field.classList.add('border-green-500');
    } else {
        field.classList.remove('border-green-500');
        field.classList.add('border-red-500', 'ring-2', 'ring-red-500');
    }
}

// Update risk score from slider
function updateRiskScore(value) {
    const riskScoreInput = document.getElementById('risk_score');
    if (riskScoreInput) {
        riskScoreInput.value = value;
    }
}

// Check API health
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        apiStatus = data.model_loaded ? 'healthy' : 'unhealthy';
        updateAPIStatusIndicator(apiStatus);
        
        if (!data.model_loaded) {
            showToast('Warning: Model not loaded. Please check the API.', 'error');
        } else {
            // Show success indicator briefly
            const statusEl = document.getElementById('api-status');
            if (statusEl) {
                statusEl.style.display = 'inline-block';
                setTimeout(() => {
                    if (statusEl) statusEl.style.opacity = '0.7';
                }, 2000);
            }
        }
    } catch (error) {
        apiStatus = 'error';
        updateAPIStatusIndicator('error');
        showToast('Cannot connect to API. Make sure it is running.', 'error');
    }
}

// Update API status indicator
function updateAPIStatusIndicator(status) {
    const statusEl = document.getElementById('api-status');
    if (!statusEl) return;
    
    const baseClasses = 'px-4 py-2 rounded-full text-sm font-semibold backdrop-blur-sm transition-all';
    const statusClasses = {
        'healthy': 'bg-green-500/20 text-green-100',
        'unhealthy': 'bg-yellow-500/20 text-yellow-100',
        'error': 'bg-red-500/20 text-red-100',
        'unknown': 'bg-gray-500/20 text-gray-100'
    };
    
    statusEl.className = `${baseClasses} ${statusClasses[status] || statusClasses.unknown}`;
    const icons = {
        'healthy': 'fa-check-circle',
        'unhealthy': 'fa-exclamation-triangle',
        'error': 'fa-times-circle',
        'unknown': 'fa-circle'
    };
    const texts = {
        'healthy': 'API Online',
        'unhealthy': 'Model Not Loaded',
        'error': 'API Offline',
        'unknown': 'Checking...'
    };
    
    statusEl.innerHTML = `<i class="fas ${icons[status]} text-xs"></i> <span>${texts[status]}</span>`;
}

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    event.stopPropagation();
    
    // Double check - prevent any default form behavior
    if (event && event.preventDefault) {
        event.preventDefault();
    }
    
    const formData = new FormData(event.target);
    
    // Convert form data to object - only collect required fields
    const transaction_amount = parseFloat(formData.get('transaction_amount'));
    const avg_transaction_amount_7d = parseFloat(formData.get('avg_transaction_amount_7d'));
    const failed_transaction_count_7d = parseFloat(formData.get('failed_transaction_count_7d'));
    const daily_transaction_count = parseInt(formData.get('daily_transaction_count'));
    const risk_score = parseFloat(formData.get('risk_score'));
    const card_age = parseInt(formData.get('card_age'));
    
    // Get hour and month (use current time if not provided)
    let hour = formData.get('hour');
    let month = formData.get('month');
    if (!hour || hour === '') {
        hour = new Date().getHours();
    } else {
        hour = parseInt(hour);
    }
    if (!month || month === '') {
        month = new Date().getMonth() + 1; // getMonth() returns 0-11
    } else {
        month = parseInt(month);
    }
    
    // Calculate derived features
    const high_failure_flag = failed_transaction_count_7d > 0 ? 1 : 0;
    const failure_rate = daily_transaction_count > 0 ? failed_transaction_count_7d / daily_transaction_count : 0.0;
    const amount_deviation = Math.abs(transaction_amount - avg_transaction_amount_7d);
    const risk_amount_interaction = risk_score * transaction_amount;
    
    // Build transaction object with only required features
    const transaction = {
        transaction_amount: transaction_amount,
        avg_transaction_amount_7d: avg_transaction_amount_7d,
        failed_transaction_count_7d: failed_transaction_count_7d,
        daily_transaction_count: daily_transaction_count,
        risk_score: risk_score,
        card_age: card_age,
        hour: hour,
        month: month,
        // Derived features (will be calculated on backend too, but send for reference)
        high_failure_flag: high_failure_flag,
        failure_rate: failure_rate,
        amount_deviation: amount_deviation,
        risk_amount_interaction: risk_amount_interaction
    };
    
    // Show loading
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(transaction)
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Prediction failed' }));
            throw new Error(errorData.detail || errorData.message || 'Prediction failed');
        }
        
        const result = await response.json();
        console.log('Prediction result:', result); // Debug log
        displayResults(result, transaction);
        
        // Save to history
        predictionHistory.push({
            transaction,
            result,
            timestamp: new Date().toISOString()
        });
        
        showToast('Transaction analyzed successfully!', 'success');
        
    } catch (error) {
        console.error('Prediction error:', error);
        showToast(`Error: ${error.message}`, 'error');
        // Show error details in console for debugging
        if (error.response) {
            console.error('Response error:', error.response);
        }
    } finally {
        hideLoading();
    }
}

// Display results
function displayResults(result, transaction) {
    console.log('Displaying results:', result, transaction); // Debug log
    
    const resultsCard = document.getElementById('results-card');
    const fraudStatus = document.getElementById('fraud-status');
    const fraudProbability = document.getElementById('fraud-probability');
    const confidence = document.getElementById('confidence');
    const responseTime = document.getElementById('response-time');
    const detailedInfo = document.getElementById('detailed-info');
    
    // Check if elements exist
    if (!resultsCard) {
        console.error('Results card element not found!');
        showToast('Error: Results card not found', 'error');
        return;
    }
    
    // Show results card
    resultsCard.style.display = 'block';
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Update fraud status
    const isFraud = result.is_fraud;
    const probability = result.fraud_probability;
    const probPercent = (probability * 100).toFixed(2);
    
    // Determine risk level
    let riskLevel = 'low';
    let riskColor = '#10b981';
    let riskText = 'Low Risk';
    
    if (probability >= 0.7) {
        riskLevel = 'high';
        riskColor = '#ef4444';
        riskText = 'High Risk';
    } else if (probability >= 0.4) {
        riskLevel = 'medium';
        riskColor = '#f59e0b';
        riskText = 'Medium Risk';
    }
    
    // Update fraud status with 3D effect
    const statusGradient = isFraud 
        ? 'background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);' 
        : 'background: linear-gradient(135deg, #10b981 0%, #059669 100%);';
    
    fraudStatus.setAttribute('style', statusGradient);
    
    const iconEl = document.getElementById('fraud-icon');
    const titleEl = document.getElementById('fraud-title');
    const descEl = document.getElementById('fraud-description');
    const detailsEl = document.getElementById('fraud-details');
    
    if (iconEl) {
        iconEl.className = `fas ${isFraud ? 'fa-exclamation-triangle' : 'fa-check-circle'} text-6xl mb-4 transform transition-all animate-pulse`;
        iconEl.style.animation = 'pulse 2s infinite';
    }
    
    if (titleEl) {
        titleEl.textContent = isFraud ? 'FRAUD DETECTED' : 'TRANSACTION SAFE';
        titleEl.className = 'text-3xl font-bold mb-3 drop-shadow-lg';
    }
    
    if (descEl) {
        descEl.textContent = isFraud 
            ? 'This transaction has been flagged as potentially fraudulent.' 
            : 'This transaction appears to be legitimate.';
        descEl.className = 'text-base opacity-90 mb-6';
    }
    
    if (detailsEl) {
        detailsEl.innerHTML = `
            <div class="text-sm opacity-90 mb-2">
                <span class="font-semibold">Risk Level:</span> 
                <strong class="text-lg" style="color: ${riskColor}">${riskText}</strong>
            </div>
            <div class="text-sm opacity-90">
                <span class="font-semibold">Fraud Probability:</span> 
                <strong class="text-lg">${probPercent}%</strong>
            </div>
        `;
    }
    
    // Update progress bars with animation
    setTimeout(() => {
        const probBar = document.getElementById('fraud-probability-bar');
        const confBar = document.getElementById('confidence-bar');
        if (probBar) {
            probBar.style.width = `${probability * 100}%`;
        }
        if (confBar) {
            confBar.style.width = `${result.confidence * 100}%`;
        }
    }, 100);
    
    // Update metrics with animation
    animateValue(fraudProbability, 0, probability * 100, 1000, '%');
    animateValue(confidence, 0, result.confidence * 100, 1000, '%');
    animateValue(responseTime, 0, result.response_time_ms, 1000, ' ms');
    
    // Update chart with risk level
    updateChart(probability, result.confidence, riskLevel);
    updateRiskGauge(probability, riskLevel);
    
    // Update detailed info with 3D card effect - show only relevant features
    detailedInfo.innerHTML = `
        <div class="group relative bg-white p-5 rounded-xl border-l-4 border-indigo-500 shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-r from-indigo-500/0 to-indigo-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <label class="text-xs text-gray-500 block mb-2 font-semibold">Transaction Amount</label>
            <value class="text-lg font-bold text-gray-800 relative z-10">$${transaction.transaction_amount.toFixed(2)}</value>
        </div>
        <div class="group relative bg-white p-5 rounded-xl border-l-4 border-indigo-500 shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-r from-indigo-500/0 to-indigo-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <label class="text-xs text-gray-500 block mb-2 font-semibold">Avg Transaction Amount (7d)</label>
            <value class="text-lg font-bold text-gray-800 relative z-10">$${transaction.avg_transaction_amount_7d.toFixed(2)}</value>
        </div>
        <div class="group relative bg-white p-5 rounded-xl border-l-4 border-red-500 shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-r from-red-500/0 to-red-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <label class="text-xs text-gray-500 block mb-2 font-semibold">Failed Transactions (7d)</label>
            <value class="text-lg font-bold text-red-600 relative z-10">${transaction.failed_transaction_count_7d}</value>
        </div>
        <div class="group relative bg-white p-5 rounded-xl border-l-4 border-indigo-500 shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-r from-indigo-500/0 to-indigo-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <label class="text-xs text-gray-500 block mb-2 font-semibold">Daily Transaction Count</label>
            <value class="text-lg font-bold text-gray-800 relative z-10">${transaction.daily_transaction_count}</value>
        </div>
        <div class="group relative bg-white p-5 rounded-xl border-l-4 border-orange-500 shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-r from-orange-500/0 to-orange-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <label class="text-xs text-gray-500 block mb-2 font-semibold">Risk Score</label>
            <value class="text-lg font-bold text-orange-600 relative z-10">${(transaction.risk_score * 100).toFixed(2)}%</value>
        </div>
        <div class="group relative bg-white p-5 rounded-xl border-l-4 border-indigo-500 shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-r from-indigo-500/0 to-indigo-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <label class="text-xs text-gray-500 block mb-2 font-semibold">Card Age</label>
            <value class="text-lg font-bold text-gray-800 relative z-10">${transaction.card_age} days</value>
        </div>
        <div class="group relative bg-white p-5 rounded-xl border-l-4 border-green-500 shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-r from-green-500/0 to-green-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <label class="text-xs text-gray-500 block mb-2 font-semibold">High Failure Flag</label>
            <value class="text-lg font-bold text-green-600 relative z-10">${transaction.high_failure_flag}</value>
        </div>
        <div class="group relative bg-white p-5 rounded-xl border-l-4 border-green-500 shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-r from-green-500/0 to-green-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <label class="text-xs text-gray-500 block mb-2 font-semibold">Failure Rate</label>
            <value class="text-lg font-bold text-green-600 relative z-10">${(transaction.failure_rate * 100).toFixed(2)}%</value>
        </div>
        <div class="group relative bg-white p-5 rounded-xl border-l-4 border-green-500 shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-r from-green-500/0 to-green-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <label class="text-xs text-gray-500 block mb-2 font-semibold">Amount Deviation</label>
            <value class="text-lg font-bold text-green-600 relative z-10">$${transaction.amount_deviation.toFixed(2)}</value>
        </div>
        <div class="group relative bg-white p-5 rounded-xl border-l-4 border-green-500 shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-r from-green-500/0 to-green-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <label class="text-xs text-gray-500 block mb-2 font-semibold">Risk-Amount Interaction</label>
            <value class="text-lg font-bold text-green-600 relative z-10">${transaction.risk_amount_interaction.toFixed(2)}</value>
        </div>
        <div class="group relative bg-white p-5 rounded-xl border-l-4 border-indigo-500 shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-r from-indigo-500/0 to-indigo-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <label class="text-xs text-gray-500 block mb-2 font-semibold">Hour</label>
            <value class="text-lg font-bold text-gray-800 relative z-10">${transaction.hour}</value>
        </div>
        <div class="group relative bg-white p-5 rounded-xl border-l-4 border-indigo-500 shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1">
            <div class="absolute inset-0 bg-gradient-to-r from-indigo-500/0 to-indigo-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <label class="text-xs text-gray-500 block mb-2 font-semibold">Month</label>
            <value class="text-lg font-bold text-gray-800 relative z-10">${transaction.month}</value>
        </div>
    `;
}

// Animate value counter
function animateValue(element, start, end, duration, suffix = '') {
    if (!element) return;
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = progress * (end - start) + start;
        element.textContent = value.toFixed(2) + suffix;
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Update chart
function updateChart(probability, confidence, riskLevel = 'low') {
    const ctx = document.getElementById('fraud-chart');
    if (!ctx) return;
    
    const safeProbability = 1 - probability;
    
    // Determine colors based on risk level
    let fraudColor = '#ef4444';
    if (riskLevel === 'medium') {
        fraudColor = '#f59e0b';
    } else if (riskLevel === 'low') {
        fraudColor = '#10b981';
    }
    
    if (fraudChart) {
        fraudChart.destroy();
    }
    
    fraudChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Safe', 'Fraud Risk'],
            datasets: [{
                data: [safeProbability * 100, probability * 100],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    fraudColor + '80'
                ],
                borderWidth: 0,
                borderColor: '#ffffff',
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '75%',
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1500
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            size: 14,
                            weight: '600',
                            family: 'Inter'
                        },
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed.toFixed(2)}%`;
                        }
                    },
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    padding: 15,
                    titleFont: {
                        size: 16,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 14
                    },
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    cornerRadius: 12
                }
            }
        },
        plugins: [{
            id: 'centerText',
            beforeDraw: function(chart) {
                const ctx = chart.ctx;
                const centerX = chart.chartArea.left + (chart.chartArea.right - chart.chartArea.left) / 2;
                const centerY = chart.chartArea.top + (chart.chartArea.bottom - chart.chartArea.top) / 2;
                
                ctx.save();
                ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
                ctx.shadowBlur = 10;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 2;
                
                ctx.font = 'bold 32px Inter, sans-serif';
                ctx.fillStyle = '#1e293b';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(`${(probability * 100).toFixed(1)}%`, centerX, centerY - 15);
                
                ctx.font = '600 16px Inter, sans-serif';
                ctx.fillStyle = '#64748b';
                ctx.fillText('Fraud Risk', centerX, centerY + 15);
                ctx.restore();
            }
        }]
    });
}

// Update Risk Gauge Chart
let riskGaugeChart = null;
function updateRiskGauge(probability, riskLevel) {
    const ctx = document.getElementById('risk-gauge-chart');
    if (!ctx) return;
    
    if (riskGaugeChart) {
        riskGaugeChart.destroy();
    }
    
    const angle = Math.PI + (probability * Math.PI);
    const radius = 100;
    const centerX = ctx.width / 2;
    const centerY = ctx.height / 2 + 20;
    
    riskGaugeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [probability * 100, (1 - probability) * 100],
                backgroundColor: [
                    probability >= 0.7 ? '#ef4444' : probability >= 0.4 ? '#f59e0b' : '#10b981',
                    '#e5e7eb'
                ],
                borderWidth: 0,
                circumference: 180,
                rotation: 270
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '70%',
            animation: {
                animateRotate: true,
                duration: 1500
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        },
        plugins: [{
            id: 'gaugeText',
            beforeDraw: function(chart) {
                const ctx = chart.ctx;
                const centerX = chart.chartArea.left + (chart.chartArea.right - chart.chartArea.left) / 2;
                const centerY = chart.chartArea.top + (chart.chartArea.bottom - chart.chartArea.top) / 2 + 30;
                
                ctx.save();
                ctx.font = 'bold 36px Inter, sans-serif';
                ctx.fillStyle = probability >= 0.7 ? '#ef4444' : probability >= 0.4 ? '#f59e0b' : '#10b981';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(`${(probability * 100).toFixed(0)}%`, centerX, centerY);
                
                ctx.font = '600 14px Inter, sans-serif';
                ctx.fillStyle = '#64748b';
                ctx.fillText(riskLevel.toUpperCase() + ' RISK', centerX, centerY + 30);
                ctx.restore();
            }
        }]
    });
}

// Fill sample data
function fillSampleData() {
    document.getElementById('transaction_amount').value = '150.50';
    document.getElementById('avg_transaction_amount_7d').value = '120.30';
    document.getElementById('failed_transaction_count_7d').value = '0.0';
    document.getElementById('daily_transaction_count').value = '5';
    document.getElementById('risk_score').value = '0.15';
    document.getElementById('risk_score_slider').value = '0.15';
    document.getElementById('card_age').value = '365';
    // Leave hour and month empty to use current time
    
    showToast('Sample data filled!', 'success');
}

// Close results
function closeResults() {
    const resultsCard = document.getElementById('results-card');
    if (resultsCard) {
        resultsCard.style.display = 'none';
    }
}

// Show single mode
function showSingleMode() {
    const batchMode = document.getElementById('batch-mode');
    const singleMode = document.getElementById('single-mode');
    if (batchMode) batchMode.style.display = 'none';
    if (singleMode) singleMode.style.display = 'block';
}

// Show batch mode
function showBatchMode() {
    const singleMode = document.getElementById('single-mode');
    const batchMode = document.getElementById('batch-mode');
    if (singleMode) singleMode.style.display = 'none';
    if (batchMode) batchMode.style.display = 'block';
}

// Show batch form
function showBatchForm() {
    showToast('Batch form feature coming soon!', 'info');
}

// Handle CSV upload
function handleCSVUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    showToast('CSV upload feature coming soon!', 'info');
    // TODO: Implement CSV parsing and batch prediction
}

// Show history
function showHistory() {
    if (predictionHistory.length === 0) {
        showToast('No prediction history yet. Analyze some transactions first!', 'info');
        return;
    }
    
    // Create history modal
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black/70 flex items-center justify-center z-50 opacity-0 transition-opacity';
    modal.innerHTML = `
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[80vh] flex flex-col transform scale-95 transition-transform">
            <div class="flex justify-between items-center p-6 border-b border-gray-200">
                <h2 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
                    <i class="fas fa-history text-indigo-600"></i> Prediction History
                </h2>
                <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-gray-600 transition-colors">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>
            <div class="p-6 overflow-y-auto flex-1">
                ${predictionHistory.slice().reverse().map((item, index) => {
                    const date = new Date(item.timestamp).toLocaleString();
                    const prob = (item.result.fraud_probability * 100).toFixed(2);
                    const borderColor = item.result.is_fraud ? 'border-red-500' : 'border-green-500';
                    const textColor = item.result.is_fraud ? 'text-red-600' : 'text-green-600';
                    return `
                        <div class="bg-gray-50 p-4 rounded-lg mb-4 border-l-4 ${borderColor} hover:shadow-md transition-shadow">
                            <div class="flex justify-between items-center mb-3">
                                <div class="flex items-center gap-2 ${textColor} font-bold">
                                    <i class="fas ${item.result.is_fraud ? 'fa-exclamation-triangle' : 'fa-check-circle'}"></i>
                                    <span>${item.result.is_fraud ? 'FRAUD' : 'SAFE'}</span>
                                </div>
                                <div class="text-sm text-gray-500">${date}</div>
                            </div>
                            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div>
                                    <label class="text-xs text-gray-500 block mb-1">Amount:</label>
                                    <value class="text-sm font-semibold text-gray-800">$${item.transaction.transaction_amount.toFixed(2)}</value>
                                </div>
                                <div>
                                    <label class="text-xs text-gray-500 block mb-1">Risk Score:</label>
                                    <value class="text-sm font-semibold text-gray-800">${(item.transaction.risk_score * 100).toFixed(1)}%</value>
                                </div>
                                <div>
                                    <label class="text-xs text-gray-500 block mb-1">Fraud Probability:</label>
                                    <value class="text-sm font-semibold ${prob > 50 ? 'text-red-600' : 'text-green-600'}">${prob}%</value>
                                </div>
                                <div>
                                    <label class="text-xs text-gray-500 block mb-1">Card Age:</label>
                                    <value class="text-sm font-semibold text-gray-800">${item.transaction.card_age} days</value>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
            <div class="p-6 border-t border-gray-200 flex justify-end gap-3">
                <button onclick="clearHistory()" class="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition-all">
                    <i class="fas fa-trash"></i> Clear History
                </button>
                <button onclick="this.closest('.fixed').remove()" class="gradient-primary text-white px-6 py-2 rounded-lg font-semibold hover:shadow-lg transition-all">
                    Close
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    setTimeout(() => {
        modal.classList.remove('opacity-0', 'scale-95');
        modal.classList.add('opacity-100');
        modal.querySelector('.bg-white').classList.remove('scale-95');
        modal.querySelector('.bg-white').classList.add('scale-100');
    }, 10);
}

// Clear history
function clearHistory() {
    if (confirm('Are you sure you want to clear all prediction history?')) {
        predictionHistory = [];
        showToast('History cleared!', 'success');
        document.querySelector('.fixed.inset-0').remove();
    }
}

// Loading overlay
function showLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    } else {
        console.warn('Loading overlay element not found');
    }
}

function hideLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

// Toast notifications
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    
    const bgColors = {
        'success': 'bg-green-500',
        'error': 'bg-red-500',
        'info': 'bg-blue-500'
    };
    
    toast.className = `${bgColors[type] || bgColors.success} text-white px-6 py-4 rounded-lg shadow-xl flex items-center gap-3 min-w-[300px] transform translate-x-full transition-transform duration-300`;
    
    const icon = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
    
    toast.innerHTML = `
        <i class="fas ${icon} text-xl"></i>
        <span class="font-semibold">${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
        toast.classList.add('translate-x-0');
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('translate-x-0');
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            if (container.contains(toast)) {
                container.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

