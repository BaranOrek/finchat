# 💬 FinChat – AI-Powered Crypto Assistant

FinChat is an AI-powered chat application that provides real-time cryptocurrency insights, including current prices, historical trends, and chart-based analysis.

The system combines natural language understanding with live market data to deliver an intuitive conversational experience.

---

## 🚀 Features

- 💰 Real-time crypto prices (Bitcoin, Ethereum, Dogecoin, etc.)
- 📊 Interactive price charts for custom timeframes
- 🧠 Context-aware conversation (follow-up questions supported)
- 🗓️ Natural language date parsing (e.g. "last month", "February")
- 🔍 Dynamic asset resolution (no strict predefined list required)
- ⚡ AI-powered responses using structured market data
- 🧩 Graceful handling of edge cases (future dates, long ranges, unknown assets)

---

## 🏗️ Architecture

### Backend (FastAPI)
- AI query planning layer
- Market data integration (CoinGecko API)
- Timeframe normalization
- Chart summarization logic

### Frontend (React + Vite)
- Chat UI
- Chart visualization
- Responsive layout

---

## 🧠 How It Works

1. User sends a message  
2. AI planner extracts:
   - intent  
   - asset  
   - timeframe  
3. Backend fetches:
   - current price  
   - historical chart data  
4. Chart summary is generated  
5. AI produces a final response using structured data  

---

## 📊 Example Queries

What is the current price of Bitcoin?
How has it changed over the last week?
Show me Ethereum performance in February
What about last month?
price of doge

---

## 🧪 Demo Conversation

User: What is the current price of BTC?
AI: The current price of Bitcoin is $74,990 USD.

User: How has it changed over the last 10 days?
AI: Bitcoin increased by 8.31% over the last 10 days...

User: What about ETH?
AI: Ethereum increased by...

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/finchat.git
cd finchat
```