# General Incident Runbook

**AEGIS Hackathon POC - Synthetic Runbook for Demo**

## Investigation Steps

1. **Gather System Metrics**
   - Check CPU, memory, disk usage
   - Review network connectivity
   - Verify all critical services running

2. **Log Analysis**
   - Check application logs for errors
   - Review system logs (syslog, journalctl)
   - Identify error patterns or spikes

3. **Recent Changes**
   - Review recent deployments
   - Check configuration changes
   - Verify scheduled maintenance

4. **External Dependencies**
   - Check third-party service status
   - Verify API endpoint availability
   - Review external service dashboards

5. **User Impact Assessment**
   - Determine number of affected users
   - Identify specific features impacted
   - Check for error reports or tickets

## Common Remediation Actions

**High Confidence (Auto-Execute):**
- Run comprehensive system diagnostics
- Collect logs for analysis
- Restart clearly failed services

**Medium Confidence (Run Diagnostics First):**
- Investigate log patterns
- Check for known issues
- Review monitoring alerts

**Low Confidence (Escalate to Human):**
- **When incident is vague or ambiguous**
- When impact is unclear
- When root cause is unknown
- When multiple systems involved

## Red Flags (Always Escalate)

- **Vague or incomplete incident description**
- **"System acting weird" or similar non-specific reports**
- Multiple unrelated symptoms
- No clear error messages
- Cannot reproduce the issue
- Issue affects production systems

## Success Criteria

- Clear understanding of the problem
- Identifiable root cause
- Measurable impact assessment
- Appropriate action plan

## Automation Policy

**Safe to auto-execute if:**
- Very clear and specific issue
- Matches known incident patterns
- Standard remediation available
- Low risk of unintended consequences

**Must escalate if:**
- **Incident description is vague or incomplete**
- **Root cause unclear**
- **No matching runbook pattern**
- **Multiple possible causes**
- **Risk of making situation worse**

## Default Stance

For unknown or ambiguous incidents:
1. Run diagnostics to gather information
2. Escalate to human with diagnostic results
3. Do not attempt automated remediation

**"When in doubt, escalate out."**

## Common Unknown Incident Patterns

- "System is slow" (could be anything)
- "Getting errors" (no specifics)
- "Something is broken" (no details)
- "Users complaining" (unclear about what)

All of these should trigger:
- confidence_score < 50
- recommended_action = escalate_to_human
