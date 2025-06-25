import React, { useState, useEffect } from 'react';
import './LiveMarketNews.css';

const LiveMarketNews = () => {
  const [news, setNews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(`http://${window.location.hostname}:8000/market-news`);
        const data = await response.json();

        if (response.ok && Array.isArray(data)) {
          setNews(data);
        } else {
          // Handle cases where the API returns an error object
          throw new Error(data.error || 'Failed to fetch news.');
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchNews();
  }, []); // Runs once on component mount

  const getSentimentClass = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return 'sentiment-positive';
      case 'negative':
        return 'sentiment-negative';
      default:
        return 'sentiment-neutral';
    }
  };

  const renderContent = () => {
    if (isLoading) {
      return <p className="loading-message">Fetching latest market news...</p>;
    }

    if (error) {
      return <p className="error-message">Error: {error}</p>;
    }

    if (news.length === 0) {
      return <p>No news available for your top holdings at the moment.</p>;
    }

    return news.map((item, index) => (
      <div key={index} className="news-item">
        <div className="news-header">
          <h4 className="news-company">{item.company} ({item.stock})</h4>
          <span className={`news-sentiment ${getSentimentClass(item.sentiment)}`}>
            {item.sentiment}
          </span>
        </div>
        <p className="news-summary">{item.summary}</p>
        <div className="news-footer">
            <p className="news-justification">{item.justification}</p>
            {item.url && item.url.startsWith('http') && (
            <a href={item.url} target="_blank" rel="noopener noreferrer" className="news-link">
                Read More
            </a>
            )}
        </div>
      </div>
    ));
  };

  return (
    <div className="card live-market-news">
      <h2 className="card-title">Live Market News</h2>
      <div className="news-content">
        {renderContent()}
      </div>
    </div>
  );
};

export default LiveMarketNews; 