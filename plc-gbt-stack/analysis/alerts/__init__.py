#!/usr/bin/env python3
"""
Phase 22.4: Task 22.4.4 - Alerting Framework Package
====================================================

Comprehensive alerting framework including:
- Configurable alert conditions
- Multi-channel notifications
- Alert prioritization and filtering
- Root cause analysis integration

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.4.4 - Alerting Framework
Methodology: AI Task Orchestrator Guide
"""

__version__ = "1.0.0"
__author__ = "PLC-GPT Development Team"
__phase__ = "22.4.4"

# Alerting framework configuration
ALERTING_CONFIG = {
    "version": __version__,
    "supported_channels": [
        "email",
        "sms",
        "slack",
        "teams",
        "webhook",
        "dashboard",
        "syslog",
        "database"
    ],
    "alert_priorities": {
        "critical": {"level": 1, "escalation_time": 300},    # 5 minutes
        "high": {"level": 2, "escalation_time": 900},        # 15 minutes
        "medium": {"level": 3, "escalation_time": 3600},     # 1 hour
        "low": {"level": 4, "escalation_time": 14400},       # 4 hours
        "info": {"level": 5, "escalation_time": 86400}       # 24 hours
    },
    "notification_settings": {
        "batch_interval": 60,  # seconds
        "max_batch_size": 10,
        "rate_limiting": {
            "critical": 0,      # No limit
            "high": 5,          # 5 per hour
            "medium": 10,       # 10 per hour
            "low": 20,          # 20 per hour
            "info": 50          # 50 per hour
        },
        "duplicate_suppression": 3600,  # 1 hour
        "escalation_enabled": True
    },
    "root_cause_analysis": {
        "enable_correlation": True,
        "correlation_window": 1800,  # 30 minutes
        "confidence_threshold": 0.7,
        "max_related_alerts": 10,
        "pattern_matching": True
    },
    "filtering_rules": {
        "maintenance_mode": False,
        "business_hours_only": False,
        "severity_threshold": "info",
        "tag_filters": [],
        "source_filters": []
    }
}

# Alerting types and enums
import asyncio
import hashlib
import json
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union


class AlertPriority(Enum):
    """Alert priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AlertStatus(Enum):
    """Alert status states"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"

class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"
    SYSLOG = "syslog"
    DATABASE = "database"

class AlertCategory(Enum):
    """Alert category types"""
    PERFORMANCE = "performance"
    FAULT = "fault"
    MAINTENANCE = "maintenance"
    SAFETY = "safety"
    SECURITY = "security"
    CONFIGURATION = "configuration"

@dataclass
class AlertCondition:
    """Alert condition definition"""
    condition_id: str
    name: str
    description: str
    condition_type: str  # "threshold", "pattern", "anomaly", "custom"
    parameters: Dict[str, Any]
    priority: AlertPriority
    category: AlertCategory
    enabled: bool = True

    # Condition logic
    threshold_value: Optional[float] = None
    comparison_operator: str = ">"  # >, <, >=, <=, ==, !=
    time_window: int = 300  # seconds
    consecutive_violations: int = 1

    # Notification settings
    notification_channels: List[NotificationChannel] = field(default_factory=list)
    notification_template: Optional[str] = None
    escalation_enabled: bool = True

    # Filtering
    applicable_tags: List[str] = field(default_factory=list)
    applicable_sources: List[str] = field(default_factory=list)

@dataclass
class Alert:
    """Alert instance"""
    alert_id: str
    condition_id: str
    title: str
    description: str
    priority: AlertPriority
    category: AlertCategory
    status: AlertStatus

    # Timestamps
    triggered_time: datetime
    acknowledged_time: Optional[datetime] = None
    resolved_time: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    # Context information
    source_id: str = "unknown"
    tag_name: Optional[str] = None
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None

    # Root cause analysis
    related_alerts: List[str] = field(default_factory=list)
    root_cause_confidence: float = 0.0
    root_cause_explanation: str = ""

    # Notification tracking
    notifications_sent: List[Dict[str, Any]] = field(default_factory=list)
    acknowledgment_user: Optional[str] = None
    resolution_notes: str = ""

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    escalation_level: int = 0

@dataclass
class NotificationMessage:
    """Notification message structure"""
    message_id: str
    alert_id: str
    channel: NotificationChannel
    recipient: str
    subject: str
    body: str
    priority: AlertPriority

    # Delivery tracking
    created_time: datetime
    sent_time: Optional[datetime] = None
    delivered_time: Optional[datetime] = None
    failed_time: Optional[datetime] = None

    # Status and retry
    delivery_status: str = "pending"  # pending, sent, delivered, failed
    retry_count: int = 0
    max_retries: int = 3

    # Message content
    template_used: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RootCauseAnalysis:
    """Root cause analysis results"""
    analysis_id: str
    primary_alert_id: str
    related_alert_ids: List[str]
    confidence_score: float

    # Analysis results
    probable_cause: str
    contributing_factors: List[str]
    correlation_evidence: Dict[str, Any]

    # Recommendations
    immediate_actions: List[str]
    preventive_actions: List[str]

    # Analysis metadata
    analysis_time: datetime
    analysis_method: str
    data_sources: List[str]

# Import alerting modules
try:
    from .alert_dashboard import AlertDashboard
    from .alert_engine import AlertEngine
    from .notification_manager import NotificationManager
    from .root_cause_analyzer import RootCauseAnalyzer
    ALERTING_MODULES_AVAILABLE = True
except ImportError:
    ALERTING_MODULES_AVAILABLE = False

# Module availability status
AVAILABILITY_STATUS = {
    "alert_engine": ALERTING_MODULES_AVAILABLE,
    "notification_manager": ALERTING_MODULES_AVAILABLE,
    "root_cause_analyzer": ALERTING_MODULES_AVAILABLE,
    "alert_dashboard": ALERTING_MODULES_AVAILABLE
}

def get_available_channels():
    """Get list of available notification channels"""
    return ALERTING_CONFIG["supported_channels"]

def get_channel_info(channel: str):
    """Get detailed information about a notification channel"""
    info = {
        "email": {
            "name": "Email Notifications",
            "description": "Send alerts via email with HTML formatting",
            "delivery_time": "< 1 minute",
            "reliability": "High",
            "best_for": ["Detailed reports", "Non-urgent alerts", "Documentation"],
            "configuration": ["SMTP server", "Recipients", "Templates"]
        },
        "sms": {
            "name": "SMS Text Messages",
            "description": "Send critical alerts via SMS",
            "delivery_time": "< 30 seconds",
            "reliability": "Very High",
            "best_for": ["Critical alerts", "Emergency notifications", "On-call staff"],
            "configuration": ["SMS gateway", "Phone numbers", "Message limits"]
        },
        "slack": {
            "name": "Slack Integration",
            "description": "Post alerts to Slack channels",
            "delivery_time": "< 10 seconds",
            "reliability": "High",
            "best_for": ["Team collaboration", "Real-time updates", "Interactive responses"],
            "configuration": ["Slack webhook", "Channels", "Bot tokens"]
        },
        "teams": {
            "name": "Microsoft Teams",
            "description": "Send notifications to Teams channels",
            "delivery_time": "< 10 seconds",
            "reliability": "High",
            "best_for": ["Enterprise environments", "Team coordination", "Rich formatting"],
            "configuration": ["Teams webhook", "Channels", "Connectors"]
        },
        "webhook": {
            "name": "Custom Webhooks",
            "description": "Send alerts to custom HTTP endpoints",
            "delivery_time": "< 5 seconds",
            "reliability": "Variable",
            "best_for": ["Custom integrations", "External systems", "API automation"],
            "configuration": ["Endpoint URL", "Authentication", "Payload format"]
        },
        "dashboard": {
            "name": "Real-time Dashboard",
            "description": "Display alerts on monitoring dashboard",
            "delivery_time": "Real-time",
            "reliability": "Very High",
            "best_for": ["Operations center", "Visual monitoring", "Status overview"],
            "configuration": ["Dashboard URL", "Display rules", "Auto-refresh"]
        }
    }
    return info.get(channel, {"description": "Unknown channel type"})

def validate_alert_condition(condition: AlertCondition) -> Dict[str, Any]:
    """Validate alert condition configuration"""

    validation = {
        "valid": True,
        "errors": [],
        "warnings": []
    }

    # Required fields validation
    required_fields = ["condition_id", "name", "condition_type", "priority"]
    for field in required_fields:
        if not getattr(condition, field, None):
            validation["errors"].append(f"Missing required field: {field}")
            validation["valid"] = False

    # Condition type validation
    valid_types = ["threshold", "pattern", "anomaly", "custom"]
    if condition.condition_type not in valid_types:
        validation["errors"].append(f"Invalid condition type: {condition.condition_type}")
        validation["valid"] = False

    # Threshold condition validation
    if condition.condition_type == "threshold":
        if condition.threshold_value is None:
            validation["errors"].append("Threshold conditions require threshold_value")
            validation["valid"] = False

        valid_operators = [">", "<", ">=", "<=", "==", "!="]
        if condition.comparison_operator not in valid_operators:
            validation["errors"].append(f"Invalid comparison operator: {condition.comparison_operator}")
            validation["valid"] = False

    # Time window validation
    if condition.time_window <= 0:
        validation["warnings"].append("Time window should be positive")

    # Notification channels validation
    valid_channels = [channel.value for channel in NotificationChannel]
    for channel in condition.notification_channels:
        if isinstance(channel, str) and channel not in valid_channels:
            validation["warnings"].append(f"Unknown notification channel: {channel}")
        elif hasattr(channel, 'value') and channel.value not in valid_channels:
            validation["warnings"].append(f"Unknown notification channel: {channel.value}")

    return validation

def create_alert_from_condition(condition: AlertCondition, trigger_data: Dict[str, Any]) -> Alert:
    """Create an alert instance from a condition and trigger data"""

    alert_id = f"{condition.condition_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{trigger_data.get('source_id', 'unknown')}"

    # Generate alert title and description
    if condition.condition_type == "threshold":
        title = f"{condition.name}: Value {trigger_data.get('current_value', 'N/A')} {condition.comparison_operator} {condition.threshold_value}"
        description = f"Threshold condition '{condition.name}' triggered. Current value: {trigger_data.get('current_value', 'N/A')}, Threshold: {condition.threshold_value}"
    else:
        title = condition.name
        description = condition.description

    alert = Alert(
        alert_id=alert_id,
        condition_id=condition.condition_id,
        title=title,
        description=description,
        priority=condition.priority,
        category=condition.category,
        status=AlertStatus.ACTIVE,
        triggered_time=datetime.now(),
        source_id=trigger_data.get("source_id", "unknown"),
        tag_name=trigger_data.get("tag_name"),
        current_value=trigger_data.get("current_value"),
        threshold_value=condition.threshold_value,
        metadata=trigger_data.get("metadata", {})
    )

    return alert

def calculate_alert_hash(alert: Alert) -> str:
    """Calculate unique hash for alert deduplication"""

    # Create hash from key identifying fields
    hash_data = f"{alert.condition_id}|{alert.source_id}|{alert.tag_name}|{alert.priority.value}"
    return hashlib.md5(hash_data.encode()).hexdigest()

def format_notification_message(alert: Alert, channel: NotificationChannel,
                               template: Optional[str] = None) -> NotificationMessage:
    """Format notification message for specific channel"""

    message_id = f"msg_{alert.alert_id}_{channel.value}_{datetime.now().strftime('%H%M%S')}"

    # Default templates by channel
    if template is None:
        if channel in [NotificationChannel.EMAIL]:
            subject = f"[{alert.priority.value.upper()}] {alert.title}"
            body = f"""
Alert Details:
- Alert ID: {alert.alert_id}
- Priority: {alert.priority.value.upper()}
- Category: {alert.category.value}
- Source: {alert.source_id}
- Triggered: {alert.triggered_time.strftime('%Y-%m-%d %H:%M:%S')}

Description:
{alert.description}

Current Value: {alert.current_value}
Threshold: {alert.threshold_value}

Status: {alert.status.value}
"""
        elif channel in [NotificationChannel.SMS]:
            subject = f"{alert.priority.value.upper()}: {alert.title[:50]}"
            body = f"ALERT: {alert.title[:100]}... Source: {alert.source_id}. Value: {alert.current_value}. Triggered: {alert.triggered_time.strftime('%H:%M')}"

        elif channel in [NotificationChannel.SLACK, NotificationChannel.TEAMS]:
            subject = f"Alert: {alert.title}"
            emoji = "🔴" if alert.priority == AlertPriority.CRITICAL else "🟠" if alert.priority == AlertPriority.HIGH else "🟡"
            body = f"""
{emoji} **{alert.priority.value.upper()} ALERT**

**{alert.title}**

• **Source:** {alert.source_id}
• **Category:** {alert.category.value}
• **Current Value:** {alert.current_value}
• **Triggered:** {alert.triggered_time.strftime('%Y-%m-%d %H:%M:%S')}

{alert.description}
"""
        else:
            subject = f"Alert: {alert.title}"
            body = alert.description
    else:
        # Use custom template (simplified template processing)
        variables = {
            "alert_id": alert.alert_id,
            "title": alert.title,
            "description": alert.description,
            "priority": alert.priority.value,
            "category": alert.category.value,
            "source_id": alert.source_id,
            "current_value": alert.current_value,
            "threshold_value": alert.threshold_value,
            "triggered_time": alert.triggered_time.strftime('%Y-%m-%d %H:%M:%S'),
            "status": alert.status.value
        }

        subject = template.format(**variables) if "{" in template else f"Alert: {alert.title}"
        body = template.format(**variables)

    message = NotificationMessage(
        message_id=message_id,
        alert_id=alert.alert_id,
        channel=channel,
        recipient="",  # To be filled by notification manager
        subject=subject,
        body=body,
        priority=alert.priority,
        created_time=datetime.now(),
        variables={"alert": alert}
    )

    return message

def filter_alerts(alerts: List[Alert], filters: Dict[str, Any]) -> List[Alert]:
    """Filter alerts based on criteria"""

    filtered_alerts = []

    for alert in alerts:
        # Priority filter
        if "min_priority" in filters:
            priority_levels = {p.value: i for i, p in enumerate(AlertPriority)}
            if priority_levels.get(alert.priority.value, 99) > priority_levels.get(filters["min_priority"], 0):
                continue

        # Status filter
        if "status" in filters:
            if isinstance(filters["status"], list):
                if alert.status.value not in filters["status"]:
                    continue
            else:
                if alert.status.value != filters["status"]:
                    continue

        # Category filter
        if "category" in filters:
            if isinstance(filters["category"], list):
                if alert.category.value not in filters["category"]:
                    continue
            else:
                if alert.category.value != filters["category"]:
                    continue

        # Source filter
        if "source_id" in filters:
            if isinstance(filters["source_id"], list):
                if alert.source_id not in filters["source_id"]:
                    continue
            else:
                if alert.source_id != filters["source_id"]:
                    continue

        # Time filter
        if "time_range" in filters:
            start_time = filters["time_range"].get("start")
            end_time = filters["time_range"].get("end")

            if start_time and alert.triggered_time < start_time:
                continue
            if end_time and alert.triggered_time > end_time:
                continue

        filtered_alerts.append(alert)

    return filtered_alerts

def prioritize_alerts(alerts: List[Alert]) -> List[Alert]:
    """Sort alerts by priority and age"""

    # Priority order (lower number = higher priority)
    priority_order = {
        AlertPriority.CRITICAL: 0,
        AlertPriority.HIGH: 1,
        AlertPriority.MEDIUM: 2,
        AlertPriority.LOW: 3,
        AlertPriority.INFO: 4
    }

    return sorted(alerts, key=lambda alert: (
        priority_order.get(alert.priority, 99),
        alert.triggered_time
    ))

def generate_alert_summary(alerts: List[Alert]) -> Dict[str, Any]:
    """Generate comprehensive alert summary"""

    if not alerts:
        return {
            "total_alerts": 0,
            "by_priority": {},
            "by_category": {},
            "by_status": {},
            "active_alerts": 0,
            "resolved_alerts": 0,
            "oldest_alert": None,
            "newest_alert": None
        }

    # Count by priority
    by_priority = defaultdict(int)
    for alert in alerts:
        by_priority[alert.priority.value] += 1

    # Count by category
    by_category = defaultdict(int)
    for alert in alerts:
        by_category[alert.category.value] += 1

    # Count by status
    by_status = defaultdict(int)
    for alert in alerts:
        by_status[alert.status.value] += 1

    # Find oldest and newest
    sorted_alerts = sorted(alerts, key=lambda a: a.triggered_time)
    oldest_alert = sorted_alerts[0].triggered_time if sorted_alerts else None
    newest_alert = sorted_alerts[-1].triggered_time if sorted_alerts else None

    summary = {
        "total_alerts": len(alerts),
        "by_priority": dict(by_priority),
        "by_category": dict(by_category),
        "by_status": dict(by_status),
        "active_alerts": by_status.get("active", 0),
        "resolved_alerts": by_status.get("resolved", 0),
        "oldest_alert": oldest_alert.isoformat() if oldest_alert else None,
        "newest_alert": newest_alert.isoformat() if newest_alert else None,
        "critical_count": by_priority.get("critical", 0),
        "high_count": by_priority.get("high", 0),
        "unresolved_count": len([a for a in alerts if a.status not in [AlertStatus.RESOLVED]]),
        "escalated_count": len([a for a in alerts if a.escalation_level > 0])
    }

    return summary

# Export configuration for external use
__all__ = [
    # Configuration
    "ALERTING_CONFIG",
    "AVAILABILITY_STATUS",

    # Data classes
    "AlertCondition",
    "Alert",
    "NotificationMessage",
    "RootCauseAnalysis",

    # Enums
    "AlertPriority",
    "AlertStatus",
    "NotificationChannel",
    "AlertCategory",

    # Utility functions
    "get_available_channels",
    "get_channel_info",
    "validate_alert_condition",
    "create_alert_from_condition",
    "calculate_alert_hash",
    "format_notification_message",
    "filter_alerts",
    "prioritize_alerts",
    "generate_alert_summary",

    # Classes (if available)
]

# Add available classes to exports
if ALERTING_MODULES_AVAILABLE:
    __all__.extend([
        "AlertEngine",
        "NotificationManager",
        "RootCauseAnalyzer",
        "AlertDashboard"
    ])

# Package version and status information
def get_package_info():
    """Get comprehensive package information"""
    return {
        "version": __version__,
        "phase": __phase__,
        "author": __author__,
        "available_channels": get_available_channels(),
        "total_available": len([v for v in AVAILABILITY_STATUS.values() if v]),
        "total_modules": len(AVAILABILITY_STATUS),
        "completion_percentage": len([v for v in AVAILABILITY_STATUS.values() if v]) / len(AVAILABILITY_STATUS) * 100,
        "implementation_status": AVAILABILITY_STATUS
    }
