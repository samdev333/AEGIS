# ✅ A.E.G.I.S. Deployment Checklist

## Pre-Deployment Verification

### Files Ready ✅
- [x] Dockerfile
- [x] Procfile
- [x] requirements.txt
- [x] src/aegis_service/main.py
- [x] src/aegis_service/models.py
- [x] src/aegis_service/watsonx_client.py
- [x] src/aegis_service/runbook_context.py
- [x] runbooks/*.md (4 files)
- [x] .env (configured with your credentials)

### Credentials Configured ✅
- [x] WATSONX_APIKEY: `your_ibm_cloud_api_key_here`
- [x] WATSONX_PROJECT_ID: `your_watsonx_project_id_here`
- [x] WATSONX_URL: `https://eu-gb.ml.cloud.ibm.com`
- [x] Region: EU-GB (Europe - UK)

---

## Deployment Steps

### Step 1: Access IBM Cloud Console
1. Go to: https://cloud.ibm.com
2. Login
3. Search: "Code Engine"
4. Open: "watsonx-Hackathon Code Engine" project

### Step 2: Create Application
1. Click: **Applications** → **Create**
2. Name: `aegis-decision-service`
3. Source: **Specify build details**
4. Upload: This folder (`your_project_directory`)

### Step 3: Configure Build
- Strategy: **Dockerfile**
- Dockerfile name: `Dockerfile`
- Port: `5000`

### Step 4: Set Environment Variables
Add these 5 variables:

```
WATSONX_APIKEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
WATSONX_URL=https://eu-gb.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
PORT=5000
```

### Step 5: Set Resources
- CPU: `0.5 vCPU`
- Memory: `1 GB`
- Min instances: `1`
- Max instances: `3`

### Step 6: Deploy
- Click: **Create**
- Wait: 3-5 minutes

### Step 7: Get URL
- Copy the application URL
- Format: `https://aegis-decision-service.xxxxxx.eu-gb.codeengine.appdomain.cloud`

---

## Post-Deployment Testing

### Test 1: Health Check ✅
```bash
curl YOUR_URL/health
```
Expected: `{"status":"ok"}`

### Test 2: Version Info ✅
```bash
curl YOUR_URL/version
```
Expected: Shows model_id and watsonx_url

### Test 3: Interactive Docs ✅
Open in browser: `YOUR_URL/docs`

### Test 4: High Confidence Incident ✅
```bash
curl -X POST YOUR_URL/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{"incident_text":"Disk at 95%. Log rotation failed. No user impact.","category":"storage"}'
```
Expected: `confidence_score` >= 80, `recommended_action` = "clear_logs"

### Test 5: Low Confidence Incident ✅
```bash
curl -X POST YOUR_URL/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{"incident_text":"Intermittent auth failures. No pattern.","category":"auth"}'
```
Expected: `confidence_score` < 80, `recommended_action` = "escalate_to_human"

---

## Quick Deploy Commands (Copy-Paste)

Once you have your URL, replace `YOUR_URL` and test:

```bash
# Set your URL (replace with actual)
URL="https://aegis-decision-service.xxxxxx.eu-gb.codeengine.appdomain.cloud"

# Test health
curl $URL/health

# Test version
curl $URL/version

# Test high confidence
curl -X POST $URL/evaluate-incident -H "Content-Type: application/json" -d '{"incident_text":"Disk at 95%. Log rotation failed.","category":"storage"}'

# Test low confidence
curl -X POST $URL/evaluate-incident -H "Content-Type: application/json" -d '{"incident_text":"Intermittent auth failures.","category":"auth"}'
```

---

## Success Indicators

✅ Health endpoint returns OK
✅ Version shows: `ibm/granite-3-8b-instruct`
✅ High confidence scenario: confidence_score >= 80
✅ Low confidence scenario: recommended_action = "escalate_to_human"
✅ No error messages in logs
✅ Response time < 5 seconds

---

## If Something Goes Wrong

### Build Fails
- Check: Dockerfile is in root directory
- Check: All files uploaded correctly
- Retry: Builds sometimes timeout

### Application Crashes
- Check: All 5 environment variables set
- Check: PORT is exactly `5000`
- View: Runtime logs in Code Engine console

### watsonx.ai Errors
- Verify: API key is correct (no extra spaces)
- Verify: Project ID is correct
- Verify: Region URL is `https://eu-gb.ml.cloud.ibm.com`
- Test: `/version` endpoint to see configuration

---

## Next Steps After Successful Deployment

1. ✅ Save your URL
2. ✅ Run all test commands above
3. ✅ Export OpenAPI spec: `python scripts/export_openapi.py`
4. ✅ Update openapi.yaml with your URL
5. ✅ Import into watsonx Orchestrate
6. ✅ Build orchestration flow
7. ✅ Practice demo scenarios

---

## Your Service Will Be Available At:

```
https://aegis-decision-service.[random-string].eu-gb.codeengine.appdomain.cloud
```

**Endpoints:**
- `/` - Service info
- `/health` - Health check
- `/version` - Version and config
- `/docs` - Interactive API docs (Swagger UI)
- `/evaluate-incident` - Main decision endpoint (POST)
- `/openapi.json` - OpenAPI specification

---

**You're ready to deploy! Follow DEPLOY_GUIDE.md for detailed steps.**
