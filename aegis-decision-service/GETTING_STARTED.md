# 🚀 Getting Started with A.E.G.I.S. v2.0

**From zero to deployed in 30 minutes**

---

## ✅ What You Have

Your A.E.G.I.S. Decision Service is now complete with:

- ✅ **FastAPI application** with auto-generated OpenAPI spec
- ✅ **IBM watsonx.ai Granite integration** with robust JSON parsing
- ✅ **Local runbook system** + optional Langflow hooks
- ✅ **Strict Pydantic contracts** for watsonx Orchestrate
- ✅ **Comprehensive tests** with pytest
- ✅ **Production Dockerfile** ready for deployment
- ✅ **Complete documentation** for demo and integration

---

## 🎯 Quick Start (3 Steps)

### Step 1: Set up credentials (5 min)

```bash
# Copy template
cp .env.template .env

# Edit .env and add:
# WATSONX_APIKEY=your_actual_api_key
# WATSONX_PROJECT_ID=your_actual_project_id
```

Get credentials:
- API Key: https://cloud.ibm.com → Manage → Access (IAM) → API Keys
- Project ID: https://dataplatform.cloud.ibm.com/wx/home → Your Project → Manage → Project ID

### Step 2: Install and run (3 min)

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install
pip install -r requirements.txt

# Run
uvicorn src.aegis_service.main:app --reload --port 5000
```

### Step 3: Test it (2 min)

```bash
# Health check
curl http://localhost:5000/health

# Test evaluation
curl -X POST http://localhost:5000/evaluate-incident \
  -H "Content-Type: application/json" \
  -d "{\"incident_text\": \"Disk at 95%. Log rotation failed. No user impact.\", \"category\": \"storage\"}"
```

**You should see a JSON response with `confidence_score`, `recommended_action`, etc.**

---

## 📊 Understanding the Response

When you POST to `/evaluate-incident`, you get:

```json
{
  "analysis": "One-sentence incident summary",
  "recommended_action": "clear_logs|restart_service|run_diagnostics|escalate_to_human",
  "confidence_score": 0-100,  // THE KEY FIELD FOR ORCHESTRATE
  "explanation": "Why this decision was made",
  "runbook_context": "Relevant runbook excerpt",
  "trace_id": "unique-uuid-for-logging",
  "model_id": "ibm/granite-3-8b-instruct",
  "policy": {
    "auto_execute_threshold": 80,
    "escalate_threshold": 80
  }
}
```

**The `confidence_score` field is what watsonx Orchestrate uses for branching:**
- **≥ 80**: Auto-execute path
- **< 80**: Escalate to human path

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_contract.py -v
```

Tests validate:
- Response schema compliance
- Confidence policy enforcement
- Fallback behavior
- Input validation

---

## 📦 Deploying to IBM Code Engine

### Option 1: Console (Easiest)

1. Go to https://cloud.ibm.com
2. Search "Code Engine"
3. Create Project: `aegis-project`
4. Create Application:
   - Name: `aegis-decision-service`
   - Source: Upload this folder (or connect to GitHub)
   - Port: `5000`
   - Env vars:
     - `WATSONX_APIKEY` = your key
     - `WATSONX_PROJECT_ID` = your project ID
     - `PORT` = `5000`
5. Deploy

You'll get a URL like: `https://aegis-decision-service.xxx.codeengine.appdomain.cloud`

### Option 2: Docker

```bash
# Build
docker build -t aegis-decision-service .

# Test locally
docker run -p 5000:5000 \
  -e WATSONX_APIKEY=your_key \
  -e WATSONX_PROJECT_ID=your_project_id \
  aegis-decision-service

# Then deploy to Code Engine using container registry
```

---

## 🔗 Export OpenAPI for Orchestrate

After deploying:

```bash
# Export the spec
python scripts/export_openapi.py

# Edit openapi.yaml and update the server URL:
servers:
  - url: https://your-actual-code-engine-url.codeengine.appdomain.cloud
```

Import `openapi.yaml` into watsonx Orchestrate:
- Go to Orchestrate → Skills → Add Skill → Import OpenAPI
- Upload `openapi.yaml`
- Test the "Evaluate Incident" skill

---

## 🎬 Demo Time

### Scenario A: High Confidence (Auto-Execute)

```bash
curl -X POST http://localhost:5000/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "Disk usage at 95%. Log rotation service failed at 3 AM. No active user sessions affected. Standard log cleanup procedures apply.",
    "category": "storage"
  }'
```

**Expected:**
- `confidence_score`: ~95
- `recommended_action`: `clear_logs`
- **Demo point**: System handles routine issues efficiently

### Scenario B: Low Confidence (Escalate) ⭐

```bash
curl -X POST http://localhost:5000/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "Multiple users reporting intermittent authentication failures. No clear pattern. May be related to deployment 2 hours ago.",
    "category": "auth"
  }'
```

**Expected:**
- `confidence_score`: ~45
- `recommended_action`: `escalate_to_human`
- **Demo point**: **AI knows when NOT to act** ← THIS IS THE WINNING MOMENT

---

## 📚 Next Steps

### For Local Development

1. ✅ Service running at http://localhost:5000
2. 📖 Browse API docs at http://localhost:5000/docs
3. 🧪 Run tests: `pytest`
4. 🔍 Check logs for trace IDs and decisions

### For Deployment

1. ☁️ Deploy to IBM Code Engine
2. 📤 Export OpenAPI spec with your URL
3. 🔗 Import into watsonx Orchestrate
4. 🎯 Build orchestration workflow

### For Demo

1. 📝 Review [docs/demo-scenarios.md](docs/demo-scenarios.md)
2. 🎤 Practice the narration (especially Scenario B)
3. 🏗️ Study the architecture diagram in README
4. 💡 Memorize the one-liner: *"AI that knows when NOT to act"*

---

## 🛠️ Troubleshooting

### "Module not found"
```bash
# Make sure you're in the right directory
cd aegis-agent

# Make sure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall
pip install -r requirements.txt
```

### "Connection to watsonx.ai failed"
```bash
# Test connection
curl http://localhost:5000/version

# Check environment variables
cat .env  # or type .env on Windows

# Make sure WATSONX_APIKEY and WATSONX_PROJECT_ID are set
```

### "JSON parse error from model"
- This is usually fine - the app has 4 fallback strategies
- Check logs for the raw model output
- The system will return a safe escalation if parsing fails

### Port already in use
```bash
# Use a different port
uvicorn src.aegis_service.main:app --port 5001

# Or kill the process using port 5000
# Windows: netstat -ano | findstr :5000
# Mac/Linux: lsof -ti:5000 | xargs kill
```

---

## 🏆 Key Files to Know

| File | Purpose |
|------|---------|
| [src/aegis_service/main.py](src/aegis_service/main.py) | FastAPI app - start here |
| [src/aegis_service/models.py](src/aegis_service/models.py) | Pydantic contracts - the JSON spec |
| [src/aegis_service/watsonx_client.py](src/aegis_service/watsonx_client.py) | Granite integration |
| [runbooks/*.md](runbooks/) | Domain-specific incident runbooks |
| [tests/test_contract.py](tests/test_contract.py) | Contract validation tests |
| [README.md](README.md) | Complete documentation |
| [docs/demo-scenarios.md](docs/demo-scenarios.md) | Demo scripts |
| [.env.template](.env.template) | Environment configuration |

---

## 💡 Pro Tips

1. **Always check the `/docs` endpoint** - FastAPI auto-generates interactive docs
2. **Use trace IDs for debugging** - every request gets a unique UUID
3. **Test both scenarios** - high confidence and low confidence
4. **Check the logs** - structured logging shows the decision flow
5. **Start simple** - test locally before deploying

---

## 🎯 Your One-Liner for Judges

> "A.E.G.I.S. demonstrates how enterprises can safely deploy agentic AI by combining watsonx Orchestrate for workflow control, watsonx.ai for intelligent decisions, and confidence-based routing for human-in-the-loop governance."

**Practice saying this out loud** - it's your opening and closing statement.

---

## ✨ You're Ready!

You now have a production-quality Decision Service that demonstrates:
- ✅ Real AI reasoning (not if-else)
- ✅ Enterprise governance patterns
- ✅ Clean architecture and testing
- ✅ Full watsonx Orchestrate integration

**Go build something amazing! 🚀**

---

**Questions? Check:**
- 📖 [README.md](README.md) - Full documentation
- 🎬 [docs/demo-scenarios.md](docs/demo-scenarios.md) - Demo scripts
- 🔗 [docs/orchestrate-setup-guide.md](docs/orchestrate-setup-guide.md) - Orchestrate integration

**Built for IBM Dev Day Hackathon 2026**
