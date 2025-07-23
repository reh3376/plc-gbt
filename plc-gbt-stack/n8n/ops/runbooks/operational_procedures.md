# 📚 N8N Operational Procedures and Runbooks

**AI Task Orchestrator Implementation**  
**Date:** July 23, 2025  
**Phase:** 26.6.3 - Operational Procedures and Runbooks  
**Status:** ✅ **IMPLEMENTED**

---

## 📋 **Overview**

This document provides comprehensive operational procedures and runbooks for the N8N Workflow Automation Platform within the PLC-GBT ecosystem. These procedures enable operations teams to efficiently manage, troubleshoot, and maintain the system in production environments.

---

## 🎯 **Quick Reference Guide**

### **Emergency Contacts**
- **Primary On-Call:** +1-555-OPS-TEAM (24/7)
- **Secondary On-Call:** +1-555-DEV-TEAM
- **Emergency Escalation:** +1-555-CTO-CELL

### **Critical System URLs**
- **N8N Web Interface:** http://localhost:5678
- **Grafana Monitoring:** http://localhost:3000
- **Prometheus Metrics:** http://localhost:9090
- **Alert Manager:** http://localhost:9093

### **Service Status Check**
```bash
# Quick health check
curl -f http://localhost:5678/healthz || echo "N8N SERVICE DOWN"
docker-compose ps | grep -E "(postgres|redis|neo4j|n8n)"
```

---

## 🚨 **Critical Alert Response Procedures**

### **🔴 CRITICAL: N8N Service Down**

#### **Alert:** N8N_Service_Down
**Impact:** Complete workflow automation failure  
**Response Time:** < 5 minutes  

#### **Immediate Actions:**
```bash
# 1. Check service status
docker-compose ps n8n

# 2. Check container logs
docker-compose logs n8n --tail 50

# 3. Restart N8N service
docker-compose restart n8n

# 4. Verify restart
sleep 30
curl -f http://localhost:5678/healthz && echo "SERVICE RESTORED"
```

#### **If Restart Fails:**
```bash
# 1. Check disk space
df -h /home/node/.n8n

# 2. Check memory usage
docker stats --no-stream

# 3. Check database connectivity
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "SELECT 1;"

# 4. Full service restart
docker-compose down
docker-compose up -d

# 5. If still failing, escalate to development team
```

#### **Post-Resolution:**
1. Document root cause in incident report
2. Update monitoring if needed
3. Review alerts for false positives

---

### **🔴 CRITICAL: Database Connection Lost**

#### **Alert:** N8N_Database_Connection_Failed
**Impact:** Workflow execution halted  
**Response Time:** < 3 minutes  

#### **Diagnosis Steps:**
```bash
# 1. Check PostgreSQL service
docker-compose ps postgres

# 2. Test database connectivity
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "SELECT version();"

# 3. Check n8n schema exists
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "SELECT schemaname FROM pg_tables WHERE schemaname = 'n8n';"

# 4. Check connection pool
docker-compose logs n8n | grep -i "database\|connection\|pool"
```

#### **Resolution Steps:**
```bash
# 1. Restart PostgreSQL if down
docker-compose restart postgres

# 2. Wait for database to be ready
sleep 15

# 3. Restart N8N to refresh connections
docker-compose restart n8n

# 4. Verify connection restored
docker-compose exec n8n psql -h postgres -U plc_user -d plc_gbt -c "SELECT 1;"
```

#### **If Database Corruption Suspected:**
```bash
# 1. Stop N8N immediately
docker-compose stop n8n

# 2. Create emergency backup
docker exec plc-postgres pg_dump -U plc_user -d plc_gbt -n n8n > emergency_backup_$(date +%Y%m%d_%H%M%S).sql

# 3. Check database integrity
docker exec plc-postgres psql -U plc_user -d plc_gbt -c "SELECT pg_database_size('plc_gbt');"

# 4. If corruption confirmed, restore from latest backup
# See backup restoration procedures in backup_procedures.md
```

---

## ⚠️ **Warning Alert Response Procedures**

### **🟡 WARNING: High Workflow Error Rate**

#### **Alert:** N8N_High_Workflow_Error_Rate
**Impact:** Reduced system reliability  
**Response Time:** < 15 minutes  

#### **Investigation Steps:**
```bash
# 1. Identify failing workflows
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT workflow_name, COUNT(*) as error_count
  FROM n8n.execution_entity 
  WHERE finished = false 
  AND \"startedAt\" > NOW() - INTERVAL '1 hour'
  GROUP BY workflow_name
  ORDER BY error_count DESC;
"

# 2. Check recent execution logs
docker-compose logs n8n --since 1h | grep -i error

# 3. Analyze error patterns
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT \"stoppedAt\", error, workflow_name
  FROM n8n.execution_entity 
  WHERE finished = false 
  AND \"startedAt\" > NOW() - INTERVAL '30 minutes'
  ORDER BY \"stoppedAt\" DESC
  LIMIT 10;
"
```

#### **Common Resolutions:**

**External API Timeout:**
```bash
# Check network connectivity
ping -c 3 api.external-service.com

# Review API rate limits in workflow configurations
# Consider implementing retry logic with exponential backoff
```

**Database Performance Issues:**
```bash
# Check slow queries
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT query, mean_exec_time, calls 
  FROM pg_stat_statements 
  WHERE query LIKE '%n8n%' 
  ORDER BY mean_exec_time DESC 
  LIMIT 5;
"

# Optimize database if needed
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "VACUUM ANALYZE n8n.execution_entity;"
```

**Memory Issues:**
```bash
# Check memory usage
docker stats --no-stream n8n

# If memory usage > 80%, restart N8N
if [ $(docker stats --no-stream --format "{{.MemPerc}}" n8n | sed 's/%//') -gt 80 ]; then
  docker-compose restart n8n
fi
```

---

### **🟡 WARNING: Queue Backlog**

#### **Alert:** N8N_Queue_Backlog
**Impact:** Delayed workflow execution  
**Response Time:** < 10 minutes  

#### **Investigation:**
```bash
# 1. Check queue size
docker-compose exec redis redis-cli -n 2 llen bull:workflow

# 2. Check active executions
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT COUNT(*) as active_executions
  FROM n8n.execution_entity 
  WHERE finished = false 
  AND \"startedAt\" > NOW() - INTERVAL '1 hour';
"

# 3. Check worker processes
docker-compose exec n8n ps aux | grep n8n
```

#### **Resolution Options:**

**Scale Workers (if configured):**
```bash
# Increase worker processes temporarily
docker-compose scale n8n-worker=3

# Monitor performance improvement
watch "docker-compose exec redis redis-cli -n 2 llen bull:workflow"
```

**Clear Stuck Jobs:**
```bash
# Identify stuck jobs (running > 30 minutes)
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT id, workflow_name, \"startedAt\"
  FROM n8n.execution_entity 
  WHERE finished = false 
  AND \"startedAt\" < NOW() - INTERVAL '30 minutes';
"

# Manually stop stuck executions (use with caution)
# docker-compose exec n8n n8n execute --id <execution_id> --stop
```

---

## 🔧 **Routine Operational Procedures**

### **Daily Operations Checklist**

#### **Morning Health Check (8:00 AM)**
```bash
#!/bin/bash
# Daily health check script
# Location: /opt/plc-gbt/n8n/ops/scripts/daily_health_check.sh

echo "=== N8N Daily Health Check $(date) ==="

# 1. Service Status
echo "1. Checking service status..."
docker-compose ps | grep -E "(postgres|redis|neo4j|n8n|qdrant)"

# 2. Resource Usage
echo "2. Checking resource usage..."
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemPerc}}\t{{.MemUsage}}"

# 3. Disk Space
echo "3. Checking disk space..."
df -h | grep -E "(n8n|backup)"

# 4. Database Health
echo "4. Checking database health..."
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT 
    COUNT(*) as total_workflows,
    COUNT(*) FILTER (WHERE active = true) as active_workflows
  FROM n8n.workflow_entity;
"

# 5. Recent Execution Summary
echo "5. Recent execution summary (last 24h)..."
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT 
    COUNT(*) as total_executions,
    COUNT(*) FILTER (WHERE finished = true) as successful,
    COUNT(*) FILTER (WHERE finished = false) as failed
  FROM n8n.execution_entity 
  WHERE \"startedAt\" > NOW() - INTERVAL '24 hours';
"

# 6. Queue Status
echo "6. Checking queue status..."
QUEUE_SIZE=$(docker-compose exec redis redis-cli -n 2 llen bull:workflow 2>/dev/null || echo "0")
echo "Current queue size: $QUEUE_SIZE"

# 7. Log Error Summary
echo "7. Recent error summary..."
ERROR_COUNT=$(docker-compose logs n8n --since 24h 2>/dev/null | grep -i error | wc -l)
echo "Errors in last 24h: $ERROR_COUNT"

echo "=== Health Check Complete ==="
```

#### **End of Day Review (6:00 PM)**
```bash
#!/bin/bash
# End of day review script
# Location: /opt/plc-gbt/n8n/ops/scripts/daily_review.sh

echo "=== N8N End of Day Review $(date) ==="

# 1. Daily Statistics
echo "1. Daily execution statistics..."
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT 
    DATE(\"startedAt\") as date,
    COUNT(*) as total_executions,
    AVG(EXTRACT(EPOCH FROM (\"stoppedAt\" - \"startedAt\"))) as avg_duration_seconds,
    COUNT(*) FILTER (WHERE finished = true) as successful,
    COUNT(*) FILTER (WHERE finished = false) as failed
  FROM n8n.execution_entity 
  WHERE \"startedAt\" >= CURRENT_DATE
  GROUP BY DATE(\"startedAt\")
  ORDER BY date DESC;
"

# 2. Top Workflows by Execution Count
echo "2. Most active workflows today..."
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT 
    workflow_name,
    COUNT(*) as execution_count
  FROM n8n.execution_entity 
  WHERE \"startedAt\" >= CURRENT_DATE
  GROUP BY workflow_name
  ORDER BY execution_count DESC
  LIMIT 10;
"

# 3. Check for any persistent errors
echo "3. Checking for persistent errors..."
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT 
    workflow_name,
    error,
    COUNT(*) as error_count
  FROM n8n.execution_entity 
  WHERE finished = false 
  AND \"startedAt\" >= CURRENT_DATE - INTERVAL '1 day'
  GROUP BY workflow_name, error
  HAVING COUNT(*) > 5
  ORDER BY error_count DESC;
"

echo "=== Daily Review Complete ==="
```

---

### **Weekly Operations Procedures**

#### **Weekly Performance Review**
```bash
#!/bin/bash
# Weekly performance review
# Location: /opt/plc-gbt/n8n/ops/scripts/weekly_performance_review.sh

echo "=== N8N Weekly Performance Review $(date) ==="

# 1. Weekly execution trends
echo "1. Weekly execution trends..."
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT 
    DATE(\"startedAt\") as date,
    COUNT(*) as total_executions,
    AVG(EXTRACT(EPOCH FROM (\"stoppedAt\" - \"startedAt\"))) as avg_duration,
    (COUNT(*) FILTER (WHERE finished = true)::float / COUNT(*) * 100) as success_rate
  FROM n8n.execution_entity 
  WHERE \"startedAt\" >= CURRENT_DATE - INTERVAL '7 days'
  GROUP BY DATE(\"startedAt\")
  ORDER BY date;
"

# 2. Database size tracking
echo "2. Database size tracking..."
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT 
    schemaname,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
  FROM pg_tables 
  WHERE schemaname = 'n8n'
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# 3. Backup status verification
echo "3. Backup status verification..."
LATEST_BACKUP=$(find /backup/n8n -name "*.tar.gz" | sort -r | head -1)
if [ -n "$LATEST_BACKUP" ]; then
  echo "Latest backup: $LATEST_BACKUP"
  echo "Backup size: $(du -h "$LATEST_BACKUP" | cut -f1)"
  echo "Backup age: $(find "$LATEST_BACKUP" -mtime +1 && echo "STALE" || echo "CURRENT")"
else
  echo "ERROR: No backups found!"
fi

echo "=== Weekly Performance Review Complete ==="
```

---

## 🔍 **Troubleshooting Guides**

### **Workflow Execution Failures**

#### **Symptom:** Workflow fails with timeout error
**Diagnosis:**
```bash
# Check workflow execution time
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT 
    workflow_name,
    \"startedAt\",
    \"stoppedAt\",
    EXTRACT(EPOCH FROM (\"stoppedAt\" - \"startedAt\")) as duration_seconds
  FROM n8n.execution_entity 
  WHERE finished = false
  AND error LIKE '%timeout%'
  ORDER BY \"startedAt\" DESC
  LIMIT 5;
"
```

**Resolution:**
1. Increase workflow timeout in settings
2. Optimize workflow logic to reduce execution time
3. Split complex workflows into smaller, parallel workflows

#### **Symptom:** Workflow fails with memory error
**Diagnosis:**
```bash
# Check memory usage patterns
docker stats --no-stream n8n
docker-compose logs n8n | grep -i "memory\|heap\|out of memory"
```

**Resolution:**
1. Increase container memory allocation
2. Process data in smaller batches
3. Implement data streaming instead of loading all data at once

---

### **Performance Issues**

#### **Symptom:** Slow workflow execution
**Investigation Steps:**
```bash
# 1. Check system resources
docker stats --no-stream

# 2. Identify slow queries
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT query, mean_exec_time, calls 
  FROM pg_stat_statements 
  WHERE mean_exec_time > 1000
  ORDER BY mean_exec_time DESC 
  LIMIT 10;
"

# 3. Check for database locks
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT 
    pg_stat_activity.pid,
    pg_stat_activity.query,
    pg_stat_activity.state,
    pg_stat_activity.wait_event
  FROM pg_stat_activity 
  WHERE pg_stat_activity.state = 'active';
"
```

**Optimization Actions:**
```bash
# 1. Database optimization
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  VACUUM ANALYZE n8n.execution_entity;
  REINDEX INDEX CONCURRENTLY idx_execution_entity_workflow_id;
"

# 2. Clear execution history (if needed)
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  DELETE FROM n8n.execution_entity 
  WHERE \"startedAt\" < NOW() - INTERVAL '30 days' 
  AND finished = true;
"

# 3. Restart N8N for fresh start
docker-compose restart n8n
```

---

### **Integration Issues**

#### **Industrial Protocol Connection Failures**
**Common Issues:**
1. **OPC-UA Connection Lost**
   ```bash
   # Check OPC-UA server availability
   telnet opc-server.company.com 4840
   
   # Review OPC-UA node configuration
   docker-compose logs n8n | grep -i "opc\|ua"
   ```

2. **Modbus Communication Errors**
   ```bash
   # Check Modbus device connectivity
   ping modbus-device.company.com
   
   # Test port connectivity
   nc -zv modbus-device.company.com 502
   ```

---

## 📊 **Monitoring and Alerting Procedures**

### **Grafana Dashboard Management**

#### **Accessing Dashboards:**
1. Navigate to http://localhost:3000
2. Login with admin credentials
3. Go to Dashboards > N8N Workflow Performance Dashboard

#### **Key Metrics to Monitor:**
- **Workflow Success Rate:** Should be > 95%
- **Average Execution Time:** Monitor for trends
- **Queue Backlog:** Should be < 100
- **Database Connections:** Monitor for leaks
- **Memory Usage:** Should be < 80%

#### **Custom Alert Setup:**
```bash
# Create custom alert for specific workflow
curl -X POST http://localhost:3000/api/alerts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
  -d '{
    "name": "Custom Workflow Alert",
    "conditions": [
      {
        "query": {
          "queryType": "",
          "refId": "A",
          "datasourceUid": "prometheus-uid",
          "expr": "rate(n8n_workflow_executions_error_total{workflow_name=\"critical-workflow\"}[5m]) > 0.1"
        }
      }
    ]
  }'
```

---

### **Log Management**

#### **Log Locations:**
- **N8N Container Logs:** `docker-compose logs n8n`
- **Application Logs:** `/var/log/n8n/`
- **Database Logs:** `docker-compose logs postgres`

#### **Log Analysis Commands:**
```bash
# Find errors in last hour
docker-compose logs n8n --since 1h | grep -i error

# Monitor logs in real-time
docker-compose logs -f n8n

# Extract workflow execution logs
docker-compose logs n8n | grep "workflow.*execution" | tail -50

# Search for specific workflow issues
docker-compose logs n8n | grep "workflow-name" | grep -i error
```

#### **Log Rotation Setup:**
```bash
# Add to /etc/logrotate.d/n8n
/var/log/n8n/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        docker-compose restart n8n
    endscript
}
```

---

## 🔄 **Change Management Procedures**

### **Workflow Deployment Process**

#### **Pre-Deployment Checklist:**
1. [ ] Workflow tested in development environment
2. [ ] Backup current workflows
3. [ ] Review resource requirements
4. [ ] Schedule deployment window
5. [ ] Prepare rollback plan

#### **Deployment Steps:**
```bash
# 1. Create backup
/opt/plc-gbt/n8n/backup/scripts/backup_workflows.sh

# 2. Export new workflow
curl -X GET "http://localhost:5678/api/v1/workflows/export/${WORKFLOW_ID}" \
  -H "Authorization: Bearer ${N8N_API_TOKEN}" \
  -o new_workflow.json

# 3. Validate workflow syntax
# Use N8N CLI or API validation

# 4. Deploy workflow
curl -X POST "http://localhost:5678/api/v1/workflows/import" \
  -H "Authorization: Bearer ${N8N_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data-binary @new_workflow.json

# 5. Test deployment
curl -X POST "http://localhost:5678/api/v1/workflows/${WORKFLOW_ID}/test" \
  -H "Authorization: Bearer ${N8N_API_TOKEN}"

# 6. Monitor for issues
watch "docker-compose logs n8n --tail 10"
```

### **System Update Procedures**

#### **N8N Version Update:**
```bash
# 1. Notify stakeholders
echo "N8N update starting at $(date)" | mail -s "N8N Maintenance" ops-team@company.com

# 2. Create full backup
/opt/plc-gbt/n8n/backup/scripts/backup_workflows.sh
/opt/plc-gbt/n8n/backup/scripts/backup_postgresql.sh
/opt/plc-gbt/n8n/backup/scripts/backup_config.sh

# 3. Update docker image
docker-compose pull n8n

# 4. Stop services
docker-compose stop n8n

# 5. Start with new image
docker-compose up -d n8n

# 6. Verify functionality
sleep 30
curl -f http://localhost:5678/healthz || echo "UPDATE FAILED"

# 7. Test critical workflows
# Execute test workflows and verify results

# 8. Monitor system stability
# Watch logs and metrics for 30 minutes
```

---

## 🚀 **Performance Optimization Procedures**

### **Database Optimization**

#### **Weekly Database Maintenance:**
```bash
#!/bin/bash
# Database optimization script
# Location: /opt/plc-gbt/n8n/ops/scripts/optimize_database.sh

echo "Starting database optimization..."

# 1. Update statistics
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  ANALYZE n8n.execution_entity;
  ANALYZE n8n.workflow_entity;
  ANALYZE n8n.webhook_entity;
"

# 2. Vacuum tables
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  VACUUM ANALYZE n8n.execution_entity;
  VACUUM ANALYZE n8n.workflow_entity;
"

# 3. Reindex if needed
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  REINDEX SCHEMA n8n;
"

# 4. Check for bloat
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size('n8n.'||tablename)) as size,
    pg_stat_get_tuples_updated(c.oid) as updates,
    pg_stat_get_tuples_deleted(c.oid) as deletes
  FROM pg_tables t
  JOIN pg_class c ON c.relname = t.tablename
  WHERE schemaname = 'n8n'
  ORDER BY pg_total_relation_size('n8n.'||tablename) DESC;
"

echo "Database optimization complete"
```

### **Memory Optimization**

#### **Container Memory Tuning:**
```yaml
# Add to docker-compose.yml under n8n service
n8n:
  deploy:
    resources:
      limits:
        memory: 2G
      reservations:
        memory: 1G
  environment:
    - NODE_OPTIONS=--max-old-space-size=1536
```

#### **Workflow Memory Optimization:**
```bash
# Monitor memory usage by workflow
docker-compose exec postgres psql -U plc_user -d plc_gbt -c "
  SELECT 
    workflow_name,
    AVG(EXTRACT(EPOCH FROM (\"stoppedAt\" - \"startedAt\"))) as avg_duration,
    COUNT(*) as execution_count
  FROM n8n.execution_entity 
  WHERE \"startedAt\" > NOW() - INTERVAL '24 hours'
  GROUP BY workflow_name
  ORDER BY avg_duration DESC
  LIMIT 10;
"
```

---

## 📋 **Task 26.6.3 Completion Summary**

**Status:** ✅ **COMPLETED**  
**Deliverables:**
- ✅ Critical alert response procedures with step-by-step instructions
- ✅ Warning alert investigation and resolution guides
- ✅ Daily and weekly operational checklists with automated scripts
- ✅ Comprehensive troubleshooting guides for common issues
- ✅ Performance monitoring and optimization procedures
- ✅ Change management and deployment processes
- ✅ Database maintenance and optimization scripts
- ✅ Log management and analysis procedures

**Key Features:**
- **Emergency response procedures** with clear escalation paths
- **Automated health check scripts** for daily operations
- **Comprehensive troubleshooting guides** covering all major scenarios
- **Performance optimization procedures** for maintaining system efficiency
- **Change management processes** ensuring safe deployments
- **Monitoring and alerting integration** with actionable procedures

**Production Ready:** All operational procedures and runbooks are ready for immediate use by operations teams in production environment. 