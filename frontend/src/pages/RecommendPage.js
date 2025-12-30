import React, { useState } from 'react';
import '../styles/RecommendPage.css';
import { FaSeedling, FaSearch, FaCheckCircle, FaTimesCircle, FaSpinner, FaTrophy } from 'react-icons/fa';
import axios from 'axios';

function RecommendPage() {
  const [customerId, setCustomerId] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searched, setSearched] = useState(false);

  const handleGetRecommendations = async (e) => {
    e.preventDefault();
    
    if (!customerId.trim()) {
      setError('Please enter a customer ID');
      return;
    }

    setLoading(true);
    setError('');
    setRecommendations([]);
    setSearched(false);

    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/api/recommend/${customerId}/`
      );
      
      if (response.data.recommendations && response.data.recommendations.length > 0) {
        setRecommendations(response.data.recommendations);
      } else {
        setRecommendations([]);
        setError('No recommendations found for this customer. Please ensure models are trained first.');
      }
      setSearched(true);
    } catch (err) {
      setError('❌ Error fetching recommendations: ' + (err.response?.data?.error || err.message));
      setSearched(true);
      console.error('Recommendation error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="recommend-page">
      <div className="recommend-container">
        <div className="recommend-header">
          <FaSeedling className="recommend-icon" />
          <h1>Smart Recommendations</h1>
          <p>Get AI-powered product recommendations for any customer</p>
        </div>

        <div className="recommend-card">
          <form className="search-form" onSubmit={handleGetRecommendations}>
            <div className="input-group">
              <input
                type="text"
                placeholder="Enter Customer ID (e.g., CUST001, C123, etc.)"
                value={customerId}
                onChange={(e) => setCustomerId(e.target.value)}
                className="customer-input"
              />
              <button type="submit" className="search-button" disabled={loading}>
                {loading ? (
                  <>
                    <FaSpinner className="spinner" />
                    Searching...
                  </>
                ) : (
                  <>
                    <FaSearch />
                    Get Recommendations
                  </>
                )}
              </button>
            </div>
          </form>

          {error && (
            <div className="message error-message">
              <FaTimesCircle className="message-icon" />
              <div>
                <h4>Error</h4>
                <p>{error}</p>
              </div>
            </div>
          )}

          {searched && recommendations.length === 0 && !error && (
            <div className="message info-message">
              <FaCheckCircle className="message-icon" />
              <div>
                <h4>No Recommendations</h4>
                <p>This customer has no surplus product predictions at this time.</p>
              </div>
            </div>
          )}

          {recommendations.length > 0 && (
            <section className="results">
              <div className="results-header">
                <FaTrophy className="trophy-icon" />
                <h2>Top Recommendations for Customer {customerId}</h2>
                <p>{recommendations.length} product(s) recommended</p>
              </div>

              <div className="recommendations-grid">
                {recommendations.map((rec, index) => (
                  <div key={index} className="recommendation-card">
                    <div className="rec-rank">#{index + 1}</div>
                    
                    <div className="rec-content">
                      <h3 className="rec-product">{rec.product_id}</h3>
                      
                      <div className="rec-details">
                        <div className="detail">
                          <span className="label">Predicted Quantity:</span>
                          <span className="value">{rec.predicted_quantity.toFixed(2)} units</span>
                        </div>
                        
                        <div className="detail">
                          <span className="label">Confidence:</span>
                          <span className="value">{(rec.predicted_quantity * 10).toFixed(1)}%</span>
                        </div>
                        
                        <div className="detail">
                          <span className="label">Surplus Flag:</span>
                          <span className={`value ${rec.surplus_flag ? 'surplus' : 'normal'}`}>
                            {rec.surplus_flag ? '⚠️ Has Surplus' : '✅ Normal'}
                          </span>
                        </div>

                        {rec.recommendation_reason && (
                          <div className="detail full-width">
                            <span className="label">Reason:</span>
                            <span className="value">{rec.recommendation_reason}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="insights">
                <h3>📊 Insights</h3>
                <ul>
                  <li>Total recommendations: {recommendations.length} products</li>
                  <li>Surplus products: {recommendations.filter(r => r.surplus_flag).length}</li>
                  <li>Average predicted quantity: {(recommendations.reduce((sum, r) => sum + r.predicted_quantity, 0) / recommendations.length).toFixed(2)} units</li>
                </ul>
              </div>
            </section>
          )}

          {!searched && recommendations.length === 0 && !error && (
            <section className="empty-state">
              <FaSeedling className="empty-icon" />
              <h3>Ready to Get Recommendations?</h3>
              <p>Enter a customer ID above and click "Get Recommendations" to see AI-powered suggestions.</p>
              <div className="tip">
                <strong>💡 Tip:</strong> Make sure to train the models first from the "Train Models" page.
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}

export default RecommendPage;
