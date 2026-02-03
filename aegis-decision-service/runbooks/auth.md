# Authentication Incident Runbook

**AEGIS Hackathon POC - Synthetic Runbook for Demo**

## Investigation Steps

1. **Service Health Check**
   - Verify authentication service status
   - Check service logs for errors
   - Confirm all auth endpoints responding

2. **Credential Validity**
   - Check for expired tokens or certificates
   - Verify API key rotation schedule
   - Review service account permissions

3. **Login Attempt Analysis**
   - Review recent failed login attempts
   - Check for account lockouts
   - Identify patterns (user, time, location)

4. **Integration Status**
   - Verify SSO/SAML provider connectivity
   - Check OAuth flow completion
   - Review third-party auth service status

5. **Recent Changes**
   - Review recent deployments
   - Check configuration changes
   - Verify certificate renewals

## Common Remediation Actions

**High Confidence (Auto-Execute):**
- Restart authentication service if clearly unhealthy
- Clear authentication cache
- Rotate expired credentials (automated)

**Medium Confidence (Run Diagnostics First):**
- Review and update token expiration policies
- Check certificate chain validity
- Verify firewall rules for auth traffic

**Low Confidence (Escalate to Human):**
- Modify authentication configuration
- Change SSO integration settings
- Investigate security incidents
- Roll back recent deployments

## Red Flags (Always Escalate)

- **Intermittent authentication failures** (some users succeed, others fail)
- Authentication issues started after deployment
- Possible security breach indicators
- Widespread failures affecting multiple users
- Auth failures with no clear error messages

## Success Criteria

- 100% of authentication attempts succeed for valid credentials
- Auth service response time < 200ms
- No expired certificates or tokens
- All auth provider integrations healthy

## Automation Policy

**Safe to auto-execute if:**
- Auth service clearly down (can safely restart)
- Credentials expired per policy (automated rotation)
- Cache corruption confirmed

**Must escalate if:**
- Intermittent or partial failures
- Unclear root cause
- Recent deployment correlation
- Multiple auth methods failing
- Potential security incident

## Security Considerations

Authentication incidents often involve:
- Potential security breaches
- User access implications
- Compliance requirements

**Default stance: When in doubt, escalate to human security review.**
