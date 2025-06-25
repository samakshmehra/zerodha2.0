import React from 'react';
import './Login.css';
import dashboardIcon from '../assets/unnamed.png';

const Login = () => {
  const handleLogin = async () => {
    try {
      const response = await fetch(`http://${window.location.hostname}:8000/`);
      if (response.ok) {
        const data = await response.json();
        if (data.login_url) {
          window.location.href = data.login_url;
        } else {
          alert('Error: Login URL not found in the response from the server.');
        }
      } else {
        alert('Error: Could not connect to the backend server. Please make sure it is running.');
      }
    } catch (error) {
      console.error('Failed to fetch login URL:', error);
      alert('An error occurred while trying to log in. Check the console for details.');
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-left">
          <div className="login-header">
            <img src={dashboardIcon} alt="Dashboard Icon" className="login-icon" />
            <h1>Zerodha Portfolio Dashboard</h1>
          </div>
          <p>
            Connect your Zerodha account to unlock powerful portfolio analytics and AI-driven
            insights.
          </p>
          <button onClick={handleLogin} className="login-button">
            Login with Zerodha
          </button>
        </div>
        <div className="login-right">
          <h2>
            <span role="img" aria-label="sparkles">
              ✨
            </span>{' '}
            Key Features
          </h2>
          <ul>
            <li>
              <span className="checkmark">✓</span>
              Interactive AI Chatbot for Portfolio Questions
            </li>
            <li>
              <span className="checkmark">✓</span>
              Dynamic Portfolio & Sector Allocations
            </li>
            <li>
              <span className="checkmark">✓</span>
              Live News Summaries for Your Top Stocks
            </li>
            <li>
              <span className="checkmark">✓</span>
              AI-Powered Sentiment Analysis on News
            </li>
            <li>
              <span className="checkmark">✓</span>
              Secure Connection via Kite Connect API
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Login; 