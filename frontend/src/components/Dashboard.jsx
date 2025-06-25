import React from 'react';
import './Dashboard.css';
import PortfolioAllocation from './PortfolioAllocation';
import Chatbot from './Chatbot';
import SectorAllocation from './SectorAllocation';
import LiveMarketNews from './LiveMarketNews';

const Dashboard = () => {
  return (
    <div className="dashboard-container">
      <div className="dashboard-grid">
        <div className="grid-item">
          <PortfolioAllocation />
        </div>
        <div className="grid-item">
          <Chatbot />
        </div>
        <div className="grid-item right-column-container">
          <div className="right-column">
            <div className="card-top">
              <SectorAllocation />
            </div>
            <div className="card-bottom">
              <LiveMarketNews />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 