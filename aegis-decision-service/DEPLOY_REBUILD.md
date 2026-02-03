# 🚀 Deployment & Rebuild Guide - IBM Cloud Code Engine

**Updated for Prompt v2: Ambiguity-Aware Confidence Scoring**

---

## Prerequisites

- ✅ Code pushed to GitHub repository
- ✅ IBM Cloud Code Engine project created
- ✅ No secrets or API keys committed to repository
- ✅ Environment variables configured in Code Engine

---

## Quick Rebuild Process

### Option 1: Trigger Rebuild from Code Engine UI

1. **Login to IBM Cloud Console**
   ```
   https://cloud.ibm.com
   ```

2. **Navigate to Code Engine**
   - Menu → Code Engine
   - Select your project: `watsonx-Hackathon Code Engine`
   - Region: `eu-gb`

3. **Select Your Application**
   - Click on `aegis-decision-service`

4. **Trigger Rebuild**
   - Click **"Configuration"** tab
   - Scroll to **"Code"** section
   - Click **"Edit and create new revision"**
   - Keep all settings the same
   - Click **"Deploy"**

   OR

   - If "Rebuild" button is visible, click it directly

5. **Monitor Deployment**
   - Go to **"Revisions"** tab
   - Watch build logs in real-time
   - Wait for status: **"Ready"**

---

### Option 2: Rebuild via IBM Cloud CLI

```bash
# 1. Login
ibmcloud login --apikey YOUR_API_KEY -r eu-gb

# 2. Target Code Engine project
ibmcloud ce project select --name "watsonx-Hackathon Code Engine"

# 3. Update application (triggers rebuild)
ibmcloud ce app update \
  --name aegis-decision-service \
  --build-source . \
  --build-context-dir . \
  --wait

# 4. Check status
ibmcloud ce app get --name aegis-decision-service
```

**Note**: If you're using Git build (not local source), use:
```bash
ibmcloud ce app update \
  --name aegis-decision-service \
  --build-source https://github.com/YOUR_USERNAME/aegis-agent \
  --build-commit main \
  --wait
```

---

## Git Workflow for Deployment

### 1. Make Changes Locally

```bash
# Edit files
# Example: src/aegis_service/watsonx_client.py

# Test locally with mock mode
MOCK_WATSONX=1 python test_ambiguity.py

# Verify tests pass
```

### 2. Commit and Push

```bash
# Stage changes
git add src/aegis_service/watsonx_client.py
git add test_ambiguity.py
git add DEPLOY_REBUILD.md

# Commit (NO SECRETS!)
git commit -m "Update prompt v2: ambiguity-aware confidence scoring"

# Push to GitHub
git push origin main
```

### 3. Rebuild in Code Engine

**If Auto-Build is Enabled:**
- Code Engine automatically detects push to `main`
- Build starts automatically
- Monitor in Code Engine UI

**If Manual Build:**
- Follow "Option 1" or "Option 2" above

---

## Environment Variables (Required)

These must be set in Code Engine application configuration:

```bash
WATSONX_APIKEY=<your-api-key>
WATSONX_PROJECT_ID=your_watsonx_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
```

**⚠️ NEVER commit these to Git!**

---

## Post-Deployment Verification

### 1. Health Check

```bash
curl https://your-aegis-service-url.codeengine.appdomain.cloud/health
```

**Expected:**
```json
{"status":"ok","message":null}
```

### 2. Version Check

```bash
curl https://your-aegis-service-url.codeengine.appdomain.cloud/version
```

**Expected:**
```json
{
  "service": "A.E.G.I.S. Decision Service",
  "version": "2.0.0",
  "model_id": "ibm/granite-3-8b-instruct",
  "watsonx_url": "https://us-south.ml.cloud.ibm.com"
}
```

### 3. Test Ambiguous Incident

```bash
curl -X POST https://your-aegis-service-url.codeengine.appdomain.cloud/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "Database latency is high but system metrics look normal."
  }'
```

**Expected:**
- `confidence_score` ≤ 60
- `recommended_action`: `"escalate_to_human"` or `"run_diagnostics"`

### 4. Test Clear Incident

```bash
curl -X POST https://your-aegis-service-url.codeengine.appdomain.cloud/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "Disk space is at 99% on Server-DB-01; /var/log growing rapidly."
  }'
```

**Expected:**
- `confidence_score` ≥ 90
- `recommended_action`: `"clear_logs"` or similar action

---

## Troubleshooting

### Build Fails

**Check build logs:**
```bash
ibmcloud ce app logs --name aegis-decision-service --build
```

**Common issues:**
- Missing `requirements.txt`
- Python version mismatch (use Python 3.11)
- Syntax errors in code

**Fix:**
- Review build logs
- Fix issues locally
- Test with `python -m py_compile src/aegis_service/*.py`
- Push fixes and rebuild

### Application Won't Start

**Check application logs:**
```bash
ibmcloud ce app logs --name aegis-decision-service --tail 50
```

**Common issues:**
- Missing environment variables
- Invalid API key
- Port configuration (should be auto-configured)

**Fix:**
- Verify all environment variables are set in Code Engine UI
- Test API key: `ibmcloud login --apikey YOUR_KEY`
- Check application configuration in UI

### Deployment Successful but watsonx.ai Errors

**Check logs:**
```bash
ibmcloud ce app logs --name aegis-decision-service --tail 100 | grep -i error
```

**Common issues:**
- Wrong `WATSONX_URL` (use `us-south` not `eu-gb`)
- Project ID mismatch
- API key doesn't have access to project

**Fix:**
- Update environment variables in Code Engine UI
- Verify project ID at: https://dataplatform.cloud.ibm.com/projects
- Test connection: hit `/version` endpoint

---

## Security Checklist

Before deployment:

- [ ] No API keys in code
- [ ] No secrets in Git history
- [ ] `.gitignore` includes sensitive files
- [ ] Environment variables set in Code Engine (not in code)
- [ ] API key has minimal required permissions

After deployment:

- [ ] Health endpoint responds
- [ ] Version endpoint shows correct config
- [ ] Test endpoints work as expected
- [ ] Application logs don't leak sensitive data
- [ ] OpenAPI spec doesn't expose internals

---

## Rollback Procedure

If new deployment has issues:

### Via UI:

1. Go to Code Engine → Applications → aegis-decision-service
2. Click **"Revisions"** tab
3. Find previous working revision
4. Click **"⋮"** menu → **"Route traffic to this revision"**
5. Set traffic to 100%
6. Click **"Save"**

### Via CLI:

```bash
# List revisions
ibmcloud ce app revisions --name aegis-decision-service

# Route traffic to previous revision
ibmcloud ce app update \
  --name aegis-decision-service \
  --revision REVISION_NAME
```

---

## Monitoring After Deployment

### Check Application Metrics

```bash
# Get application status
ibmcloud ce app get --name aegis-decision-service

# View recent logs
ibmcloud ce app logs --name aegis-decision-service --tail 100

# Monitor in real-time
ibmcloud ce app logs --name aegis-decision-service --follow
```

### Key Metrics to Watch

- **Response time**: Should be 3-5 seconds
- **Error rate**: Should be <1%
- **Confidence scores**: Watch for proper ambiguity detection
- **Action distribution**: ~60% auto-execute, ~40% escalate

---

## What Changed in Prompt v2

### Updated System Prompt

- **Ambiguity detection rules**: Conflicting signals cap confidence at 60
- **Confidence scoring rubric**: Clear 90-100 vs ambiguous 30-69
- **Auto-resolution guard**: No auto-resolve language if confidence <90
- **Policy enforcement**: Stricter action validation

### New Validation Logic

- `_detect_ambiguity()`: Pattern matching for conflicting signals
- Enhanced `_validate_decision()`: Caps confidence for ambiguous incidents
- Auto-resolution language detection
- Logs all policy enforcement actions

### Mock Mode for Testing

- `MOCK_WATSONX=1`: Use simulated responses
- No API calls required for local testing
- Simulates both clean JSON and JSON with extra text

---

## Files Modified

```
src/aegis_service/watsonx_client.py  # Core logic updated
test_ambiguity.py                     # New test script
DEPLOY_REBUILD.md                     # This file
README.md                             # Updated with v2 info
```

---

## Next Steps After Deployment

1. **Test in watsonx Orchestrate**
   - Import updated OpenAPI spec
   - Test confidence-based branching
   - Verify ambiguous incidents route correctly

2. **Update Documentation**
   - Update demo scripts with new scenarios
   - Add ambiguity examples to presentation

3. **Monitor Production**
   - Watch for any unexpected escalations
   - Review confidence score distribution
   - Collect feedback from SRE team

---

**Deployment URL**: https://your-aegis-service-url.codeengine.appdomain.cloud

**Status**: Ready for redeploy with Prompt v2 🚀

---

*Last updated: 2026-01-31*
*Prompt Version: v2 - Ambiguity-Aware Confidence*
