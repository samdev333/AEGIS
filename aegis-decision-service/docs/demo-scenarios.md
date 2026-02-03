# 🎬 A.E.G.I.S. Demo Scenarios

This document provides complete demo scripts for presenting A.E.G.I.S. to hackathon judges.

**Demo Duration**: 3-5 minutes
**Goal**: Show the contrast between auto-execution and human escalation

---

## 🎯 Demo Strategy

The winning moment is **Scenario B** - when the agent escalates to human. This proves the system is enterprise-safe.

**Structure**:
1. Quick context (30 seconds)
2. Scenario A: Auto-execution (1 minute)
3. **Scenario B: Human escalation (2 minutes)** ⭐
4. Architecture wrap-up (1 minute)

---

## Opening Statement (30 seconds)

> "A.E.G.I.S. demonstrates a critical enterprise AI pattern: agents that know when NOT to act.
>
> Traditional automation fails when faced with ambiguity. A.E.G.I.S. uses IBM watsonx.ai Granite models to analyze incidents, calculate confidence scores, and automatically route decisions based on risk.
>
> High confidence situations are auto-executed. Low confidence situations escalate to humans with full context.
>
> Let me show you both paths."

---

## Scenario A: High Confidence - Auto Execution

### Context
"First, a routine incident that's safe to automate."

### Incident Details
```
Title: Disk Space Critical
Description: Application logs show disk usage at 95%. Log rotation service failed at 3 AM. No active user sessions currently affected. Standard log cleanup procedures apply.
Category: storage
```

### Expected AI Response
```json
{
  "analysis": "Disk space critically low due to failed log rotation",
  "recommended_action": "clear_logs",
  "confidence_score": 95,
  "explanation": "Clear cause identified with standard remediation. Safe to auto-execute log cleanup."
}
```

### Narration

> "The incident is submitted to A.E.G.I.S.
>
> The Decision Service calls watsonx.ai Granite, which analyzes the incident with runbook context.
>
> **[Point to confidence_score: 95]**
>
> Confidence is 95 - this is a well-understood problem with standard remediation.
>
> **[Point to Orchestrate branching]**
>
> watsonx Orchestrate sees confidence ≥ 80 and routes to the auto-execution path.
>
> Logs are cleared. Disk space recovers. Incident resolved in under 30 seconds.
>
> **This is efficiency** - the agent handles routine issues without human intervention."

### Judge Takeaway
✅ System works for standard cases
✅ watsonx Orchestrate performs routing
✅ Granite provides the intelligence

---

## Scenario B: Low Confidence - Human Escalation ⭐

**THIS IS YOUR WINNING MOMENT**

### Context
"Now let me show you why this matters for enterprises."

### Incident Details
```
Title: Authentication Failures
Description: Multiple users reporting intermittent authentication failures over the past hour. No clear pattern in the logs. May be related to the deployment we pushed 2 hours ago, but not confirmed. Some users can log in successfully while others cannot.
Category: auth
```

### Expected AI Response
```json
{
  "analysis": "Authentication failures with unclear root cause",
  "recommended_action": "escalate_to_human",
  "confidence_score": 45,
  "explanation": "Intermittent auth failures with possible deployment correlation require human investigation. Risk of impacting user access if automated action taken without full context."
}
```

### Narration (THIS IS CRITICAL - DELIVER SLOWLY)

> "The incident is submitted to A.E.G.I.S.
>
> **[Pause for effect]**
>
> The Decision Service calls Granite, which analyzes the incident.
>
> But this time, the AI recognizes several risk factors:
> - Intermittent failures, not consistent
> - Unclear correlation with recent deployment
> - Potential user impact if wrong action taken
>
> **[Point to confidence_score: 45]**
>
> Confidence is only 45.
>
> **[Point to Orchestrate branching - THIS IS THE MOMENT]**
>
> watsonx Orchestrate sees confidence < 80 and **stops**.
>
> The workflow **pauses** and presents the incident to a human reviewer with full context:
> - The AI's analysis
> - Why it's uncertain
> - What it considered recommending
>
> **[Gesture to human approval step]**
>
> The human sees this isn't standard. They approve a diagnostic run instead of auto-remediation.
>
> The workflow resumes with the human-approved action.
>
> **This is governance** - the agent knows when it doesn't know.
>
> This is what makes agentic AI safe for enterprises."

### Judge Takeaway
✅✅✅ System demonstrates judgment - not just automation
✅✅✅ watsonx Orchestrate provides human-in-the-loop control
✅✅✅ Granite reasoning is visible and explainable
✅✅✅ **This is the "enterprise-safe AI" pattern judges are looking for**

---

## Architecture Wrap-Up (1 minute)

After showing both scenarios, point to your architecture diagram:

> "Let me show you how this works technically.
>
> **[Point to watsonx Orchestrate]**
> watsonx Orchestrate is the control plane. It owns workflow state, executes branching logic, and enforces governance policies.
>
> **[Point to Decision Service]**
> The Python Agent ADK Decision Service encapsulates the AI reasoning. It calls watsonx.ai Granite models and returns structured JSON with confidence scores.
>
> **[Point to conditional branch]**
> Orchestrate uses the confidence_score to route decisions. High confidence flows to auto-execution. Low confidence flows to human review.
>
> **[Point to runbook context]**
> The Decision Service integrates runbook context - in production, this would connect to Langflow or a RAG system for institutional knowledge.
>
> This architecture is modular, testable, and follows IBM's best practices for governed agentic workflows."

---

## Test Scenarios (For Testing Before Demo)

### Test Case 1: Clear Auto-Execute
```bash
curl -X POST https://your-url.appdomain.cloud/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "Application logs consuming 95% disk space. Log rotation failed. No user impact.",
    "category": "storage"
  }'
```

**Expected**: `confidence_score` >= 80, `recommended_action` = "clear_logs"

### Test Case 2: Clear Escalation
```bash
curl -X POST https://your-url.appdomain.cloud/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "Intermittent authentication failures reported by multiple users. No clear pattern. May be related to recent deployment.",
    "category": "auth"
  }'
```

**Expected**: `confidence_score` < 80, `recommended_action` = "escalate_to_human"

### Test Case 3: Ambiguous (Should Escalate)
```bash
curl -X POST https://your-url.appdomain.cloud/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "System acting weird. Not sure what is wrong. Please help.",
    "category": "unknown"
  }'
```

**Expected**: `confidence_score` < 50, `recommended_action` = "escalate_to_human"

### Test Case 4: Database Latency (Moderate Confidence)
```bash
curl -X POST https://your-url.appdomain.cloud/evaluate-incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_text": "Database queries taking 2000ms instead of usual 50ms. No error messages. Started 30 minutes ago.",
    "category": "latency"
  }'
```

**Expected**: `confidence_score` 60-79, `recommended_action` = "run_diagnostics" or "escalate_to_human"

---

## Backup Talking Points (If Asked)

### "How does this handle false positives?"

> "Great question. The confidence threshold is tunable. We set it at 80 for this demo, but enterprises can adjust based on their risk tolerance. More conservative organizations might set it at 90. The key is that the decision is **explicit and auditable** - not hidden in a black box."

### "What if the AI makes a wrong recommendation?"

> "This is exactly why we have the confidence score and human escalation. Even when the AI recommends an action, if confidence is low, a human reviews it. Additionally, all decisions are logged in watsonx Orchestrate, creating an audit trail. Enterprises can review patterns and tune the system over time."

### "How does this scale to thousands of incidents?"

> "The Decision Service is stateless and horizontally scalable on Code Engine. watsonx Orchestrate handles workflow state management. For high-confidence incidents, the system auto-executes immediately. Low-confidence incidents are queued for human review, preventing reviewer overload. The confidence-based routing naturally load-balances the work."

### "What about Langflow integration?"

> "In this POC, runbook context is simulated with in-memory lookups. In production, we'd connect to Langflow for vector-based retrieval of historical runbooks and resolution patterns. The Decision Service API already accepts a `runbook_context` parameter, so integration is straightforward. This demonstrates **context-aware agents** without requiring a full RAG system for the hackathon."

---

## Timing Your Demo

| Section | Duration | Critical? |
|---------|----------|-----------|
| Opening statement | 30s | ✅ Yes |
| Scenario A (auto) | 1 min | Somewhat |
| **Scenario B (escalate)** | **2 min** | **✅✅✅ CRITICAL** |
| Architecture | 1 min | ✅ Yes |
| Q&A | 1-2 min | - |

**Total**: 3-5 minutes + Q&A

---

## Visual Aids (If Allowed)

If you can show your screen during the demo:

1. **Start with**: watsonx Orchestrate workflow diagram
2. **During Scenario A**: Show the JSON response with high confidence
3. **During Scenario B**: Show the human approval pause in Orchestrate
4. **End with**: Architecture diagram

If no screen sharing, practice describing the flow verbally with hand gestures to indicate branching logic.

---

## Final Demo Checklist

Before your presentation:

- [ ] Test both scenarios against your deployed service
- [ ] Verify confidence scores are in expected ranges (>80 for Scenario A, <80 for Scenario B)
- [ ] Practice the Scenario B narration (the winning moment)
- [ ] Have your architecture diagram ready
- [ ] Test your service URL is accessible
- [ ] Prepare backup answers to common questions

---

## The One Line That Wins

If you can only say one thing, say this:

> **"A.E.G.I.S. proves that enterprise AI isn't about replacing humans - it's about AI knowing when to defer to humans."**

This is what IBM judges want to hear.

---

**Good luck! You've built something that demonstrates real enterprise value.**
