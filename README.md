# 📊 FinChat – AI-Powered Crypto Assistant

FinChat is a full-stack AI-powered chatbot that provides real-time cryptocurrency insights, including current prices and historical performance with interactive charts.

---

## 🚀 Features

* 💬 Conversational crypto assistant (ChatGPT-style interface)
* 📈 Real-time price tracking (BTC, ETH, SOL)
* 📊 Historical performance analysis with charts
* 🧠 Intelligent query planning (intent + asset + timeframe detection)
* ⚡ FastAPI backend with structured responses
* 🌐 Deployed frontend and backend (cloud-ready)

---

## 🏗️ Tech Stack

### Backend

* Python + FastAPI
* OpenAI API (for natural language understanding & responses)
* CoinGecko API (market data)
* Pydantic (schema validation)

### Frontend

* React + TypeScript
* Vite
* Chart visualization (custom chart rendering)

### Deployment

* Backend: Render
* Frontend: Vercel
* Dockerized for portability

---

## 🧠 How It Works

1. User sends a message (e.g. *"How has Bitcoin moved over the last month?"*)
2. Backend uses an AI planner to extract:

   * Intent (finance / casual)
   * Asset (BTC, ETH, etc.)
   * Timeframe
3. Market data is fetched from CoinGecko
4. A structured **market context** is built
5. AI generates a natural language response
6. Chart data is returned to frontend

---

## 📊 Example Queries

* `What is the current price of BTC?`
* `How has Ethereum performed over the last month?`
* `Show me Solana in February`
* `What happened to Bitcoin in the last year?`

---

## ⚙️ Environment Variables

### Backend

```env
OPENAI_API_KEY=your_openai_key
COINGECKO_DEMO_API_KEY=your_coingecko_key
COINGECKO_BASE_URL=https://api.coingecko.com/api/v3
```

### Frontend

```env
VITE_API_BASE_URL=https://your-backend-url.onrender.com
```

---

## 🐳 Docker Setup

Run the full stack locally:

```bash
docker-compose up --build
```

* Backend → http://localhost:8000
* Frontend → http://localhost:5173

---

## ⚠️ Notes on Rate Limiting

CoinGecko public API has strict rate limits.
To improve reliability:

* Demo API key is used
* Lightweight server-side caching can be applied (optional improvement)

---

## 📦 Project Structure

```
finchat/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── schemas/
│   │   └── core/
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   └── Dockerfile
│
└── docker-compose.yml
```

---

## ✨ Future Improvements

* Persistent chat history (context-aware conversations)
* Advanced charting (zoom, multi-asset comparison)
* Portfolio tracking
* WebSocket streaming for live price updates

---

## 🌐 Live Demo

- Frontend: https://finchat-tan.vercel.app
- Backend: https://finchat-4o0r.onrender.com

## 👤 Author

Baran Örek
