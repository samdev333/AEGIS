# ⚡ A.E.G.I.S. Quick Start Guide

**Get your Decision Service running in under 10 minutes**

---

## Step 1: Get IBM Cloud Credentials (5 minutes)

### Get API Key
1. Go to [cloud.ibm.com](https://cloud.ibm.com)
2. **Manage** > **Access (IAM)** > **API Keys**
3. **Create an IBM Cloud API key**
4. Name it `aegis-key` and **copy it**

### Get Project ID
1. Go to [watsonx.ai](https://dataplatform.cloud.ibm.com/wx/home)
2. **Projects** > **View all projects**
3. Create new project: `AEGIS`
4. Click project name > **Manage** tab
5. Copy **Project ID**

---

## Step 2: Local Setup (3 minutes)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.template .env  # Windows
cp .env.template .env    # Mac/Linux

# Edit .env and add your credentials:
# IBM_CLOUD_API_KEY=your_key_here
# WATSONX_PROJECT_ID=your_project_id_here
```

---

## Step 3: Test Locally (2 minutes)

```bash
# Start the service
python app.py
```

Open another terminal and test:

```bash
# Health check
curl http://localhost:5000

# Test evaluation
curl -X POST http://localhost:5000/evaluate-incident \
  -H "Content-Type: application/json" \
  -d "{\"incident_text\": \"High database latency detected\", \"category\": \"latency\"}"
```

✅ **You should see a JSON response with `confidence_score`, `recommended_action`, etc.**

---

## Step 4: Deploy to IBM Cloud (10 minutes)

### Via Console (No CLI)

1. Go to [IBM Cloud Console](https://cloud.ibm.com)
2. Search **Code Engine**
3. **Create Project**: `aegis-project`
4. **Create Application**: `aegis-decision-service`
5. **Source**: Upload your folder
6. **Port**: `5000`
7. **Environment Variables**:
   - `IBM_CLOUD_API_KEY` = your key
   - `WATSONX_PROJECT_ID` = your project ID
8. **Create**

Wait 2-3 minutes for build. You'll get a URL like:
```
https://aegis-decision-service.xxx.us-south.codeengine.appdomain.cloud
```

Test it:
```bash
curl https://your-url.appdomain.cloud
```

---

## Step 5: Connect to watsonx Orchestrate (15 minutes)

1. Update `openapi-spec.yaml`:
   - Change the `servers` URL to your Code Engine URL

2. Go to [watsonx Orchestrate](https://www.ibm.com/products/watsonx-orchestrate)
3. **Skills** > **Add Skill** > **Import OpenAPI**
4. Upload `openapi-spec.yaml`
5. Test the skill

Full setup details: See [docs/orchestrate-setup-guide.md](docs/orchestrate-setup-guide.md)

---

## Test Your Demo Scenarios

### High Confidence Test
```bash
curl -X POST https://your-url/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "Disk usage at 95%. Log rotation failed. No user impact.",
    "category": "storage"
  }'
```

Expected: `confidence_score` >= 80

### Low Confidence Test
```bash
curl -X POST https://your-url/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "Intermittent auth failures. No clear pattern. May be related to deployment.",
    "category": "auth"
  }'
```

Expected: `confidence_score` < 80

---

## Troubleshooting

### "Missing API key"
- Check your `.env` file has actual values (not placeholder text)
- Restart the Flask app after editing `.env`

### "Connection to watsonx.ai failed"
```bash
curl http://localhost:5000/test-connection
```
This will tell you the exact error.

### "JSON parse error"
This is usually fine - the app automatically extracts JSON from model output. Check the logs.

---

## Next Steps

1. ✅ Service running locally
2. ✅ Service deployed to Code Engine
3. ✅ Connected to watsonx Orchestrate
4. 📖 Review [docs/demo-scenarios.md](docs/demo-scenarios.md) for demo script
5. 🎯 Practice your 3-minute demo

---

## Quick Demo Checklist

Before presenting:

- [ ] Service URL works
- [ ] Test high-confidence scenario (returns 80+)
- [ ] Test low-confidence scenario (returns <80)
- [ ] Orchestrate flow pauses at human review for low confidence
- [ ] Can explain: "AI knows when NOT to act"

---

**You're ready to demo! See [README.md](README.md) for full documentation.**
