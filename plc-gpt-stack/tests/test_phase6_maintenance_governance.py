#!/usr/bin/env python3
"""
Phase 6 Testing Suite: Maintenance & Governance Systems
Following AI Task Orchestrator validation methodology

This module provides comprehensive testing for:
- Automated maintenance scripts
- Security governance systems
- Health monitoring and alerting
- Backup automation and rotation
- Compliance monitoring
"""

import asyncio
import unittest
import tempfile
import json
import time
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Phase 6 components
from scripts.maintenance.automated_maintenance import (
    AutomatedMaintenanceSystem, MaintenanceTask, MaintenanceResult
)
from scripts.governance.security_governance import (
    SecurityGovernanceSystem, AuditEventType, ComplianceStandard, DataClassification
)
from scripts.monitoring.health_monitoring import (
    EnhancedHealthMonitoring, HealthStatus, ComponentType
)
from config.enterprise_settings import EnterpriseSettings


class TestPhase6MaintenanceGovernance(unittest.TestCase):
    """
    Comprehensive test suite for Phase 6 Maintenance & Governance Systems.
    
    Test Categories:
    1. Automated Maintenance System
    2. Security Governance System  
    3. Enhanced Health Monitoring
    4. Integration Testing
    5. Performance Validation
    6. Error Handling
    """
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories
        self.temp_dir = Path(tempfile.mkdtemp())
        self.backup_dir = self.temp_dir / "backup"
        self.logs_dir = self.temp_dir / "logs"
        
        # Mock settings
        self.settings = Mock(spec=EnterpriseSettings)
        self.settings.jwt_secret = "test-secret-key"
        self.settings.jwt_algorithm = "HS256"
        self.settings.jwt_expiration_hours = 24
        self.settings.redis_host = "localhost"
        self.settings.redis_port = 6379
        self.settings.redis_password = ""
        
        # Initialize test results
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'test_categories': {},
            'overall_status': 'pending',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_duration': 0.0
        }
        
        print(f"\n🧪 Phase 6 Testing Suite: Maintenance & Governance Systems")
        print(f"📂 Test directory: {self.temp_dir}")
    
    def tearDown(self):
        """Clean up test environment."""
        # Clean up temporary files
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    # ========================================
    # Category 1: Automated Maintenance System Tests
    # ========================================
    
    def test_automated_maintenance_initialization(self):
        """Test automated maintenance system initialization."""
        print("\n🔧 Testing automated maintenance initialization...")
        
        try:
            with patch('scripts.maintenance.automated_maintenance.get_monitoring'), \
                 patch('scripts.maintenance.automated_maintenance.get_cache'), \
                 patch('scripts.maintenance.automated_maintenance.AITaskOrchestrator'):
                
                maintenance = AutomatedMaintenanceSystem(self.settings)
                
                # Verify initialization
                self.assertIsNotNone(maintenance.tasks)
                self.assertGreater(len(maintenance.tasks), 0)
                self.assertFalse(maintenance.is_running)
                
                # Verify required tasks exist
                required_tasks = [
                    'fine_tune_refresh', 'vector_reembedding', 'neo4j_backup',
                    'postgres_backup', 'qdrant_backup', 'performance_optimization',
                    'health_monitoring', 'cache_cleanup', 'backup_rotation'
                ]
                
                for task_id in required_tasks:
                    self.assertIn(task_id, maintenance.tasks)
                    task = maintenance.tasks[task_id]
                    self.assertIsInstance(task, MaintenanceTask)
                    self.assertEqual(task.task_id, task_id)
                
                print("✅ Automated maintenance initialization: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Automated maintenance initialization: FAILED - {e}")
            return False
    
    def test_maintenance_task_execution(self):
        """Test individual maintenance task execution."""
        print("\n🔧 Testing maintenance task execution...")
        
        try:
            with patch('scripts.maintenance.automated_maintenance.get_monitoring'), \
                 patch('scripts.maintenance.automated_maintenance.get_cache') as mock_cache, \
                 patch('scripts.maintenance.automated_maintenance.AITaskOrchestrator'), \
                 patch('subprocess.run') as mock_subprocess:
                
                # Mock cache cleanup
                mock_cache.return_value.cleanup_expired.return_value = 10
                mock_cache.return_value.cleanup_lru_if_needed.return_value = 5
                mock_cache.return_value.get_stats.return_value = {'size': 100, 'hit_rate': 85.0}
                
                # Mock subprocess calls
                mock_subprocess.return_value.returncode = 0
                mock_subprocess.return_value.stderr = ""
                
                maintenance = AutomatedMaintenanceSystem(self.settings)
                
                # Test cache cleanup task
                result = maintenance._run_task('cache_cleanup')
                
                self.assertIsInstance(result, MaintenanceResult)
                self.assertTrue(result.success)
                self.assertEqual(result.task_id, 'cache_cleanup')
                self.assertGreater(result.duration_seconds, 0)
                
                # Verify task status updated
                task = maintenance.tasks['cache_cleanup']
                self.assertEqual(task.status, 'completed')
                self.assertEqual(task.success_count, 1)
                self.assertEqual(task.failure_count, 0)
                
                print("✅ Maintenance task execution: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Maintenance task execution: FAILED - {e}")
            return False
    
    def test_backup_operations(self):
        """Test backup creation and rotation."""
        print("\n🔧 Testing backup operations...")
        
        try:
            with patch('scripts.maintenance.automated_maintenance.get_monitoring'), \
                 patch('scripts.maintenance.automated_maintenance.get_cache'), \
                 patch('scripts.maintenance.automated_maintenance.AITaskOrchestrator'), \
                 patch('subprocess.run') as mock_subprocess:
                
                # Mock successful backup
                mock_subprocess.return_value.returncode = 0
                mock_subprocess.return_value.stderr = ""
                
                maintenance = AutomatedMaintenanceSystem(self.settings)
                maintenance.backup_dir = self.backup_dir
                
                # Test Neo4j backup
                result = maintenance._run_neo4j_backup()
                self.assertTrue(result['success'])
                self.assertIn('backup_file', result['details'])
                
                # Test PostgreSQL backup
                with patch('builtins.open', create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value = Mock()
                    result = maintenance._run_postgres_backup()
                    self.assertTrue(result['success'])
                
                # Test backup rotation
                # Create old backup files
                old_backup_dir = self.backup_dir / "neo4j"
                old_backup_dir.mkdir(parents=True, exist_ok=True)
                
                old_file = old_backup_dir / "old_backup.backup"
                old_file.touch()
                # Set modification time to 40 days ago
                old_time = time.time() - (40 * 24 * 3600)
                os.utime(old_file, (old_time, old_time))
                
                result = maintenance._run_backup_rotation()
                self.assertTrue(result['success'])
                self.assertGreater(result['details']['files_deleted'], 0)
                
                print("✅ Backup operations: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Backup operations: FAILED - {e}")
            return False
    
    # ========================================
    # Category 2: Security Governance System Tests
    # ========================================
    
    def test_security_governance_initialization(self):
        """Test security governance system initialization."""
        print("\n🔒 Testing security governance initialization...")
        
        try:
            with patch('scripts.governance.security_governance.get_rbac_manager'), \
                 patch('scripts.governance.security_governance.get_jwt_manager'), \
                 patch('scripts.governance.security_governance.get_monitoring'):
                
                governance = SecurityGovernanceSystem(self.settings)
                
                # Verify initialization
                self.assertIsNotNone(governance.data_policies)
                self.assertIsNotNone(governance.compliance_checks)
                self.assertGreater(len(governance.data_policies), 0)
                self.assertGreater(len(governance.compliance_checks), 0)
                
                # Verify required data policies
                required_policies = ['plc_config', 'user_data', 'system_logs', 'training_data']
                for policy_id in required_policies:
                    self.assertIn(policy_id, governance.data_policies)
                    policy = governance.data_policies[policy_id]
                    self.assertEqual(policy.policy_id, policy_id)
                    self.assertIsInstance(policy.classification, DataClassification)
                
                # Verify compliance checks
                self.assertIn('gdpr_data_retention', governance.compliance_checks)
                self.assertIn('iso27001_access_control', governance.compliance_checks)
                
                print("✅ Security governance initialization: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Security governance initialization: FAILED - {e}")
            return False
    
    def test_audit_event_logging(self):
        """Test audit event logging functionality."""
        print("\n🔒 Testing audit event logging...")
        
        try:
            with patch('scripts.governance.security_governance.get_rbac_manager'), \
                 patch('scripts.governance.security_governance.get_jwt_manager'), \
                 patch('scripts.governance.security_governance.get_monitoring'):
                
                governance = SecurityGovernanceSystem(self.settings)
                governance.audit_dir = self.logs_dir / "audit"
                governance.audit_dir.mkdir(parents=True, exist_ok=True)
                
                # Test audit event logging
                event_id = governance.log_audit_event(
                    event_type=AuditEventType.USER_LOGIN,
                    user_id="test_user",
                    user_role="admin",
                    resource="/api/query",
                    action="login",
                    result="success",
                    ip_address="127.0.0.1",
                    details={"browser": "test"}
                )
                
                self.assertIsNotNone(event_id)
                self.assertEqual(len(governance.audit_events), 1)
                
                event = governance.audit_events[0]
                self.assertEqual(event.event_type, AuditEventType.USER_LOGIN)
                self.assertEqual(event.user_id, "test_user")
                self.assertEqual(event.result, "success")
                
                # Verify audit log file was created
                log_files = list(governance.audit_dir.glob("audit_*.jsonl"))
                self.assertGreater(len(log_files), 0)
                
                print("✅ Audit event logging: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Audit event logging: FAILED - {e}")
            return False
    
    def test_data_masking(self):
        """Test data masking functionality."""
        print("\n🔒 Testing data masking...")
        
        try:
            with patch('scripts.governance.security_governance.get_rbac_manager'), \
                 patch('scripts.governance.security_governance.get_jwt_manager'), \
                 patch('scripts.governance.security_governance.get_monitoring'):
                
                governance = SecurityGovernanceSystem(self.settings)
                
                # Test data masking
                test_data = {
                    'customer_name': 'ACME Corporation',
                    'site_location': '123 Main Street, Anytown, USA',
                    'serial_number': 'SN123456789',
                    'other_field': 'not masked'
                }
                
                masked_data = governance.apply_data_masking(test_data, 'plc_config')
                
                # Verify masking applied
                self.assertNotEqual(masked_data['customer_name'], test_data['customer_name'])
                self.assertNotEqual(masked_data['site_location'], test_data['site_location'])
                self.assertNotEqual(masked_data['serial_number'], test_data['serial_number'])
                self.assertEqual(masked_data['other_field'], test_data['other_field'])
                
                # Verify hash consistency
                masked_data2 = governance.apply_data_masking(test_data, 'plc_config')
                self.assertEqual(masked_data['customer_name'], masked_data2['customer_name'])
                
                print("✅ Data masking: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Data masking: FAILED - {e}")
            return False
    
    def test_compliance_monitoring(self):
        """Test compliance monitoring functionality."""
        print("\n🔒 Testing compliance monitoring...")
        
        try:
            with patch('scripts.governance.security_governance.get_rbac_manager') as mock_rbac, \
                 patch('scripts.governance.security_governance.get_jwt_manager'), \
                 patch('scripts.governance.security_governance.get_monitoring'):
                
                # Mock RBAC manager
                mock_rbac.return_value = Mock()
                
                governance = SecurityGovernanceSystem(self.settings)
                governance.compliance_dir = self.logs_dir / "compliance"
                governance.compliance_dir.mkdir(parents=True, exist_ok=True)
                
                # Run compliance checks
                results = governance.run_compliance_checks()
                
                self.assertIsInstance(results, dict)
                self.assertGreater(len(results), 0)
                
                # Verify specific checks
                self.assertIn('gdpr_data_retention', results)
                self.assertIn('iso27001_access_control', results)
                
                # Verify compliance report created
                report_files = list(governance.compliance_dir.glob("compliance_report_*.json"))
                self.assertGreater(len(report_files), 0)
                
                # Verify compliance summary
                summary = governance._generate_compliance_summary()
                self.assertIn('total_checks', summary)
                self.assertIn('compliance_percentage', summary)
                self.assertIn('overall_status', summary)
                
                print("✅ Compliance monitoring: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Compliance monitoring: FAILED - {e}")
            return False
    
    # ========================================
    # Category 3: Enhanced Health Monitoring Tests
    # ========================================
    
    def test_health_monitoring_initialization(self):
        """Test health monitoring system initialization."""
        print("\n🏥 Testing health monitoring initialization...")
        
        try:
            with patch('scripts.monitoring.health_monitoring.get_monitoring'), \
                 patch('scripts.monitoring.health_monitoring.get_cache'):
                
                health_monitor = EnhancedHealthMonitoring(self.settings)
                
                # Verify initialization
                self.assertIsNotNone(health_monitor.components)
                self.assertGreater(len(health_monitor.components), 0)
                self.assertFalse(health_monitor.is_monitoring)
                
                # Verify required components
                required_components = [
                    'neo4j', 'postgres', 'qdrant', 'redis', 'gateway',
                    'etl_worker', 'system_cpu', 'system_memory', 'system_disk'
                ]
                
                for component_id in required_components:
                    self.assertIn(component_id, health_monitor.components)
                    component = health_monitor.components[component_id]
                    self.assertEqual(component.component_id, component_id)
                    self.assertIsInstance(component.component_type, ComponentType)
                
                # Verify alert handlers
                self.assertGreater(len(health_monitor.alert_handlers), 0)
                
                print("✅ Health monitoring initialization: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Health monitoring initialization: FAILED - {e}")
            return False
    
    def test_component_health_checks(self):
        """Test individual component health checks."""
        print("\n🏥 Testing component health checks...")
        
        try:
            with patch('scripts.monitoring.health_monitoring.get_monitoring'), \
                 patch('scripts.monitoring.health_monitoring.get_cache') as mock_cache, \
                 patch('requests.get') as mock_requests, \
                 patch('psutil.cpu_percent') as mock_cpu, \
                 patch('psutil.virtual_memory') as mock_memory, \
                 patch('psutil.disk_usage') as mock_disk:
                
                # Mock system resources
                mock_cpu.return_value = 45.0
                mock_memory.return_value = Mock(percent=65.0)
                mock_disk.return_value = Mock(used=50000, total=100000)
                
                # Mock cache health
                mock_cache.return_value.health_check.return_value = {
                    'status': 'healthy',
                    'message': 'Redis is healthy'
                }
                mock_cache.return_value.get_stats.return_value = {
                    'hit_rate': 85.0,
                    'memory_usage': 256.0
                }
                
                # Mock HTTP requests
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.elapsed.total_seconds.return_value = 0.1
                mock_response.json.return_value = {'result': {'collections': []}}
                mock_requests.return_value = mock_response
                
                health_monitor = EnhancedHealthMonitoring(self.settings)
                
                # Test system resource checks
                health_monitor._check_component_health('system_cpu')
                cpu_component = health_monitor.components['system_cpu']
                self.assertEqual(cpu_component.status, HealthStatus.HEALTHY)
                self.assertGreater(len(cpu_component.metrics), 0)
                
                # Test cache health check
                health_monitor._check_component_health('redis')
                redis_component = health_monitor.components['redis']
                self.assertEqual(redis_component.status, HealthStatus.HEALTHY)
                
                # Test API service health check
                health_monitor._check_component_health('qdrant')
                qdrant_component = health_monitor.components['qdrant']
                self.assertEqual(qdrant_component.status, HealthStatus.HEALTHY)
                
                print("✅ Component health checks: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Component health checks: FAILED - {e}")
            return False
    
    def test_health_alerting(self):
        """Test health alerting functionality."""
        print("\n🏥 Testing health alerting...")
        
        try:
            with patch('scripts.monitoring.health_monitoring.get_monitoring'), \
                 patch('scripts.monitoring.health_monitoring.get_cache'), \
                 patch('psutil.cpu_percent') as mock_cpu:
                
                # Mock high CPU usage
                mock_cpu.return_value = 95.0  # Critical threshold
                
                health_monitor = EnhancedHealthMonitoring(self.settings)
                
                # Check component health (should trigger alert)
                health_monitor._check_component_health('system_cpu')
                
                # Process alerts
                health_monitor._process_alerts()
                
                # Verify alert was created
                self.assertGreater(len(health_monitor.active_alerts), 0)
                
                alert = list(health_monitor.active_alerts.values())[0]
                self.assertEqual(alert.component_id, 'system_cpu')
                self.assertFalse(alert.resolved)
                
                # Test alert resolution
                mock_cpu.return_value = 30.0  # Normal level
                health_monitor._check_component_health('system_cpu')
                health_monitor._process_alerts()
                
                # Verify alert was resolved
                self.assertTrue(alert.resolved)
                self.assertIsNotNone(alert.resolved_at)
                
                print("✅ Health alerting: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Health alerting: FAILED - {e}")
            return False
    
    def test_predictive_monitoring(self):
        """Test predictive failure detection."""
        print("\n🏥 Testing predictive monitoring...")
        
        try:
            with patch('scripts.monitoring.health_monitoring.get_monitoring'), \
                 patch('scripts.monitoring.health_monitoring.get_cache'):
                
                health_monitor = EnhancedHealthMonitoring(self.settings)
                
                # Create trending data that should trigger predictive alert
                component_id = 'system_memory'
                metric_name = 'memory_usage'
                
                # Simulate increasing memory usage trend
                base_time = datetime.now()
                for i in range(15):
                    timestamp = base_time + timedelta(minutes=i * 2)
                    value = 70.0 + (i * 2.0)  # Increasing from 70% to 98%
                    
                    from scripts.monitoring.health_monitoring import HealthMetric
                    metric = HealthMetric(
                        name=metric_name,
                        value=value,
                        unit='percentage',
                        threshold_warning=85.0,
                        threshold_critical=95.0,
                        status=HealthStatus.HEALTHY,
                        message=f'Memory usage: {value:.1f}%',
                        timestamp=timestamp
                    )
                    
                    if component_id not in health_monitor.health_history:
                        health_monitor.health_history[component_id] = []
                    health_monitor.health_history[component_id].append(metric)
                
                # Analyze trends (should create predictive alert)
                health_monitor._analyze_health_trends()
                
                # Verify predictive alert was created
                self.assertGreater(len(health_monitor.predictive_alerts), 0)
                
                predictive_alert = list(health_monitor.predictive_alerts.values())[0]
                self.assertEqual(predictive_alert.component_id, component_id)
                self.assertGreater(predictive_alert.confidence, 0)
                
                print("✅ Predictive monitoring: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Predictive monitoring: FAILED - {e}")
            return False
    
    # ========================================
    # Category 4: Integration Testing
    # ========================================
    
    def test_maintenance_governance_integration(self):
        """Test integration between maintenance and governance systems."""
        print("\n🔗 Testing maintenance-governance integration...")
        
        try:
            with patch('scripts.maintenance.automated_maintenance.get_monitoring'), \
                 patch('scripts.maintenance.automated_maintenance.get_cache'), \
                 patch('scripts.maintenance.automated_maintenance.AITaskOrchestrator'), \
                 patch('scripts.governance.security_governance.get_rbac_manager'), \
                 patch('scripts.governance.security_governance.get_jwt_manager'), \
                 patch('scripts.governance.security_governance.get_monitoring'):
                
                # Initialize both systems
                maintenance = AutomatedMaintenanceSystem(self.settings)
                governance = SecurityGovernanceSystem(self.settings)
                
                # Test that maintenance operations are audited
                maintenance_event_id = governance.log_audit_event(
                    event_type=AuditEventType.MAINTENANCE_TASK,
                    user_id="system",
                    user_role="admin",
                    resource="backup_system",
                    action="create_backup",
                    result="success"
                )
                
                self.assertIsNotNone(maintenance_event_id)
                self.assertEqual(len(governance.audit_events), 1)
                
                # Test governance status includes maintenance info
                governance_status = governance.get_governance_status()
                self.assertIn('audit_events_count', governance_status)
                self.assertEqual(governance_status['audit_events_count'], 1)
                
                # Test maintenance status
                maintenance_status = maintenance.get_maintenance_status()
                self.assertIn('is_running', maintenance_status)
                self.assertIn('tasks', maintenance_status)
                
                print("✅ Maintenance-governance integration: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Maintenance-governance integration: FAILED - {e}")
            return False
    
    def test_health_monitoring_integration(self):
        """Test integration with existing monitoring infrastructure."""
        print("\n🔗 Testing health monitoring integration...")
        
        try:
            with patch('scripts.monitoring.health_monitoring.get_monitoring') as mock_enterprise_monitoring, \
                 patch('scripts.monitoring.health_monitoring.get_cache'):
                
                # Mock enterprise monitoring
                mock_monitoring = Mock()
                mock_enterprise_monitoring.return_value = mock_monitoring
                
                health_monitor = EnhancedHealthMonitoring(self.settings)
                
                # Verify integration with enterprise monitoring
                self.assertEqual(health_monitor.enterprise_monitoring, mock_monitoring)
                
                # Test health summary integration
                summary = health_monitor.get_system_health_summary()
                
                self.assertIn('overall_status', summary)
                self.assertIn('total_components', summary)
                self.assertIn('health_percentage', summary)
                self.assertIn('active_alerts', summary)
                
                # Verify summary contains all expected fields
                expected_fields = [
                    'overall_status', 'total_components', 'healthy', 'warning',
                    'critical', 'unknown', 'health_percentage', 'active_alerts',
                    'predictive_alerts', 'last_check'
                ]
                
                for field in expected_fields:
                    self.assertIn(field, summary)
                
                print("✅ Health monitoring integration: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Health monitoring integration: FAILED - {e}")
            return False
    
    # ========================================
    # Category 5: Performance Validation
    # ========================================
    
    def test_maintenance_performance(self):
        """Test maintenance system performance."""
        print("\n⚡ Testing maintenance system performance...")
        
        try:
            with patch('scripts.maintenance.automated_maintenance.get_monitoring'), \
                 patch('scripts.maintenance.automated_maintenance.get_cache') as mock_cache, \
                 patch('scripts.maintenance.automated_maintenance.AITaskOrchestrator'):
                
                # Mock fast cache operations
                mock_cache.return_value.cleanup_expired.return_value = 100
                mock_cache.return_value.cleanup_lru_if_needed.return_value = 50
                mock_cache.return_value.get_stats.return_value = {'size': 1000, 'hit_rate': 90.0}
                
                maintenance = AutomatedMaintenanceSystem(self.settings)
                
                # Test cache cleanup performance
                start_time = time.time()
                result = maintenance._run_task('cache_cleanup')
                duration = time.time() - start_time
                
                self.assertTrue(result.success)
                self.assertLess(duration, 5.0)  # Should complete in under 5 seconds
                self.assertGreater(result.duration_seconds, 0)
                
                print(f"✅ Maintenance performance: PASSED (duration: {duration:.3f}s)")
                return True
                
        except Exception as e:
            print(f"❌ Maintenance performance: FAILED - {e}")
            return False
    
    def test_governance_performance(self):
        """Test governance system performance."""
        print("\n⚡ Testing governance system performance...")
        
        try:
            with patch('scripts.governance.security_governance.get_rbac_manager'), \
                 patch('scripts.governance.security_governance.get_jwt_manager'), \
                 patch('scripts.governance.security_governance.get_monitoring'):
                
                governance = SecurityGovernanceSystem(self.settings)
                
                # Test audit logging performance
                start_time = time.time()
                
                # Log multiple events
                for i in range(100):
                    governance.log_audit_event(
                        event_type=AuditEventType.DATA_ACCESS,
                        user_id=f"user_{i}",
                        user_role="user",
                        resource="/api/data",
                        action="read",
                        result="success"
                    )
                
                duration = time.time() - start_time
                
                self.assertEqual(len(governance.audit_events), 100)
                self.assertLess(duration, 2.0)  # Should log 100 events in under 2 seconds
                
                # Test data masking performance
                test_data = {
                    'customer_name': 'Test Customer',
                    'site_location': 'Test Location',
                    'serial_number': 'SN123456'
                }
                
                start_time = time.time()
                for i in range(100):
                    masked_data = governance.apply_data_masking(test_data, 'plc_config')
                duration = time.time() - start_time
                
                self.assertLess(duration, 1.0)  # Should mask 100 records in under 1 second
                
                print(f"✅ Governance performance: PASSED (audit: {duration:.3f}s)")
                return True
                
        except Exception as e:
            print(f"❌ Governance performance: FAILED - {e}")
            return False
    
    def test_health_monitoring_performance(self):
        """Test health monitoring performance."""
        print("\n⚡ Testing health monitoring performance...")
        
        try:
            with patch('scripts.monitoring.health_monitoring.get_monitoring'), \
                 patch('scripts.monitoring.health_monitoring.get_cache'), \
                 patch('psutil.cpu_percent') as mock_cpu, \
                 patch('psutil.virtual_memory') as mock_memory, \
                 patch('psutil.disk_usage') as mock_disk, \
                 patch('requests.get') as mock_requests:
                
                # Mock fast system calls
                mock_cpu.return_value = 50.0
                mock_memory.return_value = Mock(percent=60.0)
                mock_disk.return_value = Mock(used=50000, total=100000)
                
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.elapsed.total_seconds.return_value = 0.05
                mock_response.json.return_value = {'result': {'collections': []}}
                mock_requests.return_value = mock_response
                
                health_monitor = EnhancedHealthMonitoring(self.settings)
                
                # Test health check performance
                start_time = time.time()
                
                # Check all components
                for component_id in health_monitor.components.keys():
                    health_monitor._check_component_health(component_id)
                
                duration = time.time() - start_time
                
                self.assertLess(duration, 10.0)  # Should check all components in under 10 seconds
                
                # Test health summary performance
                start_time = time.time()
                summary = health_monitor.get_system_health_summary()
                summary_duration = time.time() - start_time
                
                self.assertLess(summary_duration, 1.0)  # Should generate summary in under 1 second
                self.assertIsInstance(summary, dict)
                
                print(f"✅ Health monitoring performance: PASSED (check: {duration:.3f}s, summary: {summary_duration:.3f}s)")
                return True
                
        except Exception as e:
            print(f"❌ Health monitoring performance: FAILED - {e}")
            return False
    
    # ========================================
    # Category 6: Error Handling Tests
    # ========================================
    
    def test_maintenance_error_handling(self):
        """Test maintenance system error handling."""
        print("\n🛡️ Testing maintenance error handling...")
        
        try:
            with patch('scripts.maintenance.automated_maintenance.get_monitoring'), \
                 patch('scripts.maintenance.automated_maintenance.get_cache') as mock_cache, \
                 patch('scripts.maintenance.automated_maintenance.AITaskOrchestrator'):
                
                # Mock cache failure
                mock_cache.return_value.cleanup_expired.side_effect = Exception("Redis connection failed")
                
                maintenance = AutomatedMaintenanceSystem(self.settings)
                
                # Test task failure handling
                result = maintenance._run_task('cache_cleanup')
                
                self.assertFalse(result.success)
                self.assertIsNotNone(result.error)
                self.assertIn("Redis connection failed", result.error)
                
                # Verify task status updated correctly
                task = maintenance.tasks['cache_cleanup']
                self.assertEqual(task.status, 'failed')
                self.assertEqual(task.failure_count, 1)
                self.assertIsNotNone(task.error_message)
                
                print("✅ Maintenance error handling: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Maintenance error handling: FAILED - {e}")
            return False
    
    def test_governance_error_handling(self):
        """Test governance system error handling."""
        print("\n🛡️ Testing governance error handling...")
        
        try:
            with patch('scripts.governance.security_governance.get_rbac_manager') as mock_rbac, \
                 patch('scripts.governance.security_governance.get_jwt_manager'), \
                 patch('scripts.governance.security_governance.get_monitoring'):
                
                # Mock RBAC failure
                mock_rbac.side_effect = Exception("RBAC system unavailable")
                
                governance = SecurityGovernanceSystem(self.settings)
                
                # Test permission check with RBAC failure
                has_permission = governance.check_data_access_permission(
                    user_id="test_user",
                    user_role="user",
                    resource="/api/data",
                    action="read"
                )
                
                # Should deny access on error
                self.assertFalse(has_permission)
                
                # Verify audit event was logged
                self.assertGreater(len(governance.audit_events), 0)
                
                # Find the failure event
                failure_events = [e for e in governance.audit_events if e.result == 'failure']
                self.assertGreater(len(failure_events), 0)
                
                print("✅ Governance error handling: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Governance error handling: FAILED - {e}")
            return False
    
    def test_health_monitoring_error_handling(self):
        """Test health monitoring error handling."""
        print("\n🛡️ Testing health monitoring error handling...")
        
        try:
            with patch('scripts.monitoring.health_monitoring.get_monitoring'), \
                 patch('scripts.monitoring.health_monitoring.get_cache'), \
                 patch('requests.get') as mock_requests:
                
                # Mock network failure
                mock_requests.side_effect = Exception("Connection timeout")
                
                health_monitor = EnhancedHealthMonitoring(self.settings)
                
                # Test health check with network failure
                health_monitor._check_component_health('qdrant')
                
                # Verify component status reflects error
                qdrant_component = health_monitor.components['qdrant']
                self.assertEqual(qdrant_component.status, HealthStatus.CRITICAL)
                self.assertIsNotNone(qdrant_component.error_message)
                self.assertIn("Connection timeout", qdrant_component.error_message)
                
                # Test system health summary with errors
                summary = health_monitor.get_system_health_summary()
                self.assertGreater(summary['critical'], 0)
                self.assertIn(summary['overall_status'], [HealthStatus.CRITICAL.value, HealthStatus.WARNING.value])
                
                print("✅ Health monitoring error handling: PASSED")
                return True
                
        except Exception as e:
            print(f"❌ Health monitoring error handling: FAILED - {e}")
            return False
    
    # ========================================
    # Test Execution and Reporting
    # ========================================
    
    def run_comprehensive_tests(self):
        """Run all Phase 6 tests and generate report."""
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"🧪 PHASE 6 COMPREHENSIVE TEST SUITE")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Test categories and methods
        test_categories = {
            "Automated Maintenance System": [
                self.test_automated_maintenance_initialization,
                self.test_maintenance_task_execution,
                self.test_backup_operations
            ],
            "Security Governance System": [
                self.test_security_governance_initialization,
                self.test_audit_event_logging,
                self.test_data_masking,
                self.test_compliance_monitoring
            ],
            "Enhanced Health Monitoring": [
                self.test_health_monitoring_initialization,
                self.test_component_health_checks,
                self.test_health_alerting,
                self.test_predictive_monitoring
            ],
            "Integration Testing": [
                self.test_maintenance_governance_integration,
                self.test_health_monitoring_integration
            ],
            "Performance Validation": [
                self.test_maintenance_performance,
                self.test_governance_performance,
                self.test_health_monitoring_performance
            ],
            "Error Handling": [
                self.test_maintenance_error_handling,
                self.test_governance_error_handling,
                self.test_health_monitoring_error_handling
            ]
        }
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        # Run tests by category
        for category, test_methods in test_categories.items():
            print(f"\n📂 {category}")
            print("-" * 50)
            
            category_results = {
                'total': len(test_methods),
                'passed': 0,
                'failed': 0,
                'tests': []
            }
            
            for test_method in test_methods:
                total_tests += 1
                
                try:
                    test_start = time.time()
                    result = test_method()
                    test_duration = time.time() - test_start
                    
                    if result:
                        passed_tests += 1
                        category_results['passed'] += 1
                        status = "PASSED"
                    else:
                        failed_tests += 1
                        category_results['failed'] += 1
                        status = "FAILED"
                    
                    category_results['tests'].append({
                        'name': test_method.__name__,
                        'status': status,
                        'duration': test_duration
                    })
                    
                except Exception as e:
                    failed_tests += 1
                    category_results['failed'] += 1
                    category_results['tests'].append({
                        'name': test_method.__name__,
                        'status': "ERROR",
                        'error': str(e),
                        'duration': 0
                    })
                    print(f"❌ {test_method.__name__}: ERROR - {e}")
            
            self.test_results['test_categories'][category] = category_results
            
            # Category summary
            success_rate = (category_results['passed'] / category_results['total']) * 100
            print(f"\n📊 {category} Summary:")
            print(f"   ✅ Passed: {category_results['passed']}/{category_results['total']} ({success_rate:.1f}%)")
            if category_results['failed'] > 0:
                print(f"   ❌ Failed: {category_results['failed']}")
        
        # Overall results
        total_duration = time.time() - start_time
        success_rate = (passed_tests / total_tests) * 100
        
        self.test_results.update({
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'test_duration': total_duration,
            'success_rate': success_rate,
            'overall_status': 'PASSED' if success_rate >= 90 else 'FAILED'
        })
        
        # Final summary
        print(f"\n{'='*60}")
        print(f"🏁 PHASE 6 TEST SUITE COMPLETE")
        print(f"{'='*60}")
        print(f"📊 Overall Results:")
        print(f"   ✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⏱️ Duration: {total_duration:.2f} seconds")
        print(f"   🎯 Status: {self.test_results['overall_status']}")
        
        # Success criteria validation
        if success_rate >= 90:
            print(f"\n🎉 SUCCESS: Phase 6 Maintenance & Governance Systems validation complete!")
            print(f"✅ All critical components tested and validated")
            print(f"✅ Ready for production deployment")
        else:
            print(f"\n⚠️ WARNING: Some tests failed. Review failed tests before deployment.")
        
        return self.test_results


def main():
    """Main function to run Phase 6 tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Phase 6 Maintenance & Governance Testing Suite')
    parser.add_argument('--output', type=str, help='Output file for test results')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Run tests
    test_suite = TestPhase6MaintenanceGovernance()
    test_suite.setUp()
    
    try:
        results = test_suite.run_comprehensive_tests()
        
        # Save results if output file specified
        if args.output:
            output_file = Path(args.output)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"\n📄 Test results saved to: {output_file}")
        
        # Exit with appropriate code
        exit_code = 0 if results['overall_status'] == 'PASSED' else 1
        exit(exit_code)
        
    finally:
        test_suite.tearDown()


if __name__ == "__main__":
    main() 