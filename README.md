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

### 2. Backend Setup

```
cd backend
pip install -r requirements.txt
```

Create a .env file:

```
AI_API_KEY=your_openai_key
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini

COINGECKO_BASE_URL=https://api.coingecko.com/api/v3
COINGECKO_DEMO_API_KEY=your_coingecko_key
```

Run the backend:

```
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```
cd frontend
npm install
```

Create a .env file:

```
VITE_API_BASE_URL=http://localhost:8000
```

Run the frontend:

```
npm run dev
```

### 🐳 Docker (Optional)

```
docker-compose up --build
```

### 🌐 Deployment

- Backend: Render
- Frontend: Vercel

---

## ⚠️ Limitations

- Historical analysis is currently limited to the most recent 365 days.
- External market data depends on CoinGecko API availability and rate limits.
- Multi-asset comparison support is currently partial and not fully charted side by side.

---

## 🔮 Future Improvements

- Add structured logging and better observability across planner, market data, and response-generation layers.
- Improve code documentation and docstring coverage in line with Python style and documentation guidelines.
- Replace localStorage-based chat persistence with a user-based backend architecture backed by a database.
- Further improve the planner layer so it can resolve more coin references and ambiguous follow-up questions more reliably.
- Remove the current 365-day historical limit by supporting broader date ranges with stronger validation and provider-side optimizations.
- Add richer chart interactions such as zooming, comparison views, and better timeframe controls.
- Introduce stronger caching and fallback strategies for external market-data rate limits.
- Improve asset disambiguation when multiple assets match the same user query.

---

## 📌 Tech Stack

- FastAPI (Python)
- React + Vite
- TypeScript
- OpenAI API
- CoinGecko API
- Docker
- Render
- Vercel

---

## 👨‍💻 Author

Baran Örek
