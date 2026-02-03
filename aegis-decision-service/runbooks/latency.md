# Latency Incident Runbook

**AEGIS Hackathon POC - Synthetic Runbook for Demo**

## Investigation Steps

1. **Check Network Latency**
   - Verify network latency to database servers
   - Check for network congestion or routing issues
   - Review VPN or proxy performance

2. **Review Query Performance**
   - Examine recent query execution times in database logs
   - Identify slow queries using database profiling tools
   - Check for missing or outdated indexes

3. **Database Lock Analysis**
   - Check for lock contention in the database
   - Review active transactions and blocking queries
   - Verify deadlock frequency and patterns

4. **Connection Pool Status**
   - Check database connection pool saturation
   - Review connection timeout errors
   - Verify pool sizing configuration

5. **Resource Utilization**
   - Check CPU and memory usage on database servers
   - Review disk I/O metrics
   - Verify cache hit ratios

## Common Remediation Actions

**High Confidence (Auto-Execute):**
- Run diagnostics to identify slow queries
- Clear query cache if stale
- Restart application connections if pool exhausted

**Medium Confidence (Run Diagnostics First):**
- Optimize query execution plans
- Update database statistics
- Rebuild fragmented indexes

**Low Confidence (Escalate to Human):**
- Database schema changes
- Infrastructure scaling decisions
- Complex query refactoring

## Red Flags (Always Escalate)

- Sudden latency spike coinciding with deployment
- Intermittent latency with no clear pattern
- Latency affecting only specific users or regions
- Database replication lag increasing

## Success Criteria

- Query response times return to baseline (< 100ms)
- No connection pool exhaustion errors
- Database CPU utilization < 70%
- Cache hit ratio > 90%
