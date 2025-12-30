import React, { useState } from 'react';
import './App.css';
import HomePage from './pages/HomePage';
import RecommendPage from './pages/RecommendPage';
import { FaSeedling, FaRobot } from 'react-icons/fa';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage />;
      case 'recommend':
        return <RecommendPage />;
      default:
        return <HomePage />;
    }
  };

  return (
    <div className="app">
      <nav className="navbar">
        <div className="nav-container">
          <div className="logo" onClick={() => setCurrentPage('home')}>
            <FaSeedling className="logo-icon" />
            <h1>HarvestIQ</h1>
          </div>
          <ul className="nav-menu">
            <li>
              <button
                className={`nav-link ${currentPage === 'home' ? 'active' : ''}`}
                onClick={() => setCurrentPage('home')}
              >
                <FaRobot /> Home
              </button>
            </li>
            {/* train removed: models auto-train on backend */}
            <li>
              <button
                className={`nav-link ${currentPage === 'recommend' ? 'active' : ''}`}
                onClick={() => setCurrentPage('recommend')}
              >
                <FaSeedling /> Get Recommendations
              </button>
            </li>
          </ul>
        </div>
      </nav>

      <main className="main-content">
        {renderPage()}
      </main>

      <footer className="footer">
        <p>&copy; 2024 HarvestIQ. Powered by AI for Smart Agriculture.</p>
      </footer>
    </div>
  );
}

export default App;
