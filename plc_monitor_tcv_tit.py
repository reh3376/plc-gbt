#!/usr/bin/env python3
"""
🖥️ PLC Tag Monitoring Script - AI Task Orchestrator Implementation

Task: Connect to PLC at 10.4.4.2:0 and monitor TCV_4110 & TIT_4111 for 30 seconds

AI Task Orchestrator Implementation
=====================================
Task Classification: MODERATE (PLC monitoring with time constraints)
Context Management: Real-time data collection with safety enforcement
Methodology Source: AI_TASK_ORCHESTRATOR_GUIDE.md

Objectives:
- Connect to CLX PLC at 10.4.4.2 slot 0 (read-only)
- Monitor tags TCV_4110 and TIT_4111 for exactly 30 seconds
- Collect timestamps and values for analysis
- Disconnect cleanly and output comprehensive results
- Ensure production safety with read-only operations

Author: AI Task Orchestrator
Created: 2025-01-18
Dependencies: pylogix for ControlLogix communication
"""

import sys
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import traceback

# Check for pylogix availability
try:
    from pylogix import PLC
    PYLOGIX_AVAILABLE = True
    print("✅ pylogix library available")
except ImportError:
    PYLOGIX_AVAILABLE = False
    print("❌ pylogix library not available")
    print("💡 Install with: pip install pylogix")
    sys.exit(1)

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class TagReading:
    """Individual tag reading with timestamp"""
    tag_name: str
    value: Any
    data_type: str
    quality: str
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None

@dataclass
class MonitoringSession:
    """Complete monitoring session results"""
    session_id: str
    plc_host: str
    plc_slot: int
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: float
    tags_monitored: List[str]
    total_readings: int
    successful_readings: int
    failed_readings: int
    readings: List[TagReading]
    connection_status: str
    errors: List[str]

# =============================================================================
# PLC MONITORING CLASS
# =============================================================================

class PLCTagMonitor:
    """Safe PLC tag monitoring with read-only enforcement"""
    
    def __init__(self, host: str, slot: int = 0):
        self.host = host
        self.slot = slot
        self.plc = None
        self.connected = False
        self.session_id = f"monitor_{int(time.time())}"
        
        # Safety enforcement
        self.read_only_enforced = True
        print(f"🔒 Read-only mode enforced for safety")
        
    def connect(self) -> bool:
        """Connect to PLC with safety validation"""
        try:
            print(f"🔌 Connecting to PLC: {self.host}:{self.slot}")
            
            # Create PLC connection
            self.plc = PLC()
            self.plc.IPAddress = self.host
            self.plc.ProcessorSlot = self.slot
            
            # Test connection with PLC time read
            print("⏱️  Testing connection with PLC time read...")
            test_result = self.plc.GetPLCTime()
            
            if test_result.Status == "Success":
                self.connected = True
                print(f"✅ Connected to CLX PLC successfully!")
                print(f"📅 PLC Time: {test_result.Value}")
                print(f"🔒 Connection Mode: READ-ONLY (Safety Enforced)")
                return True
            else:
                print(f"❌ PLC connection failed: {test_result.Status}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Safely disconnect from PLC"""
        try:
            if self.plc:
                # pylogix doesn't require explicit disconnect, but we'll clean up
                self.plc = None
            
            self.connected = False
            print("🔌 Disconnected from PLC")
            return True
            
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")
            return False
    
    def read_tag(self, tag_name: str) -> TagReading:
        """Read single tag with error handling"""
        timestamp = datetime.now()
        
        if not self.connected or not self.plc:
            return TagReading(
                tag_name=tag_name,
                value=None,
                data_type="Unknown",
                quality="BAD",
                timestamp=timestamp,
                success=False,
                error_message="PLC not connected"
            )
        
        try:
            # Read tag value
            result = self.plc.Read(tag_name)
            
            if result.Status == "Success":
                return TagReading(
                    tag_name=result.TagName,
                    value=result.Value,
                    data_type=str(type(result.Value).__name__),
                    quality="GOOD",
                    timestamp=timestamp,
                    success=True
                )
            else:
                return TagReading(
                    tag_name=tag_name,
                    value=None,
                    data_type="Unknown", 
                    quality="BAD",
                    timestamp=timestamp,
                    success=False,
                    error_message=f"Read failed: {result.Status}"
                )
                
        except Exception as e:
            return TagReading(
                tag_name=tag_name,
                value=None,
                data_type="Unknown",
                quality="BAD", 
                timestamp=timestamp,
                success=False,
                error_message=f"Exception: {str(e)}"
            )
    
    def monitor_tags(self, tags: List[str], duration_seconds: int = 30, 
                    sample_interval: float = 1.0) -> MonitoringSession:
        """Monitor multiple tags for specified duration"""
        
        print(f"\n🎯 Starting tag monitoring session")
        print(f"📊 Tags: {', '.join(tags)}")
        print(f"⏱️  Duration: {duration_seconds} seconds")
        print(f"📈 Sample interval: {sample_interval} seconds")
        print(f"🔒 Mode: READ-ONLY")
        
        # Initialize session
        start_time = datetime.now()
        session = MonitoringSession(
            session_id=self.session_id,
            plc_host=self.host,
            plc_slot=self.slot,
            start_time=start_time,
            end_time=None,
            duration_seconds=duration_seconds,
            tags_monitored=tags,
            total_readings=0,
            successful_readings=0,
            failed_readings=0,
            readings=[],
            connection_status="CONNECTED" if self.connected else "DISCONNECTED",
            errors=[]
        )
        
        if not self.connected:
            session.errors.append("PLC not connected - cannot monitor tags")
            session.end_time = datetime.now()
            return session
        
        # Calculate end time
        end_time = start_time + timedelta(seconds=duration_seconds)
        sample_count = 0
        
        print(f"\n🚀 Monitoring started at {start_time.strftime('%H:%M:%S')}")
        print(f"🏁 Will stop at {end_time.strftime('%H:%M:%S')}")
        print("📝 Live readings:")
        
        try:
            while datetime.now() < end_time:
                sample_count += 1
                current_time = datetime.now()
                elapsed = (current_time - start_time).total_seconds()
                
                print(f"\n📊 Sample {sample_count} (t={elapsed:.1f}s):")
                
                # Read all tags
                for tag_name in tags:
                    reading = self.read_tag(tag_name)
                    session.readings.append(reading)
                    session.total_readings += 1
                    
                    if reading.success:
                        session.successful_readings += 1
                        print(f"  ✅ {reading.tag_name}: {reading.value} ({reading.data_type})")
                    else:
                        session.failed_readings += 1
                        print(f"  ❌ {reading.tag_name}: {reading.error_message}")
                        session.errors.append(f"Tag {tag_name}: {reading.error_message}")
                
                # Wait for next sample (if time remaining)
                next_sample_time = start_time + timedelta(seconds=sample_count * sample_interval)
                if next_sample_time < end_time:
                    sleep_time = (next_sample_time - datetime.now()).total_seconds()
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                else:
                    break
                    
        except KeyboardInterrupt:
            print(f"\n⏹️  Monitoring interrupted by user")
            session.errors.append("Monitoring interrupted by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
            session.errors.append(f"Monitoring error: {str(e)}")
        
        # Finalize session
        session.end_time = datetime.now()
        actual_duration = (session.end_time - session.start_time).total_seconds()
        session.duration_seconds = actual_duration
        
        print(f"\n🏁 Monitoring completed at {session.end_time.strftime('%H:%M:%S')}")
        print(f"⏱️  Actual duration: {actual_duration:.1f} seconds")
        
        return session

# =============================================================================
# MAIN EXECUTION FUNCTION
# =============================================================================

def main():
    """Main execution following AI Task Orchestrator methodology"""
    
    print("🖥️  PLC Tag Monitoring Script")
    print("=" * 50)
    print("📋 Task: Monitor TCV_4110 & TIT_4111 for 30 seconds")
    print("🎯 PLC: 10.4.4.2:0")
    print("🔒 Mode: READ-ONLY (Safety Enforced)")
    print("=" * 50)
    
    # Configuration
    PLC_HOST = "10.4.4.2"
    PLC_SLOT = 0
    TAGS_TO_MONITOR = ["TCV_4110", "TIT_4111"]
    MONITORING_DURATION = 30  # seconds
    SAMPLE_INTERVAL = 2.0     # seconds between readings
    
    # Initialize monitor
    monitor = PLCTagMonitor(PLC_HOST, PLC_SLOT)
    session = None
    
    try:
        # Step 1: Connect to PLC
        print(f"\n🔌 STEP 1: Connecting to PLC")
        if not monitor.connect():
            print(f"❌ Failed to connect to PLC {PLC_HOST}:{PLC_SLOT}")
            print(f"💡 Check:")
            print(f"   - PLC is powered and responding")
            print(f"   - Network connectivity to {PLC_HOST}")
            print(f"   - PLC slot {PLC_SLOT} is correct")
            print(f"   - Firewall allows communication")
            sys.exit(1)
        
        # Step 2: Monitor tags
        print(f"\n📊 STEP 2: Monitoring Tags")
        session = monitor.monitor_tags(
            tags=TAGS_TO_MONITOR,
            duration_seconds=MONITORING_DURATION,
            sample_interval=SAMPLE_INTERVAL
        )
        
        # Step 3: Disconnect
        print(f"\n🔌 STEP 3: Disconnecting from PLC")
        monitor.disconnect()
        
        # Step 4: Output results
        print(f"\n📈 STEP 4: Results Summary")
        print("=" * 50)
        
        # Summary statistics
        success_rate = (session.successful_readings / session.total_readings * 100) if session.total_readings > 0 else 0
        
        print(f"Session ID: {session.session_id}")
        print(f"PLC: {session.plc_host}:{session.plc_slot}")
        print(f"Duration: {session.duration_seconds:.1f} seconds")
        print(f"Tags monitored: {', '.join(session.tags_monitored)}")
        print(f"Total readings: {session.total_readings}")
        print(f"Successful: {session.successful_readings}")
        print(f"Failed: {session.failed_readings}")
        print(f"Success rate: {success_rate:.1f}%")
        
        # Tag value summary
        print(f"\n📊 Tag Value Summary:")
        for tag in TAGS_TO_MONITOR:
            tag_readings = [r for r in session.readings if r.tag_name == tag and r.success]
            if tag_readings:
                values = [r.value for r in tag_readings]
                print(f"  {tag}:")
                print(f"    Samples: {len(values)}")
                print(f"    Latest: {values[-1]}")
                if len(values) > 1:
                    print(f"    Min: {min(values)}")
                    print(f"    Max: {max(values)}")
                    print(f"    Avg: {sum(values)/len(values):.3f}")
            else:
                print(f"  {tag}: No successful readings")
        
        # Error summary
        if session.errors:
            print(f"\n⚠️  Errors encountered:")
            for error in session.errors:
                print(f"  - {error}")
        
        # Detailed readings (JSON output)
        print(f"\n🔍 Detailed Readings (JSON):")
        print("=" * 50)
        
        # Convert session to JSON-serializable format
        session_dict = asdict(session)
        
        # Convert datetime objects to ISO strings
        session_dict['start_time'] = session.start_time.isoformat()
        if session.end_time:
            session_dict['end_time'] = session.end_time.isoformat()
        
        for reading in session_dict['readings']:
            reading['timestamp'] = datetime.fromisoformat(reading['timestamp']).isoformat() if isinstance(reading['timestamp'], str) else reading['timestamp'].isoformat()
        
        # Output JSON
        print(json.dumps(session_dict, indent=2, default=str))
        
        print("\n✅ Monitoring completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print(f"Stack trace:")
        traceback.print_exc()
        return 1
        
    finally:
        # Ensure disconnection
        if monitor.connected:
            print(f"\n🔧 Ensuring PLC disconnection...")
            monitor.disconnect()

if __name__ == "__main__":
    sys.exit(main()) 