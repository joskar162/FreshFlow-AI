import React, { useEffect, useState } from 'react';
import '../styles/HomePage.css';
import { FaBrain, FaChartLine, FaLeaf, FaArrowRight, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';
import axios from 'axios';

function HomePage() {
  const [topProducts, setTopProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);
        const res = await axios.get('http://127.0.0.1:8000/api/dashboard/');
        setTopProducts(res.data.top_products || []);
      } catch (err) {
        setError('Failed to load dashboard: ' + (err.response?.data?.error || err.message));
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);
  return (
    <div className="home-page">
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            🌾 Welcome to <span className="highlight">HarvestIQ</span>
          </h1>
          <p className="hero-subtitle">
            AI-Powered Agricultural Recommendations for Optimal Harvest Management
          </p>
          <p className="hero-description">
            Leverage machine learning to predict product surpluses and get intelligent recommendations for your harvest operations.
          </p>
        </div>
      </section>

      <section className="features">
        <h2>Why HarvestIQ?</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <FaBrain />
            </div>
            <h3>Advanced ML Models</h3>
            <p>State-of-the-art machine learning algorithms trained on real agricultural data to predict surpluses accurately.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <FaChartLine />
            </div>
            <h3>Data-Driven Insights</h3>
            <p>Analyze purchase patterns over 7 and 14 days to get actionable insights for your operations.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <FaLeaf />
            </div>
            <h3>Smart Recommendations</h3>
            <p>Get personalized product recommendations based on customer ID and historical data patterns.</p>
          </div>
        </div>
      </section>

      <section className="quick-start">
        <h2>Current High-Demand Products (7-day forecast)</h2>
        {loading && <p>Loading demand data...</p>}
        {error && <p className="error">{error}</p>}
        {!loading && !error && (
          <div className="demand-grid">
            {topProducts.length === 0 && <p>No demand data available.</p>}
            {topProducts.map((p) => (
              <div key={p.product_id} className="demand-card">
                <h3>{p.product_id}</h3>
                <p>Expected demand (7d): <strong>{p.expected_quantity_7d.toFixed(2)}</strong></p>
                <p>Stock: <strong>{p.stock_qty === null ? 'unknown' : p.stock_qty}</strong></p>
                <p>Status: {p.stock_status === 'sufficient' ? (<span className="status enough"><FaCheckCircle /> Sufficient</span>) : p.stock_status === 'low' ? (<span className="status low"><FaExclamationTriangle /> Low</span>) : (<span className="status out"><FaExclamationTriangle /> Out / Unknown</span>)}</p>
              </div>
            ))}
          </div>
        )}
      </section>

     
      <section className="cta">
        <h2>Actionable Next Steps</h2>
        <p>The system automatically predicts demand for the next 7 days and highlights low-stock items so you can prioritize harvesting and distribution.</p>
      </section>
    </div>
  );
}

export default HomePage;
