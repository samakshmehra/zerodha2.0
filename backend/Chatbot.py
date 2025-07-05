import os
import sqlite3
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain_community.tools import TavilySearchResults

# Load secrets
load_dotenv("secrets.env")

# SQL execution function
def execute_sql_query(sql_query: str) -> str:
    try:
        conn = sqlite3.connect("zerodha_holdings.db")
        cur = conn.cursor()
        cur.execute(sql_query)
        rows = cur.fetchall()
        if not rows:
            return "No data found."
        return "\n".join([str(row) for row in rows])
    except Exception as e:
        return f"SQL error: {e}"
    finally:
        conn.close()

# Tool that runs SQL queries
stock_tool = Tool(
    name="StockDataQuery",
    func=execute_sql_query,
    description=(
        "Use this tool to query the SQLite database. "
        "Main table: holdings_with_sector. It has these columns:\n"
        "- tradingsymbol: Stock symbol (e.g., TCS, INFY)\n"
        "- pnl: Profit or loss (in absolute ₹ value) on the current holdings\n"
        "- day_change: Daily price change in ₹\n"
        "- day_change_percentage: Daily price change in %\n"
        "- total_quantity: Total number of shares held\n"
        "- price: Current market price per share\n"
        "- average_price: Your average buy price per share\n"
        "- sector: Industry sector (e.g., Banking, IT)\n"
        "- industry: Specific industry group\n"
        "- companyName: Full company name\n"
        "- marketCap: Market capitalization of the company in ₹\n\n"
        "⚠️ IMPORTANT: For percentage profit calculations, use: (pnl / (total_quantity * average_price)) * 100\n"
        "⚠️ IMPORTANT: Always respond with plain SQL. Do NOT use markdown (like ```sql)."
    )
)

# Search tool for news and market information
search_tool = Tool(
    name="MarketSearch",
    func=TavilySearchResults(search_depth="advanced", max_results=3).run,
    description=(
        "Use this tool to find and summarize the latest financial news, market updates, and company information. "
        "After using this tool, you must synthesize the results into a concise summary for the user. "
        "Never tell the user to 'check links' or refer to a previous response; instead, provide the summary directly."
    )
)

# Advisory tool for financial advice and recommendations
advisory_tool = Tool(
    name="FinancialAdvisory",
    func=TavilySearchResults(search_depth="advanced", max_results=5).run,
    description=(
        "Use this tool to provide personalized financial advice for Indian consumers. "
        "When users ask for financial advice, investment recommendations, or product suggestions, "
        "FIRST ask them to share their profile details: "
        "1. Age (what's your age?) "
        "2. Annual income (what's your annual income in lakhs?) "
        "3. Financial goals (what are your financial goals - savings, insurance, investments, retirement?) "
        "4. Current investments (what financial products do you currently have?) "
        "5. Risk tolerance (are you conservative, moderate, or aggressive with investments?) "
        "Once they provide this information, then search for specific advice on Indian financial products: "
        "INSURANCE: Life Insurance (Term, Endowment, ULIP), Health Insurance, General Insurance (Motor, Home, Travel) "
        "INVESTMENTS: Mutual Funds (Equity, Debt, Hybrid), Fixed Deposits, PPF/EPF, NPS "
        "BANKING: Savings Accounts, Credit Cards, Personal Loans "
        "Provide specific product recommendations with Indian providers, current rates, and features based on their profile."
    )
)

# LLM setup with system prompt
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    # The system message is now part of the agent's prompt, not here.
)



def get_chatbot_response(user_message: str, chat_history: list = []) -> str:
    """
    Get a response from the chatbot for a user message, maintaining conversation history.
    """
    try:
        # 1. Setup memory with the chat history from the frontend
        memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True
        )
        for message in chat_history:
            if message.get('sender') == 'sent':
                memory.chat_memory.add_user_message(message.get('text', ''))
            elif message.get('sender') == 'received':
                memory.chat_memory.add_ai_message(message.get('text', ''))

        # 2. Initialize a conversational agent with memory
        agent = initialize_agent(
            tools=[stock_tool, search_tool, advisory_tool],
            llm=llm,
            agent="conversational-react-description",
            verbose=False,
            memory=memory,
            handle_parsing_errors="Check your output and make sure it conforms!",
            agent_kwargs={
                "system_message": (
                    "You are a helpful financial data assistant and advisor. "
                    "You can query portfolio data, provide market news, and offer financial advice. "
                    "When you use a tool, you must process its output and provide a clear, summarized answer to the user. "
                    "Never refer to information from a tool as if the user can see it. Present the key information directly. "
                    "For advisory questions, provide actionable insights and recommendations based on current market data. "
                    "Your final answers must be plain text only. "
                    "Do not use any markdown formatting, such as backticks (`), in your responses."
                )
            }
        )
        
        # 3. Get response from the agent
        response = agent.invoke({"input": user_message})
        
        # 4. Extract and clean the final answer
        if isinstance(response, dict) and 'output' in response:
            clean_response = response['output'].replace('```', '').strip()
            return clean_response
        else:
            clean_response = str(response).replace('```', '').strip()
            return clean_response
            
    except Exception as e:
        # Return a more user-friendly error
        return f"Sorry, I encountered an error: {str(e)}"

# Test queries
if __name__ == "__main__":
    print("\n📉 Testing chatbot responses with history:")
    
    # Simulate a conversation
    history = []
    
    q1 = "which stock has the highest loss"
    print(f"\nQ1: {q1}")
    a1 = get_chatbot_response(q1, history)
    print(f"A1: {a1}")
    
    history.append({"sender": "sent", "text": q1})
    history.append({"sender": "received", "text": a1})
    
    q2 = "and by how much percent?"
    print(f"\nQ2: {q2}")
    a2 = get_chatbot_response(q2, history)
    print(f"A2: {a2}")

    # Test the new advisory tool
    history.append({"sender": "sent", "text": q2})
    history.append({"sender": "received", "text": a2})
    
    q3 = "give me some investment advice for the current market"
    print(f"\nQ3: {q3}")
    a3 = get_chatbot_response(q3, history)
    print(f"A3: {a3}")


