import React, { useState } from 'react';
import '../styles/TrainPage.css';
import { FaBrain, FaCheckCircle, FaTimesCircle, FaSpinner } from 'react-icons/fa';
import axios from 'axios';

function TrainPage() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [trainProgress, setTrainProgress] = useState(0);

  const handleTrain = async () => {
    setLoading(true);
    setMessage('');
    setError('');
    setTrainProgress(0);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setTrainProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + Math.random() * 30;
        });
      }, 300);

      const response = await axios.post('http://127.0.0.1:8000/api/train/');
      
      clearInterval(progressInterval);
      setTrainProgress(100);
      setMessage('✅ Models trained successfully! Your AI models are ready to make recommendations.');
      
      setTimeout(() => {
        setTrainProgress(0);
      }, 2000);
    } catch (err) {
      setError('❌ Error training models: ' + (err.response?.data?.error || err.message));
      console.error('Training error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="train-page">
      <div className="train-container">
        <div className="train-header">
          <FaBrain className="train-icon" />
          <h1>Train AI Models</h1>
          <p>Initialize and train machine learning models on your agricultural data</p>
        </div>

        <div className="train-card">
          <section className="train-info">
            <h2>Model Training Process</h2>
            <div className="info-steps">
              <div className="info-step">
                <div className="step-num">📊</div>
                <div>
                  <h4>Data Generation</h4>
                  <p>Generates dummy agricultural transaction data</p>
                </div>
              </div>
              <div className="info-step">
                <div className="step-num">🔧</div>
                <div>
                  <h4>Data Preprocessing</h4>
                  <p>Cleans and processes data for 7-day and 14-day windows</p>
                </div>
              </div>
              <div className="info-step">
                <div className="step-num">🤖</div>
                <div>
                  <h4>Model Training</h4>
                  <p>Trains classification and regression models</p>
                </div>
              </div>
              <div className="info-step">
                <div className="step-num">💾</div>
                <div>
                  <h4>Model Persistence</h4>
                  <p>Saves trained models for future predictions</p>
                </div>
              </div>
            </div>
          </section>

          <section className="train-control">
            <button
              className={`train-button ${loading ? 'loading' : ''}`}
              onClick={handleTrain}
              disabled={loading}
            >
              {loading ? (
                <>
                  <FaSpinner className="spinner" />
                  Training Models...
                </>
              ) : (
                <>
                  <FaBrain />
                  Train Models Now
                </>
              )}
            </button>

            {trainProgress > 0 && (
              <div className="progress-container">
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${trainProgress}%` }}>
                    {trainProgress.toFixed(0)}%
                  </div>
                </div>
              </div>
            )}

            {message && (
              <div className="message success-message">
                <FaCheckCircle className="message-icon" />
                <div>
                  <h4>Success!</h4>
                  <p>{message}</p>
                </div>
              </div>
            )}

            {error && (
              <div className="message error-message">
                <FaTimesCircle className="message-icon" />
                <div>
                  <h4>Error</h4>
                  <p>{error}</p>
                </div>
              </div>
            )}
          </section>

          <section className="training-details">
            <h3>What Gets Trained?</h3>
            <div className="details-grid">
              <div className="detail-item">
                <strong>Classification Models</strong>
                <p>Predicts product surplus likelihood</p>
              </div>
              <div className="detail-item">
                <strong>Regression Models</strong>
                <p>Estimates quantity surplus values</p>
              </div>
              <div className="detail-item">
                <strong>Time Windows</strong>
                <p>7-day and 14-day analysis periods</p>
              </div>
              <div className="detail-item">
                <strong>Feature Engineering</strong>
                <p>Automated feature extraction from raw data</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

export default TrainPage;
