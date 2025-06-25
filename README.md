# Zerodha 2.0 - Automated Stock Portfolio Dashboard

A full-stack application that enhances the Zerodha trading experience with automated portfolio management, real-time news analysis, and an AI-powered chatbot.

## Features

- **Portfolio Analytics**: Real-time tracking and visualization of stock holdings
- **Automated News Analysis**: Live news fetching and sentiment analysis for portfolio stocks
- **Sector Allocation**: Visual breakdown of portfolio by sectors
- **AI Chatbot**: Intelligent assistant for portfolio queries using SQL and web search capabilities
- **React Agent**: Automated reasoning and action system for portfolio management

## Tech Stack

### Frontend
- React.js
- Modern UI components
- Real-time data visualization
- Responsive design

### Backend
- Python FastAPI
- LangChain for AI/ML operations
- Google Gemini API for natural language processing
- SQLite database for portfolio data
- Zerodha API integration

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 14+
- Zerodha trading account
- API keys for:
  - Zerodha
  - Google Gemini
  - Tavily Search
  - Financial Modeling Prep (FMP)

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `secrets.env` file with your API keys:
   ```env
   ZERODHA_API_KEY=your_key
   ZERODHA_API_SECRET=your_secret
   GEMINI_API_KEY=your_key
   TAVILY_API_KEY=your_key
   FMP_API_KEY=your_key
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Running the Application

1. Start the backend server:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. In a new terminal, start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Access the application at `http://localhost:5173`

## Security Note
- Never commit your `secrets.env` file
- Keep your API keys confidential
- Use environment variables in production

## Contributing
Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT License - see the [LICENSE](LICENSE) file for details 