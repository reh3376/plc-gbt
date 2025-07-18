#!/usr/bin/env python3
"""
🔐 CLI Session Manager

Session management for the PLC Control Loop CLI with persistence,
cleanup, and multi-session support.

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 21.1 - Core CLI Infrastructure
"""

import os
import json
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import logging

from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)

# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

@dataclass
class SessionActivity:
    """Session activity tracking"""
    timestamp: datetime
    command: str
    duration_ms: float
    success: bool
    error_message: Optional[str] = None

@dataclass 
class SessionStatistics:
    """Session statistics"""
    total_commands: int = 0
    successful_commands: int = 0
    failed_commands: int = 0
    total_duration_seconds: float = 0.0
    average_command_time_ms: float = 0.0
    most_used_commands: Dict[str, int] = None
    
    def __post_init__(self):
        if self.most_used_commands is None:
            self.most_used_commands = {}

class SessionManager:
    """Manages CLI sessions with persistence and cleanup"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".plc-control-loop"
        self.sessions_dir = self.config_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session tracking
        self.current_session_id: Optional[str] = None
        self.session_start_time: Optional[datetime] = None
        self.activity_log: List[SessionActivity] = []
        self.session_stats = SessionStatistics()
        
        # Auto cleanup old sessions on startup
        self._cleanup_old_sessions()
    
    def start_session(self, session_id: str, user_info: Dict[str, Any]) -> bool:
        """Start a new session"""
        try:
            self.current_session_id = session_id
            self.session_start_time = datetime.now(timezone.utc)
            self.activity_log = []
            self.session_stats = SessionStatistics()
            
            # Create session file
            session_data = {
                "session_id": session_id,
                "start_time": self.session_start_time.isoformat(),
                "user_info": user_info,
                "status": "active",
                "activity_log": [],
                "statistics": asdict(self.session_stats)
            }
            
            session_file = self.sessions_dir / f"{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            logger.info(f"Session started: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            return False
    
    def log_activity(self, command: str, duration_ms: float, success: bool, error_message: Optional[str] = None):
        """Log session activity"""
        if not self.current_session_id:
            return
        
        activity = SessionActivity(
            timestamp=datetime.now(timezone.utc),
            command=command,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message
        )
        
        self.activity_log.append(activity)
        
        # Update statistics
        self.session_stats.total_commands += 1
        if success:
            self.session_stats.successful_commands += 1
        else:
            self.session_stats.failed_commands += 1
        
        self.session_stats.total_duration_seconds += duration_ms / 1000
        self.session_stats.average_command_time_ms = (
            self.session_stats.total_duration_seconds * 1000 / self.session_stats.total_commands
        )
        
        # Track command usage
        if command in self.session_stats.most_used_commands:
            self.session_stats.most_used_commands[command] += 1
        else:
            self.session_stats.most_used_commands[command] = 1
        
        # Persist activity (async to avoid blocking)
        asyncio.create_task(self._persist_activity(activity))
    
    async def _persist_activity(self, activity: SessionActivity):
        """Persist activity to session file"""
        if not self.current_session_id:
            return
        
        try:
            session_file = self.sessions_dir / f"{self.current_session_id}.json"
            
            if session_file.exists():
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Add activity
                session_data['activity_log'].append(asdict(activity))
                session_data['statistics'] = asdict(self.session_stats)
                session_data['last_activity'] = datetime.now(timezone.utc).isoformat()
                
                with open(session_file, 'w') as f:
                    json.dump(session_data, f, indent=2, default=str)
        
        except Exception as e:
            logger.error(f"Failed to persist activity: {e}")
    
    def end_session(self) -> Optional[Dict[str, Any]]:
        """End current session and return summary"""
        if not self.current_session_id:
            return None
        
        try:
            end_time = datetime.now(timezone.utc)
            session_duration = (end_time - self.session_start_time).total_seconds() if self.session_start_time else 0
            
            # Create session summary
            summary = {
                "session_id": self.current_session_id,
                "start_time": self.session_start_time.isoformat() if self.session_start_time else None,
                "end_time": end_time.isoformat(),
                "duration_seconds": session_duration,
                "statistics": asdict(self.session_stats),
                "activity_count": len(self.activity_log)
            }
            
            # Update session file
            session_file = self.sessions_dir / f"{self.current_session_id}.json"
            if session_file.exists():
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                session_data['end_time'] = end_time.isoformat()
                session_data['duration_seconds'] = session_duration
                session_data['status'] = 'completed'
                session_data['statistics'] = asdict(self.session_stats)
                session_data['summary'] = summary
                
                with open(session_file, 'w') as f:
                    json.dump(session_data, f, indent=2, default=str)
            
            logger.info(f"Session ended: {self.current_session_id}")
            
            # Reset current session
            self.current_session_id = None
            self.session_start_time = None
            self.activity_log = []
            self.session_stats = SessionStatistics()
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            return None
    
    def get_session_summary(self) -> Optional[Dict[str, Any]]:
        """Get current session summary"""
        if not self.current_session_id or not self.session_start_time:
            return None
        
        now = datetime.now(timezone.utc)
        duration = (now - self.session_start_time).total_seconds()
        
        return {
            "session_id": self.current_session_id,
            "start_time": self.session_start_time.isoformat(),
            "current_time": now.isoformat(),
            "duration_seconds": duration,
            "statistics": asdict(self.session_stats),
            "recent_activity_count": len([a for a in self.activity_log if (now - a.timestamp).total_seconds() < 300])  # Last 5 minutes
        }
    
    def list_sessions(self, limit: int = 10, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List recent sessions"""
        sessions = []
        
        try:
            session_files = sorted(
                self.sessions_dir.glob("*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            for session_file in session_files[:limit]:
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    if status and session_data.get('status') != status:
                        continue
                    
                    # Create summary
                    session_summary = {
                        "session_id": session_data["session_id"],
                        "start_time": session_data["start_time"],
                        "end_time": session_data.get("end_time"),
                        "status": session_data.get("status", "unknown"),
                        "duration_seconds": session_data.get("duration_seconds", 0),
                        "user": session_data.get("user_info", {}).get("username", "unknown"),
                        "commands_executed": session_data.get("statistics", {}).get("total_commands", 0),
                        "success_rate": self._calculate_success_rate(session_data.get("statistics", {}))
                    }
                    
                    sessions.append(session_summary)
                    
                except Exception as e:
                    logger.warning(f"Failed to read session file {session_file}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
        
        return sessions
    
    def get_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific session"""
        session_file = self.sessions_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to get session details: {e}")
            return None
    
    def _cleanup_old_sessions(self, days_old: int = 30):
        """Clean up old session files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cleaned_count = 0
            
            for session_file in self.sessions_dir.glob("*.json"):
                try:
                    # Check file modification time
                    if session_file.stat().st_mtime < cutoff_date.timestamp():
                        session_file.unlink()
                        cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to clean up session file {session_file}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old session files")
        
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
    
    def _calculate_success_rate(self, statistics: Dict[str, Any]) -> float:
        """Calculate success rate from statistics"""
        total = statistics.get("total_commands", 0)
        successful = statistics.get("successful_commands", 0)
        
        if total == 0:
            return 0.0
        
        return (successful / total) * 100
    
    def export_session_data(self, session_id: str, format: str = "json") -> Optional[str]:
        """Export session data in specified format"""
        session_data = self.get_session_details(session_id)
        
        if not session_data:
            return None
        
        try:
            if format == "json":
                return json.dumps(session_data, indent=2, default=str)
            elif format == "csv":
                # Export activity log as CSV
                import csv
                import io
                
                output = io.StringIO()
                
                if "activity_log" in session_data:
                    writer = csv.DictWriter(output, fieldnames=["timestamp", "command", "duration_ms", "success", "error_message"])
                    writer.writeheader()
                    writer.writerows(session_data["activity_log"])
                
                return output.getvalue()
            else:
                return None
        
        except Exception as e:
            logger.error(f"Failed to export session data: {e}")
            return None 