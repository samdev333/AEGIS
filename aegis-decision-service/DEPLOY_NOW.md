# 🚀 Deploy A.E.G.I.S. NOW - 10 Minute Guide

**Everything is configured and ready. Let's deploy using IBM Cloud Console.**

---

## ✅ Pre-Flight Check

Your configuration is ready:
- ✅ API Key: Configured
- ✅ Project ID: Configured (your_watsonx_project_id_here)
- ✅ Region: EU-GB
- ✅ Code Engine Project: watsonx-Hackathon Code Engine
- ✅ All source files ready

---

## 🎯 Deploy in 4 Steps (10 minutes total)

### STEP 1: Access Code Engine (2 min)

1. **Open browser**: https://cloud.ibm.com/codeengine/overview
2. **Login** with your IBM credentials
3. **Click** on your project: **"watsonx-Hackathon Code Engine"**

### STEP 2: Create Application (3 min)

1. **Click "Applications"** in the left sidebar
2. **Click "Create"** button (top right)

3. **General tab:**
   - Name: `aegis-decision-service`
   - Choose: **"Source code"**

4. **Code tab:**
   - Click: **"Specify build details"**
   - Source: **"Local"**
   - Click: **"Choose folder"** or **"Choose files"**
   - **Select**: Browse to `your_project_directory` and select the ENTIRE folder
   - **Upload**: Wait for upload to complete

5. **Build tab:**
   - Strategy: **"Dockerfile"** (select from dropdown)
   - Dockerfile name: `Dockerfile` (should auto-detect)

6. **Resources tab:**
   - **Port**: `5000`
   - **CPU**: `0.5 vCPU`
   - **Memory**: `1 GB`
   - **Min instances**: `1`
   - **Max instances**: `3`

### STEP 3: Add Environment Variables (2 min)

**IMPORTANT**: Click "Environment variables" tab and add these 5 variables:

**Copy-paste these exact values:**

1. **Variable 1:**
   - Name: `WATSONX_APIKEY`
   - Value: `your_ibm_cloud_api_key_here`

2. **Variable 2:**
   - Name: `WATSONX_PROJECT_ID`
   - Value: `your_watsonx_project_id_here`

3. **Variable 3:**
   - Name: `WATSONX_URL`
   - Value: `https://eu-gb.ml.cloud.ibm.com`

4. **Variable 4:**
   - Name: `WATSONX_MODEL_ID`
   - Value: `ibm/granite-3-8b-instruct`

5. **Variable 5:**
   - Name: `PORT`
   - Value: `5000`

### STEP 4: Deploy! (3 min)

1. **Click "Create"** at the bottom
2. **Wait 3-5 minutes** for build and deployment
   - You'll see a progress indicator
   - Status will change from "Deploying" → "Ready"
3. **Copy the URL** when ready (top of application page)

---

## 🧪 Test Your Deployment

### Your URL will look like:
```
https://aegis-decision-service.xxxxxxxxx.eu-gb.codeengine.appdomain.cloud
```

### Test Commands (replace YOUR_URL):

**1. Health Check:**
```bash
curl https://YOUR_URL/health
```
Expected: `{"status":"ok"}`

**2. Interactive API Docs:**
Open in browser: `https://YOUR_URL/docs`

**3. High Confidence Test:**
```bash
curl -X POST https://YOUR_URL/evaluate-incident \
  -H "Content-Type: application/json" \
  -d "{\"incident_text\":\"Disk at 95%. Log rotation failed. No user impact.\",\"category\":\"storage\"}"
```
Expected: `confidence_score` ~95, `recommended_action` = `"clear_logs"`

**4. Low Confidence Test (Should Escalate):**
```bash
curl -X POST https://YOUR_URL/evaluate-incident \
  -H "Content-Type: application/json" \
  -d "{\"incident_text\":\"Intermittent auth failures. No pattern.\",\"category\":\"auth\"}"
```
Expected: `confidence_score` ~45, `recommended_action` = `"escalate_to_human"`

---

## ✅ Success Checklist

After deployment:
- [ ] Application status shows "Ready"
- [ ] URL accessible (health check works)
- [ ] `/docs` shows interactive API
- [ ] High confidence test returns ~95 confidence
- [ ] Low confidence test escalates to human
- [ ] No errors in application logs

---

## 🔧 Troubleshooting

### "Upload Failed"
- **Try creating a ZIP file** of the `aegis-agent` folder first
- Upload the ZIP instead

### "Build Failed"
- Check: All files uploaded correctly
- Check: Dockerfile exists in root
- **Solution**: Click "Rebuild" button

### "Application Crashes"
- Check: All 5 environment variables set correctly
- Check: PORT is exactly `5000`
- **View logs**: In Code Engine → Your app → Logs tab

### "watsonx.ai Connection Error"
- Verify API key has no extra spaces
- Verify Project ID is correct
- Check region URL: `https://eu-gb.ml.cloud.ibm.com`

---

## 📊 Alternative: Upload as ZIP

If folder upload doesn't work:

1. **Create ZIP**:
   - Right-click `aegis-agent` folder
   - Send to → Compressed (zipped) folder
   - Name it: `aegis-agent.zip`

2. **Upload ZIP** in Code Engine create application flow

---

## 🎉 What Happens Next

Once deployed, you'll have:

✅ **Live Decision Service URL**
✅ **AI-powered incident analysis**
✅ **Confidence-based routing**
✅ **Interactive API docs at /docs**
✅ **Ready for watsonx Orchestrate**

---

## 📝 After Deployment

1. **Save your URL** somewhere safe
2. **Test all endpoints** above
3. **Export OpenAPI**:
   ```bash
   python scripts/export_openapi.py
   ```
4. **Update openapi.yaml** with your URL
5. **Import to watsonx Orchestrate**

---

## 🆘 Still Having Issues?

**Web Console Not Working?**
Try these alternatives:

### Option A: Manual Upload to GitHub
1. Push code to GitHub
2. Use GitHub as source in Code Engine

### Option B: Container Registry
1. Build Docker image locally
2. Push to IBM Container Registry
3. Deploy from registry

---

## 🎯 Quick Reference Card

```
Project: watsonx-Hackathon Code Engine
Region: eu-gb
App Name: aegis-decision-service
Port: 5000
CPU: 0.5
Memory: 1GB
Min: 1
Max: 3

Environment Variables (5):
WATSONX_APIKEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
WATSONX_URL=https://eu-gb.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
PORT=5000
```

---

**Ready? Go to https://cloud.ibm.com/codeengine/overview and deploy!**

**Reply with your URL once deployed and I'll help you test it! 🚀**
