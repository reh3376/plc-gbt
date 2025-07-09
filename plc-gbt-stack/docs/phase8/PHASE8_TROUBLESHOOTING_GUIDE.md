# Phase 8: PID Tuning Integration - Troubleshooting Guide

## 🎯 Overview

This comprehensive troubleshooting guide provides systematic problem resolution procedures for Phase 8 PID Tuning Integration system. Following AI Task Orchestrator Guide methodology, this guide offers structured diagnostic approaches, common solutions, and escalation procedures for technical issues.

## 📋 Table of Contents

1. [Quick Diagnostic Checklist](#quick-diagnostic-checklist)
2. [System Issues](#system-issues)
3. [Control Loop Problems](#control-loop-problems)
4. [Performance Issues](#performance-issues)
5. [Security and Access Issues](#security-and-access-issues)
6. [Integration Problems](#integration-problems)
7. [Data Quality Issues](#data-quality-issues)
8. [Emergency Procedures](#emergency-procedures)
9. [Escalation Procedures](#escalation-procedures)

---

## Quick Diagnostic Checklist

### ⚡ First 5 Minutes - Emergency Assessment

```
☐ Is the system responding to user input?
☐ Are there any active alarms or alerts?
☐ Is communication with PLCs functioning?
☐ Are critical safety systems operational?
☐ Is there any immediate safety risk?
```

### 🔍 Initial System Health Check

```python
# System health verification script
def quick_system_check():
    health_status = {
        "database_connection": check_database(),
        "plc_communication": check_plc_connectivity(),
        "user_authentication": check_auth_system(),
        "control_loops": check_active_loops(),
        "disk_space": check_storage(),
        "memory_usage": check_memory()
    }
    return health_status
```

### 📊 Performance Baseline Check

| Metric | Normal Range | Warning Level | Critical Level |
|--------|--------------|---------------|----------------|
| Response Time | <2 seconds | 2-5 seconds | >5 seconds |
| CPU Usage | <70% | 70-85% | >85% |
| Memory Usage | <80% | 80-90% | >90% |
| Disk Space | <80% | 80-95% | >95% |
| Loop Updates | >95% success | 90-95% | <90% |

---

## System Issues

### 1. System Won't Start

#### Symptoms:
- Application fails to launch
- Database connection errors
- Service startup failures
- License validation errors

#### Diagnostic Steps:

```bash
# Check system services
systemctl status plc-gbt-phase8
systemctl status postgresql
systemctl status redis

# Check logs
tail -f /var/log/plc-gbt/phase8.log
tail -f /var/log/postgresql/postgresql.log

# Verify database connectivity
psql -h localhost -U plc_gpt_user -d phase8_db -c "SELECT version();"

# Check license status
./check_license.sh
```

#### Common Solutions:

1. **Database Connection Issues**:
   ```sql
   -- Reset database connections
   SELECT pg_terminate_backend(pg_stat_activity.pid)
   FROM pg_stat_activity
   WHERE pg_stat_activity.datname = 'phase8_db'
     AND pid <> pg_backend_pid();
   ```

2. **Service Dependencies**:
   ```bash
   # Restart in correct order
   sudo systemctl stop plc-gbt-phase8
   sudo systemctl restart postgresql
   sudo systemctl restart redis
   sudo systemctl start plc-gbt-phase8
   ```

3. **License Renewal**:
   - Contact support for new license file
   - Place license in `/etc/plc-gbt/license/`
   - Restart services

### 2. Poor System Performance

#### Symptoms:
- Slow response times
- High CPU/memory usage
- Database query timeouts
- User interface lag

#### Performance Analysis:

```python
# Performance monitoring
def analyze_performance():
    metrics = {
        "database_performance": {
            "active_connections": get_db_connections(),
            "query_execution_time": get_slow_queries(),
            "index_usage": check_index_efficiency()
        },
        "application_performance": {
            "response_times": get_response_times(),
            "memory_usage": get_memory_stats(),
            "cache_hit_ratio": get_cache_stats()
        }
    }
    return metrics
```

#### Optimization Solutions:

1. **Database Optimization**:
   ```sql
   -- Identify slow queries
   SELECT query, mean_time, calls, total_time
   FROM pg_stat_statements
   ORDER BY total_time DESC
   LIMIT 10;
   
   -- Rebuild indexes
   REINDEX DATABASE phase8_db;
   
   -- Update statistics
   ANALYZE;
   ```

2. **Application Tuning**:
   ```python
   # Configuration optimization
   app_config = {
       "database_pool_size": 20,
       "cache_timeout": 300,
       "worker_processes": 4,
       "max_connections": 100
   }
   ```

### 3. Communication Failures

#### PLC Communication Issues

**Symptoms**:
- "Communication Lost" alarms
- Stale data indicators
- Tag read/write failures
- Intermittent connectivity

**Diagnostic Procedure**:

```python
# PLC communication diagnostics
def diagnose_plc_communication():
    for plc in plc_list:
        results = {
            "ping_test": ping_plc(plc.ip_address),
            "port_connectivity": check_port(plc.ip_address, plc.port),
            "protocol_handshake": test_protocol(plc),
            "tag_read_test": test_tag_reads(plc),
            "response_time": measure_response_time(plc)
        }
        log_results(plc.name, results)
```

**Solutions**:

1. **Network Issues**:
   ```bash
   # Network diagnostics
   ping -c 4 192.168.1.100
   traceroute 192.168.1.100
   telnet 192.168.1.100 44818
   
   # Check firewall rules
   iptables -L -n | grep 44818
   ```

2. **PLC Configuration**:
   - Verify PLC communication settings
   - Check security certificates
   - Validate tag configurations
   - Review connection limits

---

## Control Loop Problems

### 1. Poor Control Performance

#### Oscillating Loops

**Symptoms**:
- Process variable oscillates around setpoint
- Control output moves excessively
- Poor product quality
- High oscillation index

**Root Cause Analysis**:

```python
def diagnose_oscillation(loop_id):
    data = get_loop_data(loop_id, hours=4)
    
    analysis = {
        "oscillation_frequency": calculate_frequency(data.pv),
        "controller_contribution": analyze_cv_behavior(data.cv),
        "process_disturbances": detect_disturbances(data),
        "valve_stiction": detect_stiction(data.cv, data.pv),
        "measurement_noise": analyze_noise(data.pv)
    }
    
    return analysis
```

**Solutions by Root Cause**:

1. **Aggressive Tuning**:
   ```json
   {
     "action": "retune_controller",
     "method": "more_conservative",
     "parameters": {
       "reduce_gain": "by_50_percent",
       "increase_integral_time": "by_factor_2",
       "reduce_derivative": "if_excessive_noise"
     }
   }
   ```

2. **Valve Stiction**:
   - Perform valve diagnostics
   - Implement valve positioner
   - Consider valve maintenance
   - Add small bias signal

3. **Process Interactions**:
   - Implement decoupling control
   - Adjust tuning for interactions
   - Consider multivariable control

#### Slow Response

**Symptoms**:
- Long settling times
- Poor setpoint tracking
- Sluggish disturbance rejection

**Diagnostic Steps**:

```python
def diagnose_slow_response(loop_id):
    # Perform step test analysis
    step_data = perform_step_test(loop_id)
    
    analysis = {
        "process_gain": calculate_gain(step_data),
        "time_constant": estimate_time_constant(step_data),
        "dead_time": estimate_dead_time(step_data),
        "controller_output_limits": check_cv_saturation(step_data),
        "measurement_dynamics": analyze_pv_response(step_data)
    }
    
    return analysis
```

**Solutions**:

1. **Increase Controller Gain**:
   ```python
   # Gradual gain increase
   current_kc = get_controller_parameter(loop_id, 'kc')
   new_kc = min(current_kc * 1.5, safety_limit)
   set_controller_parameter(loop_id, 'kc', new_kc)
   ```

2. **Reduce Integral Time**:
   - Decrease Ti for faster steady-state response
   - Monitor for overshoot
   - Ensure stability margins

### 2. Tuning Failures

#### Auto-Tuning Not Completing

**Symptoms**:
- Tuning procedure aborts
- Insufficient process response
- Safety limits triggered
- Communication timeouts

**Troubleshooting Steps**:

```python
def troubleshoot_autotuning(loop_id):
    checks = {
        "process_steady_state": verify_steady_state(loop_id),
        "control_output_authority": check_cv_range(loop_id),
        "measurement_quality": check_pv_quality(loop_id),
        "safety_constraints": verify_safety_settings(loop_id),
        "communication_stability": test_communication(loop_id)
    }
    
    for check, result in checks.items():
        if not result.passed:
            log_issue(check, result.details)
    
    return checks
```

**Common Issues and Solutions**:

1. **Process Not at Steady State**:
   - Wait for process stabilization
   - Remove external disturbances
   - Check for other active controllers

2. **Insufficient Control Authority**:
   ```python
   # Check CV operating range
   cv_analysis = {
       "current_value": get_current_cv(loop_id),
       "available_range_up": 100 - get_current_cv(loop_id),
       "available_range_down": get_current_cv(loop_id) - 0,
       "recommended_step": calculate_step_size(loop_id)
   }
   ```

3. **Safety Constraints Too Tight**:
   - Review alarm settings
   - Adjust step size
   - Extend test duration

### 3. Cascade Control Issues

#### Primary/Secondary Loop Coordination

**Symptoms**:
- Secondary loop fighting primary
- Poor overall performance
- Instability when switched to cascade

**Diagnostic Approach**:

```python
def diagnose_cascade_control(primary_loop, secondary_loop):
    analysis = {
        "speed_ratio": calculate_speed_ratio(primary_loop, secondary_loop),
        "tuning_quality": assess_individual_tuning(primary_loop, secondary_loop),
        "interaction_strength": measure_loop_interaction(primary_loop, secondary_loop),
        "mode_switching": test_cascade_switching(primary_loop, secondary_loop)
    }
    
    return analysis
```

**Solutions**:

1. **Proper Speed Ratio**:
   - Secondary loop should be 5-10x faster than primary
   - Tune secondary loop first
   - Use conservative tuning for primary

2. **Correct Mode Switching**:
   ```python
   # Cascade switching logic
   def switch_to_cascade(primary_loop, secondary_loop):
       # Ensure secondary is in auto and stable
       if not secondary_loop.is_stable():
           return False
       
       # Match primary output to secondary setpoint
       primary_output = primary_loop.get_output()
       secondary_loop.set_setpoint(primary_output)
       
       # Switch to cascade mode
       primary_loop.set_cascade_mode(True)
       return True
   ```

---

## Performance Issues

### 1. Poor Control Quality

#### High Variability

**Symptoms**:
- High standard deviation in PV
- Poor process capability indices
- Product quality issues

**Analysis Tools**:

```python
def analyze_control_variability(loop_id, timeframe_hours=24):
    data = get_historical_data(loop_id, timeframe_hours)
    
    metrics = {
        "pv_standard_deviation": np.std(data.pv),
        "cv_variability": calculate_cv_variability(data.cv),
        "disturbance_magnitude": estimate_disturbances(data),
        "control_effort": calculate_control_effort(data.cv),
        "process_capability": calculate_cpk(data.pv, data.setpoint)
    }
    
    return metrics
```

**Improvement Strategies**:

1. **Measurement Filtering**:
   ```python
   # Implement appropriate filtering
   filter_config = {
       "type": "exponential",
       "time_constant": 5.0,  # seconds
       "noise_threshold": 0.1
   }
   ```

2. **Advanced Control**:
   - Implement feed-forward control
   - Add disturbance estimation
   - Consider model predictive control

### 2. Energy Efficiency Problems

#### High Energy Consumption

**Symptoms**:
- Excessive utility usage
- High CV variability
- Frequent actuator movement

**Energy Analysis**:

```python
def analyze_energy_efficiency(loop_id):
    data = get_loop_data(loop_id, hours=168)  # One week
    
    analysis = {
        "cv_movement": calculate_cv_movement(data.cv),
        "energy_consumption": calculate_energy_usage(data),
        "efficiency_opportunities": identify_optimization(data),
        "operating_point_analysis": analyze_setpoints(data)
    }
    
    return analysis
```

**Optimization Solutions**:

1. **Setpoint Optimization**:
   ```python
   # Optimize setpoints for energy efficiency
   def optimize_setpoints(loop_id):
       current_sp = get_setpoint(loop_id)
       energy_model = load_energy_model(loop_id)
       
       optimized_sp = energy_model.optimize(
           constraints=get_process_constraints(loop_id),
           objectives=['minimize_energy', 'maintain_quality']
       )
       
       return optimized_sp
   ```

2. **Control Strategy Optimization**:
   - Implement economic MPC
   - Add energy penalty to control objective
   - Optimize control loop interactions

---

## Security and Access Issues

### 1. Authentication Problems

#### Users Cannot Log In

**Symptoms**:
- Login failures
- Authentication timeouts
- Account lockouts

**Diagnostic Steps**:

```bash
# Check authentication service
systemctl status authentication-service

# Review authentication logs
grep "authentication" /var/log/plc-gbt/security.log

# Test LDAP connectivity (if used)
ldapsearch -x -H ldap://company.local -D "CN=service,DC=company,DC=local" -W

# Verify user accounts
./check_user_accounts.sh
```

**Solutions**:

1. **Reset User Account**:
   ```python
   # Reset user account
   def reset_user_account(username):
       user = get_user(username)
       user.unlock_account()
       user.reset_failed_attempts()
       user.update_last_login()
       save_user(user)
   ```

2. **LDAP Configuration**:
   ```json
   {
     "ldap_config": {
       "server": "ldap://company.local",
       "base_dn": "DC=company,DC=local",
       "user_search": "(&(objectClass=user)(sAMAccountName={username}))",
       "connection_timeout": 10,
       "search_timeout": 5
     }
   }
   ```

### 2. Permission Issues

#### Access Denied Errors

**Symptoms**:
- "Insufficient permissions" messages
- Feature restrictions
- Audit trail gaps

**Permission Analysis**:

```python
def analyze_permissions(username):
    user = get_user(username)
    
    analysis = {
        "assigned_roles": user.get_roles(),
        "effective_permissions": calculate_permissions(user),
        "role_inheritance": trace_role_inheritance(user),
        "recent_changes": get_permission_changes(user, days=7)
    }
    
    return analysis
```

**Solutions**:

1. **Role Assignment Review**:
   ```python
   # Standard role definitions
   roles = {
       "pid_engineer": [
           "create_loops", "modify_loops", "tune_loops",
           "view_performance", "export_data"
       ],
       "operator": [
           "view_loops", "manual_mode", "view_performance"
       ],
       "viewer": [
           "view_loops", "view_performance"
       ]
   }
   ```

---

## Integration Problems

### 1. PLC Integration Issues

#### Tag Communication Failures

**Symptoms**:
- Bad quality tags
- Read/write timeouts
- Inconsistent data

**Diagnostic Procedure**:

```python
def diagnose_tag_issues(tag_list):
    results = {}
    
    for tag in tag_list:
        test_results = {
            "read_test": test_tag_read(tag),
            "write_test": test_tag_write(tag),
            "data_type_validation": validate_data_type(tag),
            "scaling_verification": verify_scaling(tag),
            "update_rate": measure_update_rate(tag)
        }
        
        results[tag.name] = test_results
    
    return results
```

**Solutions**:

1. **Tag Configuration Validation**:
   ```python
   # Validate tag configuration
   def validate_tag_config(tag):
       checks = {
           "address_format": validate_address(tag.address),
           "data_type_match": verify_data_type(tag),
           "scaling_parameters": check_scaling(tag),
           "update_rate": verify_scan_rate(tag)
       }
       return all(checks.values())
   ```

2. **Communication Optimization**:
   ```python
   # Optimize communication settings
   comm_settings = {
       "connection_timeout": 5000,  # ms
       "read_timeout": 3000,       # ms
       "retry_attempts": 3,
       "packet_size": 500          # tags per packet
   }
   ```

---

## Emergency Procedures

### 1. System Failure Recovery

#### Complete System Failure

**Immediate Actions**:

```bash
#!/bin/bash
# Emergency recovery script

echo "=== EMERGENCY SYSTEM RECOVERY ==="

# 1. Switch all loops to manual mode
echo "Switching loops to manual mode..."
./emergency_manual_mode.sh

# 2. Backup current state
echo "Backing up system state..."
./backup_system_state.sh

# 3. Restart core services
echo "Restarting core services..."
systemctl restart postgresql
systemctl restart redis
systemctl restart plc-gbt-phase8

# 4. Verify critical functions
echo "Verifying system recovery..."
./verify_system_health.sh

echo "=== RECOVERY COMPLETE ==="
```

#### Manual Override Procedures

```python
# Emergency manual override
def emergency_manual_override(loop_id):
    """Switch loop to manual mode and hold current output"""
    
    try:
        # Get current output value
        current_cv = get_control_output(loop_id)
        
        # Switch to manual mode
        set_control_mode(loop_id, "MANUAL")
        
        # Hold current output
        set_manual_output(loop_id, current_cv)
        
        # Log emergency action
        log_emergency_action(loop_id, "manual_override", current_cv)
        
        # Notify operators
        send_emergency_notification(loop_id, "Emergency manual override activated")
        
        return True
        
    except Exception as e:
        log_error(f"Emergency override failed for {loop_id}: {str(e)}")
        return False
```

### 2. Data Recovery

#### Database Corruption

**Recovery Steps**:

```sql
-- Database recovery procedure
-- 1. Stop application
-- 2. Backup corrupted database
pg_dump phase8_db > phase8_db_corrupted_backup.sql

-- 3. Restore from last good backup
dropdb phase8_db
createdb phase8_db
psql phase8_db < phase8_db_last_good_backup.sql

-- 4. Verify data integrity
SELECT COUNT(*) FROM loops;
SELECT COUNT(*) FROM historical_data WHERE timestamp > NOW() - INTERVAL '24 hours';

-- 5. Restart application
```

---

## Escalation Procedures

### 1. Support Escalation Matrix

| Issue Severity | Response Time | Escalation Level | Contact Method |
|----------------|---------------|------------------|----------------|
| **Critical** - System down, safety impact | 15 minutes | Level 3 Engineer | Emergency hotline |
| **High** - Major functionality affected | 2 hours | Level 2 Engineer | Phone + Email |
| **Medium** - Limited functionality impact | 4 hours | Level 1 Engineer | Email + Ticket |
| **Low** - Minor issues, enhancement requests | 24 hours | Support Team | Ticket system |

### 2. Information to Collect

#### Before Contacting Support

```python
# Support information collection script
def collect_support_info():
    support_package = {
        "system_info": {
            "version": get_software_version(),
            "installation_date": get_install_date(),
            "last_update": get_last_update(),
            "license_info": get_license_status()
        },
        "error_logs": {
            "application_logs": get_recent_logs("application", hours=24),
            "system_logs": get_recent_logs("system", hours=24),
            "security_logs": get_recent_logs("security", hours=24)
        },
        "performance_data": {
            "cpu_usage": get_cpu_stats(),
            "memory_usage": get_memory_stats(),
            "disk_usage": get_disk_stats(),
            "database_stats": get_db_stats()
        },
        "configuration": {
            "system_config": get_system_config(),
            "loop_configs": get_loop_configs(),
            "user_accounts": get_user_summary()
        }
    }
    
    # Create support package
    create_support_package(support_package)
    return "support_package.zip"
```

### 3. Contact Information

#### 24/7 Emergency Support
- **Phone**: +1-800-PLC-HELP
- **Email**: emergency@plc-gbt.com
- **Portal**: https://support.plc-gbt.com/emergency

#### Standard Support
- **Email**: support@plc-gbt.com
- **Portal**: https://support.plc-gbt.com
- **Documentation**: https://docs.plc-gbt.com/phase8

#### Training and Consulting
- **Email**: training@plc-gbt.com
- **Phone**: +1-800-PLC-TRAIN

---

## 📋 Troubleshooting Checklists

### Daily Health Check
```
☐ System services running
☐ Database connectivity verified
☐ PLC communications active
☐ All critical loops operational
☐ No active alarms
☐ Performance within normal ranges
☐ Backup systems functional
☐ Security logs reviewed
```

### Weekly Maintenance
```
☐ Log files archived
☐ Database maintenance completed
☐ Performance trends reviewed
☐ Security updates applied
☐ User access reviewed
☐ Documentation updated
☐ Backup verification
☐ Disaster recovery test
```

---

*This troubleshooting guide follows AI Task Orchestrator Guide methodology for systematic problem resolution.*  
*Last Updated: January 10, 2025*  
*Version: 1.0.0*  
*Emergency Contact: +1-800-PLC-HELP* 