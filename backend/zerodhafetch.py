from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from kiteconnect import KiteConnect
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import os
import requests
from pathlib import Path
from Chatbot import get_chatbot_response
from news import get_top_holdings_news

# Load secrets from .env
load_dotenv(dotenv_path=Path(__file__).parent / "secrets.env")
Z_API_KEY = os.getenv("ZERODHA_API_KEY")
Z_API_SECRET = os.getenv("ZERODHA_API_SECRET")
FMP_API_KEY = os.getenv("FMP_API_KEY")

# Init
app = FastAPI()
kite = KiteConnect(api_key=Z_API_KEY)
DB_PATH = "zerodha_holdings.db"
engine = create_engine(f"sqlite:///{DB_PATH}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_and_save_data(holdings_data: list):
    """
    This function runs in the background. It takes the holdings data,
    fetches sector information from an external API, merges the data,
    and saves it to the database. This is the time-consuming part.
    """
    try:
        # Step 2 (cont.): Process holdings
        df = pd.DataFrame(holdings_data)
        if df.empty:
            print("Background task: No holdings data to process.")
            return

        df['total_quantity'] = df['opening_quantity']
        df = df[['tradingsymbol', 'average_price', 'day_change', 'day_change_percentage', 'pnl', 'total_quantity']]

        # Step 3: Fetch NSE Sector Data (SLOW part)
        url = "https://financialmodelingprep.com/api/v3/stock-screener"
        params = {"exchange": "NSE", "limit": 5000, "apikey": FMP_API_KEY}
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        sector_data = response.json()

        fieldnames = ["symbol", "sector", "industry", "marketCap", "companyName", "volume", "price"]
        filtered_data = [{field: item.get(field) for field in fieldnames} for item in sector_data]
        sector_df = pd.DataFrame(filtered_data)
        sector_df['clean_symbol'] = sector_df['symbol'].str.replace('.NS', '', regex=False)

        # Step 4: Merge in memory
        merged_df = pd.merge(
            df,
            sector_df,
            left_on="tradingsymbol",
            right_on="clean_symbol",
            how="inner"
        )
        merged_df['total_value'] = merged_df['price'].astype(float) * merged_df['total_quantity'].astype(float)
        merged_df.drop(columns=['symbol', 'clean_symbol'], inplace=True)
        numeric_cols = merged_df.select_dtypes(include=['float64', 'int64']).columns
        merged_df[numeric_cols] = merged_df[numeric_cols].round(2)

        # Step 5: Save only merged data to DB
        merged_df.to_sql("holdings_with_sector", engine, if_exists="replace", index=False)
        print("Background task: Data processing and saving complete.")

    except Exception as e:
        # Log errors from the background task
        print(f"Error in background task: {e}")

@app.get("/")
def login_url():
    return {"login_url": kite.login_url()}

@app.get("/callback")
async def callback(request: Request, background_tasks: BackgroundTasks):
    try:
        # Step 1: Zerodha login
        token = request.query_params["request_token"]
        session = kite.generate_session(token, api_secret=Z_API_SECRET)
        kite.set_access_token(session["access_token"])

        # Step 2: Fetch Zerodha Holdings (Fast)
        holdings = kite.holdings()

        # Add the slow data processing task to run in the background
        background_tasks.add_task(process_and_save_data, holdings)

        # Step 3: Redirect IMMEDIATELY back to the frontend app
        return RedirectResponse(url=f"http://localhost:5173/?request_token={token}")

    except Exception as e:
        # Redirect with an error message if something goes wrong during login
        return RedirectResponse(url=f"http://localhost:5173/?error={str(e)}")

@app.get("/holdings")
def get_holdings():
    try:
        with engine.connect() as connection:
            df = pd.read_sql("SELECT * FROM holdings_with_sector", connection)
            # Calculate portfolio percentage
            total_portfolio_value = df['total_value'].sum()
            df['percentage'] = round((df['total_value'] / total_portfolio_value) * 100, 2)
            return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@app.get("/sector-allocation")
def get_sector_allocation():
    try:
        with engine.connect() as connection:
            df = pd.read_sql("SELECT sector, SUM(total_value) as total_value FROM holdings_with_sector GROUP BY sector", connection)
            total_portfolio_value = df['total_value'].sum()
            df['percentage'] = round((df['total_value'] / total_portfolio_value) * 100, 2)
            return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@app.get("/market-news")
def get_market_news():
    """
    Endpoint to fetch, summarize, and analyze news for the top 5 stock holdings.
    """
    try:
        news_data = get_top_holdings_news()
        return news_data
    except Exception as e:
        # This will catch any unexpected errors from the news function
        return {"error": f"Failed to fetch market news: {str(e)}"}

@app.post("/chatbot")
async def chatbot_endpoint(request: Request):
    """
    Chatbot endpoint that accepts user messages and returns AI responses
    """
    try:
        # Parse the request body
        body = await request.json()
        user_message = body.get("message", "")
        chat_history = body.get("history", [])  # Get history from request
        
        if not user_message:
            return {"error": "No message provided"}
        
        # Get response from chatbot, passing the history
        response = get_chatbot_response(user_message, chat_history)
        
        return {
            "response": response,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": f"Error processing request: {str(e)}",
            "status": "error"
        }

