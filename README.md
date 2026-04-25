# 💬 FinChat – AI-Powered Crypto Assistant

FinChat is an AI-powered crypto assistant that turns natural language questions into real market insights.

Instead of returning raw numbers, it understands user intent and provides **clear explanations, comparisons, and performance analysis** based on live market data.


---

## ✨ Key Features

- 💰 **Real-time crypto prices** (BTC, ETH, SOL, DOGE, XRP, etc.)
- 📊 **Interactive charts** for recent market performance
- 🔍 **Natural language understanding** ("last month", "2 weeks ago", "February")
- 🔗 **Context-aware conversations** (follow-up questions supported)
- ⚡ **Multi-asset queries** (compare multiple cryptocurrencies)
- 📈 **Normalized comparison charts** (relative performance indexed to 100)
- 🧠 **AI-powered reasoning** using structured market data
- 🧩 **Graceful handling of edge cases** (invalid ranges, unsupported queries)

---

## 🧠 What Makes It Interesting

FinChat is not just a chatbot — it follows a **hybrid architecture**:

- LLM is used for **understanding and explanation**
- Backend logic handles **data fetching and calculations**

This ensures:
- ✔️ reliable outputs  
- ✔️ no hallucinated price data  
- ✔️ consistent behavior  

---

## 🏗️ Architecture

### Backend (FastAPI)

- AI query planner (intent + parameters extraction)
- Market data integration (CoinGecko API)
- Timeframe normalization (with safe constraints)
- Chart summarization
- Multi-asset handling
- Deterministic data pipeline

### Frontend (React + Vite)

- Chat-based UI
- Multi-series chart rendering (Recharts)
- Suggested prompts for feature discovery
- Responsive layout
- Local chat persistence

---

## ⚙️ How It Works

1. User sends a message  
2. AI planner extracts:
   - intent  
   - asset(s)  
   - timeframe  
3. Backend:
   - resolves assets  
   - fetches market data  
   - prepares structured context  
4. AI generates a natural response using this data  

👉 LLM never guesses prices — it only explains real data.

---

## 📊 Example Queries

```txt
Compare Bitcoin and Ethereum performance
Which performed better: BTC or DOGE last 30 days?
Show me Bitcoin trend over the last week
If I invested $1000 in Bitcoin 2 months ago, what now?
```

---

## 🧪 Demo Conversation

User:
> Compare Bitcoin and Dogecoin performance over the last 30 days

FinChat:
> Bitcoin increased by 9.56%, while Dogecoin increased by 11.11%.  
> Dogecoin slightly outperformed Bitcoin over this period.

📈 Includes a normalized comparison chart (relative performance indexed to 100)

---

## ⚠️ Limitations

- Analysis is currently limited to recent market data (last 12 months)
- External data depends on CoinGecko API availability
- Multi-asset comparison is limited to a maximum of 5 assets

---

## 🎯 Design Decisions

1. Historical data limited to 12 months for:
   - API reliability
   - performance consistency
2. Asset limit (5) to:
   - avoid UI overload
   - keep responses clear
3. Hybrid AI + backend approach to:
   - prevent hallucinated data
   - ensure deterministic outputs

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

## 🔗 Live Demo

- Frontend (Vercel): https://finchat-tan.vercel.app 
- Backend (Render): https://finchat-4o0r.onrender.com  

You can directly interact with the application using the frontend, or test the backend via API tools like curl or Postman.

---

## 🔮 Future Improvements

- Investment simulation (multi-asset portfolio support)
- Extended historical data range
- Persistent user accounts (database-backed)
- Advanced chart interactions (zoom, overlays)
- Improved asset disambiguation
- Caching layer for performance

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
