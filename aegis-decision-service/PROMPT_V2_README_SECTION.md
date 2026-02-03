## 🧠 Prompt v2: Ambiguity-Aware Confidence

**Updated**: 2026-01-31

### What Changed

Version 2 of the decision service prompt includes enhanced ambiguity detection and stricter confidence scoring to prevent false-positive auto-executions.

### Key Improvements

#### 1. Ambiguity Detection Patterns

The system now detects and handles ambiguous incidents:

- **Conflicting signals**: "latency high but metrics normal"
- **Unclear root cause**: "no clear pattern in logs"
- **Multiple possibilities**: "could be X, might be Y"
- **Uncertainty markers**: Multiple instances of "may", "possibly", "unclear"

**Action**: Caps confidence at ≤60 and forces escalation/diagnostics

#### 2. Refined Confidence Scoring Rubric

| Score Range | Criteria | Example |
|-------------|----------|---------|
| **90-100** | Clear, common issue with strong indicators and low risk. All signals align. | "Disk 99% full, /var/log 50GB" |
| **70-89** | Likely issue but missing 1-2 key confirming signals or minor ambiguity. | "High latency, CPU 90%, but logs unclear" |
| **30-69** | Ambiguous, conflicting signals, OR multiple plausible root causes. | "Latency high but metrics normal" |
| **0-29** | Unknown, high risk, insufficient information, or safety-critical uncertainty. | "System crashed, no logs available" |

#### 3. Stricter Policy Enforcement

- **Confidence < 80**: Action MUST be `escalate_to_human` OR `run_diagnostics`
- **Confidence < 90**: Explanation MUST NOT imply auto-resolution
- **Ambiguous incident**: Confidence capped at 60 regardless of model output

#### 4. Enhanced JSON Parsing

- Handles model output with extra text (e.g., "Here's the analysis: {...}")
- 5-layer parsing strategy with defensive fallbacks
- Validates all fields and types
- Safe fallback on any parsing failure

### Testing with Mock Mode

For local development without API calls:

```bash
# Enable mock mode
export MOCK_WATSONX=1

# Run test suite
python test_ambiguity.py

# Test specific scenarios
python test_ambiguity.py --verbose
```

Mock mode simulates:
- Clean JSON responses
- JSON wrapped in extra text
- Ambiguous vs clear incidents

### Demo Scenarios with Prompt v2

#### Recommended Demo Flow for watsonx Orchestrate

**1. Show Ambiguous Incident** (New in v2)
```
Input: "Database latency is high but system metrics look normal."

Expected Output:
- confidence_score: ≤60
- recommended_action: "run_diagnostics" or "escalate_to_human"
- Orchestrate workflow: PAUSES for human review

Demo Point: "Notice how the AI detected conflicting signals and
            refused to auto-execute despite symptoms present."
```

**2. Show Clear Incident**
```
Input: "Disk space at 99% on Server-DB-01; /var/log 50GB."

Expected Output:
- confidence_score: ≥90
- recommended_action: "clear_logs"
- Orchestrate workflow: Auto-executes cleanup

Demo Point: "Clear cause, standard remediation, high confidence."
```

**3. Show Threshold Behavior**
```
Input: "Application crashed twice. May be memory-related."

Expected Output:
- confidence_score: 30-60
- recommended_action: "escalate_to_human"

Demo Point: "Uncertainty language triggers escalation automatically."
```

### Confidence Thresholds for Orchestrate Integration

When building workflows in watsonx Orchestrate:

| Threshold | Behavior | Use Case |
|-----------|----------|----------|
| **>= 90** | Auto-execute without notification | Standard, low-risk operations |
| **80-89** | Auto-execute with notification | Medium-confidence operations |
| **< 80** | Always escalate to human | Anything ambiguous or uncertain |

**Recommended**: Use 80 as the primary branch point in Orchestrate.

### Validation Logic Flow

```
1. Model generates response with confidence score
   ↓
2. Parse JSON (5 strategies with fallbacks)
   ↓
3. Detect ambiguity in incident text
   ↓
4. If ambiguous:
   - Cap confidence at 60
   - Force safe action (escalate/diagnose)
   ↓
5. Enforce policy:
   - confidence < 80 → must escalate or diagnose
   - confidence < 90 → no auto-resolve language
   ↓
6. Return validated decision
```

### Files Modified in v2

```
src/aegis_service/watsonx_client.py  # Core prompt and validation logic
test_ambiguity.py                     # New comprehensive test suite
DEPLOY_REBUILD.md                     # Deployment guide
README.md                             # This documentation
```

### Migrating from v1 to v2

**Breaking Changes**: None

**Behavioral Changes**:
- Ambiguous incidents now cap at confidence 60 (previously could be 70-89)
- More conservative scoring overall
- Stricter action validation

**Orchestrate Impact**:
- More incidents will route to human review path
- Reduction in false-positive auto-executions
- Better alignment with safety-first principles

### Monitoring Recommendations

After deploying v2, monitor:

1. **Confidence Distribution**:
   - Expect increase in 30-60 range (ambiguous incidents)
   - High-confidence (90+) should still be ~40-50% of total

2. **Action Distribution**:
   - Expect increase in `escalate_to_human`
   - This is expected and desired behavior

3. **False Escalations**:
   - Review escalated incidents that were actually clear
   - Refine ambiguity patterns if needed

4. **False Auto-Executions**:
   - Should be near zero with v2
   - Any found indicate prompt refinement needed

---
