# 🔗 watsonx Orchestrate Integration Guide

**A.E.G.I.S. Decision Service → watsonx Orchestrate**

---

## 📦 OpenAPI Specification File

**File**: [aegis-openapi.json](aegis-openapi.json)

This file contains the complete OpenAPI 3.1.0 specification for your A.E.G.I.S. Decision Service.

**Service Base URL**: `https://your-aegis-service-url.codeengine.appdomain.cloud`

---

## 🚀 Import to watsonx Orchestrate

### Step 1: Access watsonx Orchestrate

1. Login to IBM Cloud: https://cloud.ibm.com
2. Navigate to **watsonx Orchestrate**
3. Open your Orchestrate instance

### Step 2: Import the OpenAPI Spec

**Option A: Import from File**
1. Go to **Skills** → **Custom skills** → **Create**
2. Select **OpenAPI**
3. Click **Upload file**
4. Upload: `aegis-openapi.json`
5. Enter base URL: `https://your-aegis-service-url.codeengine.appdomain.cloud`
6. Click **Next**
7. Review the skill details
8. Click **Create**

**Option B: Import from URL**
1. Go to **Skills** → **Custom skills** → **Create**
2. Select **OpenAPI**
3. Select **Import from URL**
4. Enter: `https://your-aegis-service-url.codeengine.appdomain.cloud/openapi.json`
5. Click **Next**
6. Review and create

### Step 3: Verify the Skill

After import, you should see:
- **Skill name**: A.E.G.I.S. Decision Service API
- **Version**: 2.0.0
- **Operations**:
  - ✅ `POST /evaluate-incident` - Main decision endpoint
  - ✅ `GET /health` - Health check
  - ✅ `GET /version` - Version info

---

## 🎯 Key Endpoint: `/evaluate-incident`

This is the main endpoint for watsonx Orchestrate workflows.

### Input Schema:
```json
{
  "incident_text": "string (required, min 10 chars)",
  "category": "latency | storage | auth | unknown (optional)",
  "reporter_role": "SRE | Developer | Manager | Other (optional)",
  "context": {} // optional additional context
}
```

### Output Schema:
```json
{
  "analysis": "string - One-sentence summary",
  "recommended_action": "clear_logs | restart_service | run_diagnostics | escalate_to_human",
  "confidence_score": 0-100, // ⭐ USE THIS FOR BRANCHING
  "explanation": "string - Why this decision",
  "runbook_context": "string - Runbook used",
  "trace_id": "string - Request tracking",
  "model_id": "string - AI model used",
  "policy": {
    "auto_execute_threshold": 80,
    "escalate_threshold": 80
  }
}
```

### ⭐ Critical Field: `confidence_score`
- **>= 80**: High confidence - safe for auto-execution
- **< 80**: Low confidence - escalate to human

---

## 🔄 Create Orchestration Workflow

### Workflow Pattern: Confidence-Based Routing

```
┌─────────────────────────────────────┐
│  1. Incident Alert Received         │
│     (from monitoring system)        │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  2. Call A.E.G.I.S. Skill           │
│     POST /evaluate-incident         │
│     Input: incident_text, category  │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  3. Get Response                    │
│     Extract: confidence_score       │
│                recommended_action   │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  4. Conditional Branch              │
│     IF confidence_score >= 80       │
└─────┬───────────────┬───────────────┘
      │               │
      │ HIGH          │ LOW
      │ CONFIDENCE    │ CONFIDENCE
      ▼               ▼
┌─────────────┐  ┌──────────────────┐
│ AUTO PATH   │  │ HUMAN PATH       │
├─────────────┤  ├──────────────────┤
│ 5a. Execute │  │ 5b. Create       │
│    Action   │  │    Incident      │
│             │  │    Ticket        │
│ 6a. Log     │  │                  │
│    Success  │  │ 6b. Notify       │
│             │  │    SRE Team      │
│ 7a. Close   │  │                  │
│    Incident │  │ 7b. Wait for     │
│             │  │    Human Action  │
└─────────────┘  └──────────────────┘
```

### Workflow Steps in Orchestrate:

**1. Trigger**: Set up incident alert trigger
   - Slack notification
   - ServiceNow webhook
   - Email alert
   - Manual trigger for testing

**2. Call A.E.G.I.S. Skill**:
   - Skill: "A.E.G.I.S. Decision Service API"
   - Operation: "evaluate_incident"
   - Map inputs from trigger to request body

**3. Extract Variables**:
   - Create variable: `confidence_score` from response
   - Create variable: `recommended_action` from response
   - Create variable: `trace_id` for tracking

**4. Conditional Branch**:
   ```
   IF confidence_score >= 80
      THEN → AUTO_EXECUTION_PATH
      ELSE → HUMAN_ESCALATION_PATH
   ```

**5a. Auto Execution Path** (High Confidence):
   - Use `recommended_action` to determine next skill
   - Example mappings:
     - `clear_logs` → Call log cleanup automation
     - `restart_service` → Call service restart automation
     - `run_diagnostics` → Call diagnostic tool
   - Log action taken
   - Update incident status → "Auto-resolved"

**5b. Human Escalation Path** (Low Confidence):
   - Create incident ticket (ServiceNow, Jira, etc.)
   - Include `analysis`, `explanation`, `trace_id`
   - Set priority based on category
   - Notify SRE team (Slack, email, PagerDuty)
   - Attach runbook context for investigation

**6. Logging & Monitoring**:
   - Log all decisions to audit trail
   - Track auto-execution success rate
   - Monitor escalation patterns

---

## 🧪 Test Your Workflow

### Test Case 1: High Confidence (Should Auto-Execute)

**Input**:
```json
{
  "incident_text": "Disk usage at 95%. Log rotation failed at 3 AM. No user impact. Standard log cleanup applies.",
  "category": "storage"
}
```

**Expected Output**:
```json
{
  "confidence_score": 90,
  "recommended_action": "clear_logs"
}
```

**Expected Behavior**: Workflow takes AUTO_EXECUTION_PATH

---

### Test Case 2: Low Confidence (Should Escalate)

**Input**:
```json
{
  "incident_text": "Intermittent authentication failures reported by users. No clear pattern in logs. May be related to deployment 2 hours ago.",
  "category": "auth"
}
```

**Expected Output**:
```json
{
  "confidence_score": 70,
  "recommended_action": "escalate_to_human"
}
```

**Expected Behavior**: Workflow takes HUMAN_ESCALATION_PATH

---

## 📋 Workflow Variables to Map

### Input Variables (to A.E.G.I.S.):
| Variable | Source | Example |
|----------|--------|---------|
| incident_text | Alert message | "High CPU detected: 95%" |
| category | Alert type | "latency" |
| reporter_role | User role | "SRE" |

### Output Variables (from A.E.G.I.S.):
| Variable | Use For | Example |
|----------|---------|---------|
| confidence_score | Branching logic | 90 |
| recommended_action | Action routing | "clear_logs" |
| analysis | Ticket description | "Disk critically low" |
| explanation | Audit log | "Standard remediation" |
| trace_id | Tracking | "uuid-here" |

---

## 🔐 Authentication (If Needed)

Currently, the A.E.G.I.S. service is **publicly accessible** (no authentication required).

If you need to add authentication later:
1. Update Code Engine to require API keys
2. Add authentication in Orchestrate skill configuration
3. Use IBM Cloud IAM or custom API keys

---

## 🎬 Demo Workflow

### Quick Demo in Orchestrate:

**Workflow Name**: "Intelligent Incident Response with A.E.G.I.S."

**Steps**:
1. **Manual Trigger** → Ask user for incident description
2. **Call A.E.G.I.S.** → Send to /evaluate-incident
3. **Show Decision** → Display confidence_score and recommended_action
4. **Branch**:
   - High confidence → Show "Auto-executing [action]"
   - Low confidence → Show "Escalating to human because [explanation]"
5. **Log Result** → Save to audit trail

---

## 📊 Success Metrics

Track these metrics in your Orchestrate workflow:

| Metric | Description | Target |
|--------|-------------|--------|
| **Auto-Resolution Rate** | % of incidents auto-executed | > 60% |
| **Escalation Accuracy** | % of escalations that needed human | > 90% |
| **False Positives** | Auto-executions that caused issues | < 5% |
| **Response Time** | Time from alert to decision | < 10s |
| **SRE Time Saved** | Hours saved by automation | Track monthly |

---

## 🆘 Troubleshooting

### Issue: Skill import fails
**Solution**:
- Verify OpenAPI file is valid JSON
- Check base URL is accessible
- Ensure you have permissions in Orchestrate

### Issue: Workflow can't reach service
**Solution**:
- Test service URL directly: `curl https://your-aegis-service-url.codeengine.appdomain.cloud/health`
- Check Code Engine app is running: `ibmcloud ce app get -n aegis-decision-service`
- Verify network connectivity from Orchestrate

### Issue: Confidence scores seem wrong
**Solution**:
- Review runbook context in response
- Check if incident_text is descriptive enough
- Verify category is appropriate
- Consider tuning confidence threshold (currently 80)

---

## 📚 Additional Resources

### API Documentation:
- **Interactive Docs**: https://your-aegis-service-url.codeengine.appdomain.cloud/docs
- **OpenAPI Spec**: https://your-aegis-service-url.codeengine.appdomain.cloud/openapi.json

### Project Files:
- [README.md](README.md) - Technical documentation
- [DEPLOYMENT_SUCCESS.md](DEPLOYMENT_SUCCESS.md) - Deployment details
- [test-high-confidence.json](test-high-confidence.json) - Test case 1
- [test-low-confidence.json](test-low-confidence.json) - Test case 2

---

## ✨ Why This Integration Matters

### Business Value:
- **Reduces Alert Fatigue**: Only escalates when AI is uncertain
- **Faster Resolution**: Auto-executes standard remediations
- **Risk Mitigation**: Human oversight on ambiguous situations
- **Audit Trail**: Every decision tracked with confidence scores
- **Trust Building**: AI transparently shows its confidence

### Technical Value:
- **Structured Contracts**: Strict JSON schemas for reliability
- **Conditional Orchestration**: Enable/disable automation per use case
- **Extensible**: Easy to add new actions and categories
- **Observable**: Trace IDs for debugging
- **Production-Ready**: Error handling and safe fallbacks

---

## 🎯 Next Steps

1. ✅ Import OpenAPI spec to watsonx Orchestrate
2. ✅ Create simple test workflow
3. ✅ Test with both high and low confidence scenarios
4. ✅ Add conditional branching logic
5. ✅ Connect to real automation tools
6. ✅ Set up monitoring and metrics
7. ✅ Demo to stakeholders!

---

**OpenAPI File**: `aegis-openapi.json` (in current directory)
**Service URL**: `https://your-aegis-service-url.codeengine.appdomain.cloud`

**Status**: Ready for watsonx Orchestrate integration! 🚀

---

*IBM Dev Day Hackathon 2026*
*A.E.G.I.S. - AI That Knows When NOT to Act*
