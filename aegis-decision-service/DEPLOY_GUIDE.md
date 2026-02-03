# 🚀 Deployment Guide for A.E.G.I.S. Decision Service

**Your credentials are configured. Let's deploy to IBM Cloud Code Engine.**

---

## ✅ Pre-configured Settings

Your `.env` file is already set up with:
- ✅ API Key: `your_ibm_cloud_api_key_here`
- ✅ Project ID: `your_watsonx_project_id_here`
- ✅ Region: `eu-gb` (Europe - UK)
- ✅ Code Engine Project: `watsonx-Hackathon Code Engine`

---

## 🎯 Deployment Method 1: IBM Cloud Console (EASIEST - 10 minutes)

### Step 1: Access Code Engine

1. Go to https://cloud.ibm.com
2. Login with your credentials
3. Search for **"Code Engine"** in the top search bar
4. Click on **Code Engine**

### Step 2: Select Your Project

1. You should see your project: **"watsonx-Hackathon Code Engine"**
2. Click on it to open

### Step 3: Create Application

1. Click **"Applications"** in the left sidebar
2. Click **"Create"** button (top right)

### Step 4: Configure Application

**General:**
- **Name**: `aegis-decision-service`
- **Choose how to run**: Select **"Source code"**

**Source:**
- **Code**: Click **"Specify build details"**
  - **Source**: Choose **"Local source code"**
  - Click **"Choose files"** or **"Choose folder"**
  - **Navigate to**: `your_project_directory`
  - **Upload the entire folder**

  **OR** if folder upload doesn't work:
  - Create a ZIP file of the `aegis-agent` folder first
  - Upload the ZIP file

**Build details:**
- **Strategy**: Select **"Dockerfile"** (our Dockerfile is already configured)
- **Dockerfile**: Leave as `Dockerfile` (it will find it automatically)
- **Timeout**: 600 seconds

**Runtime settings:**
- **Listening port**: `5000`
- **Resources**:
  - **CPU**: `0.5 vCPU`
  - **Memory**: `1 GB`
- **Scaling**:
  - **Min instances**: `1`
  - **Max instances**: `3`

**Environment variables** - Click "Add environment variable" for each:
1. **Name**: `WATSONX_APIKEY`
   **Value**: `your_ibm_cloud_api_key_here`

2. **Name**: `WATSONX_PROJECT_ID`
   **Value**: `your_watsonx_project_id_here`

3. **Name**: `WATSONX_URL`
   **Value**: `https://eu-gb.ml.cloud.ibm.com`

4. **Name**: `WATSONX_MODEL_ID`
   **Value**: `ibm/granite-3-8b-instruct`

5. **Name**: `PORT`
   **Value**: `5000`

### Step 5: Deploy

1. Click **"Create"** at the bottom
2. Wait 3-5 minutes for the build and deployment
3. You'll see a progress indicator

### Step 6: Get Your URL

Once deployment is complete:
1. Click on your application name: `aegis-decision-service`
2. You'll see the **URL** at the top (something like):
   ```
   https://aegis-decision-service.xxxxxxxxxxx.eu-gb.codeengine.appdomain.cloud
   ```
3. **Copy this URL** - this is your service endpoint!

---

## 🧪 Test Your Deployment

Once you have the URL, test it:

### Health Check
```bash
curl https://your-url.eu-gb.codeengine.appdomain.cloud/health
```

**Expected response:**
```json
{"status": "ok"}
```

### Version Check
```bash
curl https://your-url.eu-gb.codeengine.appdomain.cloud/version
```

### Interactive API Docs
Open in browser:
```
https://your-url.eu-gb.codeengine.appdomain.cloud/docs
```

### Test Incident Evaluation (High Confidence)
```bash
curl -X POST https://your-url.eu-gb.codeengine.appdomain.cloud/evaluate-incident \
  -H "Content-Type: application/json" \
  -d "{\"incident_text\": \"Disk usage at 95%. Log rotation failed. No user impact.\", \"category\": \"storage\"}"
```

**Expected response:**
```json
{
  "analysis": "Disk space critically low due to failed log rotation",
  "recommended_action": "clear_logs",
  "confidence_score": 95,
  ...
}
```

### Test Incident Evaluation (Low Confidence - Should Escalate)
```bash
curl -X POST https://your-url.eu-gb.codeengine.appdomain.cloud/evaluate-incident \
  -H "Content-Type: application/json" \
  -d "{\"incident_text\": \"Intermittent auth failures. No clear pattern. May be related to deployment.\", \"category\": \"auth\"}"
```

**Expected response:**
```json
{
  "analysis": "Authentication failures with unclear root cause",
  "recommended_action": "escalate_to_human",
  "confidence_score": 45,
  ...
}
```

---

## 🎯 Deployment Method 2: IBM Cloud CLI (IF YOU HAVE IT INSTALLED)

If you have the IBM Cloud CLI installed, run:

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

This will automatically deploy and give you the URL.

---

## 📦 After Deployment: Export OpenAPI Spec

Once deployed, update the OpenAPI spec with your URL:

1. **Edit `scripts/export_openapi.py`** and update line 24-25 with your actual URL

2. **Run the export script:**
```bash
python scripts/export_openapi.py
```

3. **Edit `openapi.yaml`** and update the servers section:
```yaml
servers:
  - url: https://your-actual-url.eu-gb.codeengine.appdomain.cloud
    description: IBM Code Engine Deployment
```

4. **Import into watsonx Orchestrate:**
   - Go to watsonx Orchestrate
   - Skills → Add Skill → Import OpenAPI
   - Upload `openapi.yaml`
   - Test the "Evaluate Incident" skill

---

## 🔧 Troubleshooting

### Build Failed
- **Check Dockerfile**: Make sure it's in the root directory
- **Check logs**: In Code Engine console → Your app → Logs
- **Try again**: Sometimes builds fail due to timeout, just retry

### Application Won't Start
- **Check environment variables**: Make sure all 5 env vars are set correctly
- **Check port**: Must be `5000`
- **Check logs**: Code Engine console → Your app → Runtime logs

### Can't Access URL
- **Wait a minute**: Sometimes DNS takes time to propagate
- **Check status**: Make sure application shows "Ready" status
- **Check scaling**: Make sure min instances is at least 1

### watsonx.ai Connection Errors
- **Check API key**: Make sure `WATSONX_APIKEY` is correct
- **Check Project ID**: Make sure `WATSONX_PROJECT_ID` is correct
- **Check region**: URL should be `https://eu-gb.ml.cloud.ibm.com` for your region
- **Test**: Try `/version` endpoint first to check configuration

---

## 📊 Monitoring Your Deployment

In the Code Engine console, you can:
- **View logs**: Real-time application logs
- **Monitor requests**: See incoming requests and response times
- **Check scaling**: See how many instances are running
- **View metrics**: CPU, memory usage

---

## ✅ Success Checklist

- [ ] Application deployed successfully
- [ ] URL obtained
- [ ] Health check returns `{"status": "ok"}`
- [ ] Version endpoint shows watsonx.ai config
- [ ] `/docs` endpoint shows interactive API
- [ ] High confidence incident returns `confidence_score >= 80`
- [ ] Low confidence incident returns `escalate_to_human`
- [ ] OpenAPI spec exported with correct URL
- [ ] Ready to import into watsonx Orchestrate

---

## 🎉 You're Done!

Once all checks pass, you have:
✅ A working Decision Service deployed to IBM Cloud
✅ Real AI-powered incident analysis using Granite
✅ Confidence-based routing ready for Orchestrate
✅ Interactive API docs at `/docs`

**Next:** Import your `openapi.yaml` into watsonx Orchestrate and build the orchestration flow!

See [docs/orchestrate-setup-guide.md](docs/orchestrate-setup-guide.md) for detailed integration steps.
