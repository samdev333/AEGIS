# 🔗 watsonx Orchestrate Setup Guide

This guide walks you through integrating the A.E.G.I.S. Decision Service with watsonx Orchestrate to create the complete governed agentic workflow.

---

## 📋 Prerequisites

Before starting:
- [ ] Decision Service deployed to IBM Code Engine with a public URL
- [ ] URL tested and working (`curl https://your-url.appdomain.cloud`)
- [ ] `openapi-spec.yaml` updated with your Code Engine URL
- [ ] Access to watsonx Orchestrate (trial or paid account)

---

## Part 1: Import Decision Service Skill

### Step 1: Access watsonx Orchestrate

1. Go to [watsonx Orchestrate](https://www.ibm.com/products/watsonx-orchestrate)
2. Log in with your IBM Cloud credentials
3. Navigate to your workspace

### Step 2: Import OpenAPI Specification

1. In Orchestrate, go to **Skills** (left sidebar)
2. Click **Add Skill** (top right)
3. Select **Import OpenAPI**
4. Choose **Upload file**
5. Select your `openapi-spec.yaml` file
6. Click **Import**

Orchestrate will parse the OpenAPI spec and create a skill called **"A.E.G.I.S. Decision Service API"** with two operations:
- Health Check (GET /)
- **Evaluate Incident** (POST /evaluate-incident) ← This is what we'll use

### Step 3: Test the Skill

1. Find the newly imported skill in your Skills list
2. Click on the skill name
3. Click **Test** for the "Evaluate Incident" operation
4. Enter test data:
```json
{
  "incident_text": "Test incident: High database latency detected",
  "category": "latency"
}
```
5. Click **Run**
6. Verify you get a JSON response with `confidence_score`, `recommended_action`, etc.

✅ If successful, your Decision Service is now a usable skill in Orchestrate!

---

## Part 2: Create the Orchestration Workflow

Now we'll build the complete A.E.G.I.S. workflow using skills and conditional logic.

### Step 1: Create a New Skill Flow

1. In Orchestrate, go to **Skill Flows** (left sidebar)
2. Click **Create skill flow**
3. Name it: `A.E.G.I.S. Incident Response`
4. Description: `Automated incident evaluation with confidence-based routing`
5. Click **Create**

### Step 2: Build the Flow (Step-by-Step)

We'll create a flow with 5 components:

```
1. Incident Intake
2. Call Decision Service
3. Conditional Branch (confidence >= 80?)
   ├─ Auto-Execute Path
   └─ Human Escalation Path
4. Merge paths
5. Resolution Summary
```

#### Component 1: Incident Intake

**Purpose**: Collect incident details from the user

1. Drag a **Form** block onto the canvas
2. Configure the form:
   - **Name**: `Incident Intake`
   - **Add fields**:
     - Field 1:
       - Label: `Incident Description`
       - Type: `Text area`
       - Variable name: `incident_text`
       - Required: ✅
     - Field 2:
       - Label: `Category`
       - Type: `Dropdown`
       - Variable name: `category`
       - Options: `latency`, `storage`, `auth`, `unknown`
       - Default: `unknown`

#### Component 2: Call Decision Service

**Purpose**: Send incident to AI for analysis

1. Drag your **A.E.G.I.S. Decision Service** skill onto the canvas
2. Connect it to the Incident Intake form output
3. Configure the skill:
   - Operation: `Evaluate Incident` (POST /evaluate-incident)
   - **Input mapping**:
     - `incident_text` → `{{incident_text}}` (from form)
     - `category` → `{{category}}` (from form)
   - **Output mapping**:
     - Store the entire response in a variable: `decision_result`

**Important**: Make sure to capture these fields from the response:
- `decision_result.confidence_score`
- `decision_result.recommended_action`
- `decision_result.analysis`
- `decision_result.explanation`

#### Component 3: Conditional Branch

**Purpose**: Route based on confidence score (THE CRITICAL PIECE)

1. Drag a **Branch** block onto the canvas
2. Connect it to the Decision Service output
3. Configure the branch:
   - **Condition type**: `Expression`
   - **Branch 1** (Auto-Execute):
     - Name: `High Confidence`
     - Condition: `{{decision_result.confidence_score >= 80}}`
   - **Branch 2** (Human Review):
     - Name: `Low Confidence`
     - Condition: `{{decision_result.confidence_score < 80}}`

**Judge Gold**: This is the visible proof that Orchestrate is making decisions based on AI confidence.

#### Component 4a: Auto-Execute Path

**Purpose**: Handle high-confidence incidents automatically

1. On the "High Confidence" branch, add a **Skill** block
2. You can use a mock skill or a custom skill:
   - **Option A (Quick Demo)**: Use a **Set Variable** block
     - Variable: `execution_result`
     - Value: `Auto-executed: {{decision_result.recommended_action}}`
   - **Option B (More Complete)**: Create a custom skill that logs:
     - Action taken: `{{decision_result.recommended_action}}`
     - Timestamp
     - Status: `success`

#### Component 4b: Human Escalation Path

**Purpose**: Pause and show incident to human (THE WINNING MOMENT)

1. On the "Low Confidence" branch, add a **Form** block
2. Configure as a Human Review form:
   - **Name**: `Human Review Required`
   - **Description**: `This incident requires human judgment`
   - **Display fields** (read-only):
     - Show `analysis`: `{{decision_result.analysis}}`
     - Show `recommended_action`: `{{decision_result.recommended_action}}`
     - Show `confidence_score`: `{{decision_result.confidence_score}}`
     - Show `explanation`: `{{decision_result.explanation}}`
   - **Input field** (editable):
     - Label: `Approved Action`
     - Type: `Dropdown`
     - Variable name: `human_approved_action`
     - Options: `clear_logs`, `restart_service`, `run_diagnostics`, `escalate_further`
   - **Button**: `Approve and Continue`

This form **pauses the workflow** and waits for human input. This is the human-in-the-loop control.

3. After the form, add an **Execute Action** skill (same as auto-execute)
   - Action: `{{human_approved_action}}`
   - Status: `human_approved`

#### Component 5: Merge and Resolution Summary

1. Drag a **Merge** block to combine both paths
2. After the merge, add a **Message** block:
   - **Name**: `Resolution Summary`
   - **Message**:
```
Incident Resolved

Analysis: {{decision_result.analysis}}
Action Taken: {{execution_result}}
Confidence: {{decision_result.confidence_score}}
Approval: {{#if human_approved_action}}Human Approved{{else}}Auto-Executed{{/if}}
```

---

## Part 3: Test the Complete Flow

### Test Case 1: High Confidence (Auto-Execute)

1. In Orchestrate, click **Test** on your skill flow
2. Enter incident details:
   - **Incident Description**: `Application logs consuming 95% disk space. Log rotation failed. No user impact.`
   - **Category**: `storage`
3. Click **Submit**

**Expected behavior**:
- Decision Service returns confidence ~95
- Flow takes "High Confidence" branch
- Action auto-executes
- Summary shows "Auto-Executed"
- **No human pause**

### Test Case 2: Low Confidence (Human Escalation)

1. Click **Test** again
2. Enter incident details:
   - **Incident Description**: `Intermittent authentication failures reported by users. No clear pattern. May be related to recent deployment.`
   - **Category**: `auth`
3. Click **Submit**

**Expected behavior**:
- Decision Service returns confidence ~45
- Flow takes "Low Confidence" branch
- **Workflow pauses** at Human Review form
- Human sees analysis, confidence, and explanation
- Human selects approved action
- Flow resumes
- Summary shows "Human Approved"

✅ **THIS IS YOUR DEMO MOMENT** - show judges the workflow pausing and requiring approval.

---

## Part 4: Publish and Deploy

### Option A: Internal Testing

1. Save your skill flow
2. Test with your team
3. Iterate on the conditional logic and messaging

### Option B: Publish for Organization

1. In your skill flow, click **Publish**
2. Set permissions (who can invoke this flow)
3. The flow becomes available to authorized users in your organization
4. Users can invoke via:
   - Orchestrate UI
   - Slack integration (if configured)
   - API calls

---

## Part 5: Advanced Enhancements (Optional)

These are **NOT required** for the hackathon but show production-readiness:

### Enhancement 1: Audit Logging

Add a skill that logs every decision to a database:
- Incident text
- Confidence score
- Action taken
- Approval path
- Timestamp

### Enhancement 2: Metrics Dashboard

Create a skill flow that queries recent incidents and shows:
- Auto-execute rate
- Average confidence scores
- Most common incident types

### Enhancement 3: Feedback Loop

After resolution, add a form asking:
- Was the action appropriate? (Yes/No)
- Additional comments

Use this to tune confidence thresholds over time.

---

## Part 6: Troubleshooting

### Issue: "Skill import failed"

**Solution**:
1. Validate your OpenAPI spec at [editor.swagger.io](https://editor.swagger.io)
2. Ensure the `servers` URL in the spec is correct
3. Check that your Decision Service is accessible from Orchestrate's network

### Issue: "Branch condition not working"

**Solution**:
1. Ensure `confidence_score` is properly mapped from the Decision Service response
2. Use Orchestrate's expression editor to test: `{{decision_result.confidence_score}}`
3. Check data types - confidence_score must be an integer, not a string

### Issue: "Human review form not pausing workflow"

**Solution**:
1. Ensure the form is configured as a "User Task" (not just a display)
2. Check that the form has an input field (e.g., `human_approved_action`)
3. Verify there's a submit button configured

### Issue: "Decision Service returns 500 error"

**Solution**:
1. Check Code Engine logs: `ibmcloud ce app logs --name aegis-decision-service`
2. Verify environment variables are set in Code Engine
3. Test the service directly with curl to isolate the issue

---

## 🎯 Validation Checklist

Before the hackathon demo, verify:

- [ ] Decision Service skill imported successfully
- [ ] Skill flow created with all 5 components
- [ ] High-confidence path routes to auto-execute
- [ ] Low-confidence path pauses at human review
- [ ] Both paths merge to resolution summary
- [ ] Test case 1 (high confidence) works end-to-end
- [ ] Test case 2 (low confidence) pauses for human approval
- [ ] Architecture diagram shows Orchestrate as control plane
- [ ] You can explain the conditional branching logic

---

## 📊 Visual Diagram of Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    watsonx Orchestrate                      │
│                                                             │
│  ┌──────────────┐                                          │
│  │Incident Intake│ (Form: text + category)                 │
│  └───────┬──────┘                                          │
│          │                                                  │
│          ▼                                                  │
│  ┌──────────────────┐                                      │
│  │Decision Service  │ (Calls your Code Engine API)         │
│  │ POST /evaluate   │                                       │
│  └───────┬──────────┘                                      │
│          │ Returns: {confidence_score, action, ...}         │
│          ▼                                                  │
│  ┌──────────────────┐                                      │
│  │  Conditional     │                                      │
│  │  Branch          │                                      │
│  │ confidence >= 80?│                                      │
│  └─────┬────────┬───┘                                      │
│        │        │                                          │
│    YES │        │ NO                                       │
│        │        │                                          │
│        ▼        ▼                                          │
│  ┌─────────┐  ┌──────────────┐                           │
│  │Auto-Exec│  │Human Review  │ ⬅ WORKFLOW PAUSES HERE    │
│  │ Action  │  │Form (Approval)│                           │
│  └────┬────┘  └──────┬───────┘                           │
│       │              │                                     │
│       └──────┬───────┘                                     │
│              ▼                                             │
│      ┌───────────────┐                                    │
│      │Resolution     │                                    │
│      │Summary        │                                    │
│      └───────────────┘                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏆 Judge Narration for This Setup

When explaining your Orchestrate setup to judges:

> "watsonx Orchestrate is the control plane for A.E.G.I.S.
>
> It owns the workflow state, executes the conditional branching logic, and enforces human-in-the-loop governance.
>
> **[Point to flow diagram]**
>
> When an incident comes in, Orchestrate calls our Decision Service, which uses Granite to analyze the incident and return a confidence score.
>
> **[Point to branch node]**
>
> Orchestrate then evaluates the confidence score and routes accordingly:
> - High confidence (≥80) flows to auto-execution
> - Low confidence (<80) **pauses** the workflow and presents the incident to a human reviewer
>
> **[Point to human form]**
>
> The human sees the AI's analysis, the confidence score, and the explanation. They can approve, modify, or escalate further.
>
> Once approved, the workflow resumes.
>
> **[Point to merge]**
>
> Both paths converge to a resolution summary that logs what happened, how it was decided, and who approved it.
>
> This pattern - **AI recommendation + confidence-based routing + human governance** - is what makes agentic workflows safe for enterprises."

---

## 📚 Additional Resources

- [watsonx Orchestrate Documentation](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [Skill Flow Builder Guide](https://www.ibm.com/docs/en/watsonx/watson-orchestrate/current?topic=skills-building-skill-flows)
- [OpenAPI Integration Guide](https://www.ibm.com/docs/en/watsonx/watson-orchestrate/current?topic=skills-importing-openapi-specifications)

---

**You now have a complete governed agentic workflow using watsonx Orchestrate and watsonx.ai!**
