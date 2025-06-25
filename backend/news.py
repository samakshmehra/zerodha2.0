import os
import sqlite3
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import TavilySearchResults
import json

# Load secrets from .env file
load_dotenv(dotenv_path="secrets.env")

# Initialize the LLM and the search tool
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)
search_tool = TavilySearchResults(search_depth="advanced", max_results=3)

def get_top_holdings_news():
    """
    Fetches the top 5 stock holdings, gets the top news article for them from moneycontrol.com,
    summarizes the article, and determines the sentiment (Positive, Negative, or Neutral).
    """
    try:
        # 1. Connect to the database and get top 5 holdings by total_value
        conn = sqlite3.connect("zerodha_holdings.db")
        cur = conn.cursor()
        cur.execute("SELECT tradingsymbol, companyName FROM holdings_with_sector ORDER BY total_value DESC LIMIT 5")
        top_stocks = cur.fetchall()
        conn.close()

        if not top_stocks:
            return {"error": "No holdings found in the database."}

        # 2. Prepare the prompt for the LLM. This is now for a single article.
        prompt_template = """
        Based on the content of the following news article for {company_name} ({trading_symbol}) from moneycontrol.com, please do the following:
        1. Summarize the key news in a single, concise paragraph.
        2. Determine the sentiment of the news as 'Positive', 'Negative', or 'Neutral'.
        3. Provide a brief one-sentence justification for your sentiment analysis.

        News Article Content:
        {news_article_content}

        Provide the output in a valid JSON format with three keys: "summary", "sentiment", and "justification".
        Do not include any other text or markdown formatting like ```json.
        """

        all_news = []
        # Re-initialize the tool here to ensure max_results is set for this specific use case
        search_tool = TavilySearchResults(max_results=1)

        # 3. For each stock, search for news and process it with the LLM
        for symbol, company in top_stocks:
            print(f"Fetching top news for {company} ({symbol})...")
            
            # Use a more robust search query
            search_query = f'latest news for "{company}" moneycontrol.com'
            try:
                # Use .invoke() which is more standard and reliable. It returns a list of dicts.
                search_results = search_tool.invoke(search_query)
                
                if not search_results or not isinstance(search_results, list) or len(search_results) == 0:
                    print(f"No search results found for {symbol}.")
                    continue

                # We only care about the top result
                top_result = search_results[0]
                article_content = top_result.get("content")
                article_url = top_result.get("url")

                if not article_content:
                    print(f"Top result for {symbol} has no content.")
                    continue

                # Format the prompt with the content of the single top article
                prompt = prompt_template.format(
                    company_name=company,
                    trading_symbol=symbol,
                    news_article_content=article_content
                )
                
                # Get the structured response from the LLM
                response = llm.invoke(prompt)
                
                # Clean and parse the JSON response
                cleaned_response = response.content.strip().replace('```json', '').replace('```', '')
                news_data = json.loads(cleaned_response)

                all_news.append({
                    "stock": symbol,
                    "company": company,
                    "summary": news_data.get("summary", "No summary available."),
                    "sentiment": news_data.get("sentiment", "Neutral"),
                    "justification": news_data.get("justification", ""),
                    "url": article_url
                })

            except json.JSONDecodeError as e:
                print(f"Could not parse LLM response for {symbol}: {e}. Skipping.")
                continue
            except Exception as e:
                print(f"An error occurred while processing {symbol}: {e}")
                continue

        return all_news

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {"error": f"Database error: {e}"}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": f"An unexpected error occurred: {e}"}

# For direct testing of this script
if __name__ == "__main__":
    news_summary = get_top_holdings_news()
    print("\n--- News Summary ---")
    print(json.dumps(news_summary, indent=2))