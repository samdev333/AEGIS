# Storage Incident Runbook

**AEGIS Hackathon POC - Synthetic Runbook for Demo**

## Investigation Steps

1. **Disk Space Analysis**
   - Check disk space usage on all volumes
   - Identify mount points nearing capacity
   - Review growth trends over past 24 hours

2. **Log File Review**
   - Check log rotation configuration
   - Identify large log files (> 1GB)
   - Verify log retention policies

3. **Temporary Files**
   - Scan for orphaned temporary files
   - Check /tmp and cache directories
   - Review file age and ownership

4. **Database and Backup Space**
   - Check database file sizes
   - Verify backup process disk usage
   - Review backup retention settings

5. **Large File Identification**
   - Find top 20 largest files
   - Check for core dumps
   - Identify unexpected data growth

## Common Remediation Actions

**High Confidence (Auto-Execute):**
- Clear old application logs (> 7 days)
- Remove orphaned temporary files
- Clear system cache if safe

**Medium Confidence (Run Diagnostics First):**
- Compress large log files
- Archive old backup files
- Clean up package manager caches

**Low Confidence (Escalate to Human):**
- Delete production data
- Modify backup retention policies
- Resize or add storage volumes

## Red Flags (Always Escalate)

- Rapid disk space consumption (> 10% in 1 hour)
- Storage issue affecting production databases
- No clear cause for disk space usage
- Mission-critical volumes below 10% free

## Success Criteria

- All volumes have > 20% free space
- Log rotation functioning correctly
- No orphaned temporary files > 24 hours old
- Backup processes completing successfully

## Automation Policy

**Safe to auto-execute if:**
- Log rotation simply failed to run
- Temporary files are clearly orphaned (> 48 hours)
- Disk usage < 95% (not critical yet)
- No active user sessions affected

**Must escalate if:**
- Disk usage > 95% (critical)
- Unclear cause of space consumption
- Production database involved
- Recent deployment may have caused issue
