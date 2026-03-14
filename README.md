# 🛡️ RefundShield AI

**Autonomous Refund Fraud Investigator**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![Razorpay](https://img.shields.io/badge/Razorpay-3395FF?style=for-the-badge&logo=razorpay&logoColor=white)](https://razorpay.com/)

An intelligent multi-agent system that automatically investigates refund claims, detects fraud patterns using AI, and autonomously processes or rejects refunds via Razorpay.

![Dashboard Preview](https://img.shields.io/badge/Dashboard-Next.js-000000?style=flat-square)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square)
![AI Model](https://img.shields.io/badge/AI-GPT--4_Vision-412991?style=flat-square)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Demo](#-demo)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Sponsor Integrations](#-sponsor-integrations)
- [Contributing](#-contributing)

---

## ✨ Features

### 🤖 AI-Powered Investigation
- **Evidence Analysis**: GPT-4 Vision analyzes damage evidence images
- **Fraud Detection**: Detects AI-generated images, manipulation, and anomalies
- **Pattern Recognition**: FAISS-based vector search for similar fraud cases

### 🔒 Security & Verification
- **File Security**: SafeDep-style file validation and scanning
- **URL Threat Detection**: Gearsec-style malicious URL detection via VirusTotal
- **Merchant Verification**: Crustdata API integration for company intelligence

### 💰 Automated Refunds
- **Payment Processing**: Razorpay API for instant refund execution
- **Risk-Based Decisions**: Auto-approve (0-30), Manual review (31-70), Reject (71-100)
- **Customer Communication**: Automated email responses via AI

### 📊 Observability
- **Event Streaming**: S2.dev-style event logging
- **Multi-Agent Orchestration**: Emergent AI-style agent coordination
- **Real-time Dashboard**: Monitor all investigations

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           REFUNDSHIELD AI                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐          │
│  │   Next.js    │───▶│   FastAPI        │───▶│   SQLite         │          │
│  │   Dashboard  │◀───│   Backend        │◀───│   Database       │          │
│  └──────────────┘    └──────────────────┘    └──────────────────┘          │
│                              │                                              │
│           ┌──────────────────┼──────────────────┐                          │
│           ▼                  ▼                  ▼                          │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                   │
│  │EvidenceAgent │   │SecurityAgent │   │MerchantAgent │                   │
│  │  (OpenAI)    │   │(SafeDep/VT)  │   │ (Crustdata)  │                   │
│  └──────────────┘   └──────────────┘   └──────────────┘                   │
│         │                  │                  │                           │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                   │
│  │KnowledgeAgent│   │  FraudAgent  │   │ RefundAgent  │                   │
│  │(Unsiloed AI) │   │(Risk Scorer) │   │  (Razorpay)  │                   │
│  └──────────────┘   └──────────────┘   └──────────────┘                   │
│                             │                                             │
│                    ┌────────┴────────┐                                    │
│                    ▼                 ▼                                    │
│            ┌──────────────┐  ┌──────────────┐                            │
│            │ ReportAgent  │  │ResponseAgent │                            │
│            │              │  │ (Concierge)  │                            │
│            └──────────────┘  └──────────────┘                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Workflow

```
Claim Submission → Evidence Analysis → Image Search → Security Scan → 
Merchant Verification → Knowledge Retrieval → Fraud Scoring → 
Refund Decision → Payment Action → Report Generation → Customer Response
```

---

## 🎬 Demo

### Fraud Score Gauge
| Score | Decision | Color |
|-------|----------|-------|
| 0-30 | ✅ APPROVED | Green |
| 31-70 | ⏸ MANUAL REVIEW | Yellow |
| 71-100 | ❌ REJECTED | Red |

### Example Output
```json
{
  "claim_id": "CLM_A1B2C3D4E5F6",
  "fraud_score": 12,
  "decision": "approved",
  "refund_id": "rfnd_FP8R8EGjGbPkVb",
  "risk_factors": [],
  "investigation_report": {
    "image_analysis": { "damage_detected": true, "ai_generated_probability": 5 },
    "security_scan": { "safe": true, "threats_found": [] },
    "merchant_verification": { "verified": true, "company_name": "Amazon" }
  }
}
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- API Keys (optional - works in simulation mode):
  - OpenAI API Key (for image analysis)
  - Razorpay API Keys (for live refunds)
  - VirusTotal API Key (for URL scanning)

### 1-Minute Setup

```bash
# Clone repository
git clone <repository-url>
cd refundshield-ai

# Start Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Edit .env with your OPENAI_API_KEY
cp .env.example .env
uvicorn main:app --reload

# Start Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Access the application:
- 🖥️ **Dashboard**: http://localhost:3000
- 🔌 **API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

---

## 📦 Installation

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Edit .env and add your API keys

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
npm start
```

### Environment Variables

Create `backend/.env`:

```env
# Required for AI Analysis
OPENAI_API_KEY=sk-your_openai_api_key_here

# Optional - System simulates if not provided
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
VIRUSTOTAL_API_KEY=your_virustotal_api_key
SERPAPI_API_KEY=your_serpapi_key
CRUSTDATA_API_KEY=your_crustdata_api_key
```

---

## 📡 API Documentation

### Submit Refund Claim

```http
POST /submit-claim
Content-Type: multipart/form-data

order_id=ORDER123
merchant_name=Amazon
payment_id=pay_xxx
refund_amount=1000.00
claim_reason=Product damaged on delivery
image=<file>
```

**Response:**
```json
{
  "claim_id": "CLM_A1B2C3D4E5F6",
  "fraud_score": 12,
  "decision": "approved",
  "refund_status": "processed",
  "refund_id": "rfnd_xxx",
  "investigation_report": { ... },
  "customer_response": "Dear Customer, Your refund..."
}
```

### Get All Claims

```http
GET /claims?limit=50
```

### Get Event Logs (S2.dev Style)

```http
GET /events?claim_id=xxx&event_type=xxx
```

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "agents": ["EvidenceAgent", "SecurityAgent", "MerchantAgent", ...]
}
```

---

## 🧪 Testing

### Using the Test File

A comprehensive test file with 10 scenarios is provided:

```bash
# View test cases
cat backend/test_inputs.txt
```

### Quick Test via curl

```bash
# Test 1: Low Risk (Approved)
curl -X POST http://localhost:8000/submit-claim \
  -F "order_id=ORDER_001_LEGIT" \
  -F "merchant_name=Amazon" \
  -F "payment_id=pay_Amazon123" \
  -F "refund_amount=1299.00" \
  -F "claim_reason=Received damaged smartphone" \
  -F "image=@/path/to/photo.jpg"

# Test 2: High Risk (Rejected) - with suspicious URL
curl -X POST http://localhost:8000/submit-claim \
  -F "order_id=ORDER_002_FAKE" \
  -F "merchant_name=UnknownShop" \
  -F "payment_id=pay_Fraud999" \
  -F "refund_amount=4999.00" \
  -F "claim_reason=Visit http://bit.ly/suspicious for details" \
  -F "image=@/path/to/stock_photo.jpg"
```

### Test Scenarios

| # | Scenario | Expected Score | Decision |
|---|----------|----------------|----------|
| 1 | Amazon + Real damage | 10-25 | ✅ APPROVED |
| 2 | AI-generated image | 70-95 | ❌ REJECTED |
| 3 | Suspicious URL | 35-55 | ⏸ MANUAL |
| 4 | Flipkart + Valid claim | 10-20 | ✅ APPROVED |
| 5 | Reused stock image | 75-90 | ❌ REJECTED |

---

## 🤝 Sponsor Integrations

| Sponsor | Integration | Status | Description |
|---------|-------------|--------|-------------|
| **Razorpay** | Payment Gateway | ✅ Live + Simulated | Execute refunds via Razorpay API |
| **SafeDep** | File Security | ✅ Simulated | Validate file types and scan for threats |
| **Gearsec** | URL Threat Detection | ✅ Via VirusTotal | Check URLs for malicious content |
| **Crustdata** | Company Intelligence | ✅ Simulated | Verify merchant legitimacy |
| **S2.dev** | Event Streaming | ✅ Simulated | Log all system events |
| **Emergent AI** | Agent Orchestration | ✅ Implemented | Multi-agent coordination |
| **Unsiloed AI** | Knowledge Retrieval | ✅ FAISS-based | Vector search for fraud patterns |
| **Concierge** | Response Automation | ✅ OpenAI-powered | Generate customer emails |

---

## 📊 Fraud Scoring System

### Risk Factors

| Factor | Score Impact |
|--------|-------------|
| AI-generated image detected | +40 |
| Image found online (reuse) | +30 |
| Suspicious URL detected | +20 |
| Unverified merchant | +20 |
| Similar fraud pattern found | +20 |
| Security threat detected | +25 |
| Image manipulation detected | +35 |
| Metadata anomaly | +15 |

### Decision Matrix

```
Score 0-30:   🟢 APPROVE  → Process refund via Razorpay
Score 31-70:  🟡 MANUAL   → Flag for human review
Score 71-100: 🔴 REJECT   → Deny refund, log fraud attempt
```

---

## 🛡️ Security Features

- ✅ File type validation using magic numbers
- ✅ Malicious file detection
- ✅ URL reputation checking (VirusTotal API)
- ✅ Suspicious pattern detection
- ✅ Metadata anomaly detection
- ✅ Image perceptual hashing
- ✅ Reverse image search (SerpAPI)

---

## 🏛️ Project Structure

```
refundshield-ai/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example              # Environment template
│   ├── test_inputs.txt           # 10 test scenarios
│   ├── agents/                   # 8 AI Agents
│   │   ├── base_agent.py         # Agent orchestration (Emergent AI)
│   │   ├── evidence_agent.py     # OpenAI Vision analysis
│   │   ├── security_agent.py     # SafeDep/Gearsec scanning
│   │   ├── merchant_agent.py     # Crustdata verification
│   │   ├── fraud_agent.py        # Risk scoring engine
│   │   ├── refund_agent.py       # Razorpay integration
│   │   ├── knowledge_agent.py    # Unsiloed AI (FAISS)
│   │   ├── report_agent.py       # Investigation reports
│   │   └── response_agent.py     # Concierge automation
│   ├── services/
│   │   ├── event_logger.py       # S2.dev event streaming
│   │   └── image_search.py       # SerpAPI integration
│   └── database/
│       └── models.py             # SQLite models
│
├── frontend/
│   ├── pages/index.js            # Main dashboard
│   ├── components/
│   │   ├── SponsorBadges.js      # Integration badges
│   │   ├── FraudScoreGauge.js    # Animated score display
│   │   ├── InvestigationReport.js # Report viewer
│   │   └── RecentClaims.js       # Claims history
│   └── styles/globals.css        # Tailwind CSS
│
└── README.md                     # This file
```

---

## 🛠️ Technologies Used

### Backend
- **FastAPI** - High-performance web framework
- **SQLAlchemy** - ORM for database operations
- **OpenAI GPT-4 Vision** - Image analysis
- **FAISS** - Vector similarity search
- **Razorpay SDK** - Payment processing

### Frontend
- **Next.js 14** - React framework
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client
- **Lucide React** - Icon library

### AI/ML
- **GPT-4 Vision** - Evidence analysis
- **ImageHash** - Perceptual hashing
- **FAISS** - Vector search
- **TikToken** - Token counting

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built for the hackathon with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [OpenAI](https://openai.com/)
- [Razorpay](https://razorpay.com/)
- [FAISS](https://github.com/facebookresearch/faiss)

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

**RefundShield AI** - Making refund processing smarter, faster, and safer with AI. 🚀
