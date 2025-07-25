'use client'

import { useState, useEffect, useCallback } from 'react'
import { X, Save, Circle } from 'lucide-react'
import { cn } from '@/lib/utils/cn'
import { useFileStore } from '@/lib/stores/file-store'
import { MonacoEditor } from './monaco-editor'

interface EditorTab {
  fileId: string
  fileName: string
  filePath: string
  content: string
  isDirty: boolean
  isActive: boolean
}

interface TabbedEditorProps {
  className?: string
}

export function TabbedEditor({ className }: TabbedEditorProps) {
  const [tabs, setTabs] = useState<EditorTab[]>([])
  const [activeTabId, setActiveTabId] = useState<string | null>(null)
  
  const { 
    selectedFileId, 
    findFileById, 
    markFileAsModified
  } = useFileStore()

  // Sample file contents for demo
  const getSampleContent = (fileName: string): string => {
    const ext = fileName.split('.').pop()?.toLowerCase()
    
    switch (ext) {
      case 'json':
        if (fileName.includes('PID') || fileName.includes('Temperature')) {
          return `{
  "controlLoop": {
    "name": "Temperature Control Loop",
    "type": "PID",
    "parameters": {
      "kp": 1.2,
      "ki": 0.8,
      "kd": 0.1,
      "setpoint": 75.0,
      "processVariable": 72.3,
      "output": 45.2,
      "units": "°C"
    },
    "tuning": {
      "method": "Ziegler-Nichols",
      "autoTune": true,
      "lastTuned": "2025-01-17T14:30:00Z"
    },
    "alarms": {
      "highAlarm": 85.0,
      "lowAlarm": 65.0,
      "deviationAlarm": 5.0
    }
  }
}`
        } else if (fileName.includes('Pressure')) {
          return `{
  "controlLoop": {
    "name": "Pressure Control Loop", 
    "type": "PIDE",
    "parameters": {
      "kp": 2.5,
      "ki": 1.1,
      "kd": 0.05,
      "setpoint": 150.0,
      "processVariable": 148.7,
      "output": 52.1,
      "units": "PSI"
    },
    "advanced": {
      "feedforward": true,
      "cascade": false,
      "ratio": 1.0
    }
  }
}`
        } else if (fileName.includes('workflow')) {
          return `{
  "workflow": {
    "name": "Startup Sequence",
    "description": "Standard plant startup procedure",
    "steps": [
      {
        "id": 1,
        "action": "Check Safety Systems",
        "type": "safety_check",
        "timeout": 30
      },
      {
        "id": 2, 
        "action": "Initialize Control Loops",
        "type": "control_init",
        "loops": ["temperature", "pressure", "flow"]
      },
      {
        "id": 3,
        "action": "Start Production",
        "type": "production_start",
        "confirmation_required": true
      }
    ]
  }
}`
        }
        return `{
  "plcProject": {
    "name": "New PLC Project",
    "version": "1.0.0",
    "created": "${new Date().toISOString()}",
    "description": "Industrial automation project"
  }
}`

      case 'st':
      case 'txt':
        return `(* Structured Text Program *)
PROGRAM Temperature_Control
VAR
    TemperatureSetpoint : REAL := 75.0;
    TemperaturePV : REAL;
    HeaterOutput : REAL;
    
    (* PID Controller *)
    TempController : PID;
    
    (* Timers *)
    StartupTimer : TON;
    AlarmTimer : TON;
END_VAR

(* Main Control Logic *)
IF StartupTimer.Q THEN
    (* PID Control *)
    TempController(
        PV := TemperaturePV,
        SP := TemperatureSetpoint,
        CV => HeaterOutput
    );
    
    (* Alarm Logic *)
    IF ABS(TemperaturePV - TemperatureSetpoint) > 5.0 THEN
        AlarmTimer(IN := TRUE, PT := T#10s);
    ELSE
        AlarmTimer(IN := FALSE);
    END_IF;
END_IF;

(* Startup Sequence *)
StartupTimer(IN := TRUE, PT := T#30s);

END_PROGRAM`

      case 'acd':
      case 'l5x':
        return `<?xml version="1.0" encoding="UTF-8"?>
<RSLogix5000Content SchemaRevision="1.0">
  <Controller>
    <Name>DistillationControl</Name>
    <ProcessorType>1756-L73</ProcessorType>
    <MajorRev>32</MajorRev>
    <MinorRev>11</MinorRev>
    <TimeSlice>20</TimeSlice>
    <ShareUnusedTimeSlice>1</ShareUnusedTimeSlice>
    
    <Tags>
      <Tag Name="Temperature_PV" TagType="Base" DataType="REAL" Usage="Input">
        <Data Format="L5K">0.0</Data>
      </Tag>
      <Tag Name="Temperature_SP" TagType="Base" DataType="REAL" Usage="InOut">
        <Data Format="L5K">75.0</Data>
      </Tag>
      <Tag Name="Heater_Output" TagType="Base" DataType="REAL" Usage="Output">
        <Data Format="L5K">0.0</Data>
      </Tag>
    </Tags>
    
    <Programs>
      <Program Name="MainProgram" Type="PROGRAM">
        <Routines>
          <Routine Name="MainRoutine" Type="RLL">
            <!-- Ladder Logic would be defined here -->
          </Routine>
        </Routines>
      </Program>
    </Programs>
  </Controller>
</RSLogix5000Content>`

      default:
        return `// ${fileName}
// PLC-GBT Industrial Automation IDE

Welcome to the PLC-GBT IDE!

This file is ready for editing. You can:
- Write Structured Text programs (.st files)
- Configure control loops (.json files)
- Import/Export PLC projects (.acd, .l5x files)
- Create automation workflows

Start typing to begin...`
    }
  }

  // Open a file in a new tab or switch to existing tab
  const openFile = useCallback((fileId: string) => {
    const file = findFileById(fileId)
    if (!file || file.type === 'folder') return

    // Check if tab already exists
    const existingTabIndex = tabs.findIndex(tab => tab.fileId === fileId)
    
    if (existingTabIndex >= 0) {
      // Switch to existing tab
      setActiveTabId(fileId)
    } else {
      // Create new tab
      const newTab: EditorTab = {
        fileId,
        fileName: file.name,
        filePath: file.path,
        content: getSampleContent(file.name),
        isDirty: false,
        isActive: true
      }

      const newTabs = tabs.map(tab => ({ ...tab, isActive: false }))
      newTabs.push(newTab)
      
      setTabs(newTabs)
      setActiveTabId(fileId)
    }
  }, [findFileById, tabs, setActiveTabId, setTabs])

  // Close a tab
  const closeTab = (fileId: string, event?: React.MouseEvent) => {
    event?.stopPropagation()
    
    const tabIndex = tabs.findIndex(tab => tab.fileId === fileId)
    if (tabIndex === -1) return

    const newTabs = tabs.filter(tab => tab.fileId !== fileId)
    
    // If closing active tab, switch to adjacent tab
    if (activeTabId === fileId) {
      if (newTabs.length === 0) {
        setActiveTabId(null)
      } else {
        const newActiveIndex = Math.min(tabIndex, newTabs.length - 1)
        setActiveTabId(newTabs[newActiveIndex].fileId)
      }
    }
    
    setTabs(newTabs)
    
    // Clear file modification state
    markFileAsModified(fileId, false)
  }

  // Update tab content and mark as dirty
  const updateTabContent = (fileId: string, newContent: string) => {
    setTabs(prevTabs => 
      prevTabs.map(tab => 
        tab.fileId === fileId 
          ? { ...tab, content: newContent, isDirty: true }
          : tab
      )
    )
  }

  // Save tab content
  const saveTab = (fileId: string, event?: React.MouseEvent) => {
    event?.stopPropagation()
    
    setTabs(prevTabs => 
      prevTabs.map(tab => 
        tab.fileId === fileId 
          ? { ...tab, isDirty: false }
          : tab
      )
    )
    
    markFileAsModified(fileId, false)
    
    // In a real app, this would save to the backend
    console.log(`Saved file: ${fileId}`)
  }

  // Listen for file selection changes
  useEffect(() => {
    if (selectedFileId && selectedFileId !== activeTabId) {
      openFile(selectedFileId)
    }
  }, [selectedFileId, activeTabId, openFile])

  // Get active tab
  const activeTab = tabs.find(tab => tab.fileId === activeTabId)

  return (
    <div className={cn("h-full flex flex-col bg-[#1e1e1e]", className)}>
      {/* Tab Bar */}
      {tabs.length > 0 && (
        <div className="flex bg-[#2d2d30] border-b border-[#3c3c3c] overflow-x-auto">
          {tabs.map((tab) => {
            const file = findFileById(tab.fileId)
            const hasUnsavedChanges = file?.hasUnsavedChanges || tab.isDirty
            
            return (
              <div
                key={tab.fileId}
                onClick={() => setActiveTabId(tab.fileId)}
                className={cn(
                  "flex items-center px-3 py-2 border-r border-[#3c3c3c] cursor-pointer group",
                  "min-w-[120px] max-w-[200px] relative",
                  activeTabId === tab.fileId
                    ? "bg-[#1e1e1e] text-[#cccccc]"
                    : "bg-[#2d2d30] text-[#969696] hover:text-[#cccccc]"
                )}
              >
                {/* File name */}
                <span className="flex-1 truncate text-sm">
                  {tab.fileName}
                </span>

                {/* Unsaved changes indicator */}
                {hasUnsavedChanges && (
                  <Circle className="w-2 h-2 ml-2 fill-[#4fc3f7] text-[#4fc3f7]" />
                )}

                {/* Save button (appears on hover if dirty) */}
                {hasUnsavedChanges && (
                  <button
                    onClick={(e) => saveTab(tab.fileId, e)}
                    className="ml-1 opacity-0 group-hover:opacity-100 p-1 hover:bg-[#3c3c3c] rounded transition-opacity"
                    title="Save"
                  >
                    <Save className="w-3 h-3" />
                  </button>
                )}

                {/* Close button */}
                <button
                  onClick={(e) => closeTab(tab.fileId, e)}
                  className="ml-1 opacity-0 group-hover:opacity-100 p-1 hover:bg-[#3c3c3c] rounded transition-opacity"
                  title="Close"
                >
                  <X className="w-3 h-3" />
                </button>

                {/* Active tab indicator */}
                {activeTabId === tab.fileId && (
                  <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#007acc]" />
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Editor Area */}
      <div className="flex-1 overflow-hidden">
        {activeTab ? (
          <MonacoEditor
            fileId={activeTab.fileId}
            value={activeTab.content}
            onChange={(newContent) => updateTabContent(activeTab.fileId, newContent)}
          />
        ) : (
          <div className="h-full flex items-center justify-center bg-[#1e1e1e]">
            <div className="text-center text-[#969696]">
              <div className="text-4xl mb-4">📁</div>
              <h3 className="text-lg font-medium mb-2">No file open</h3>
              <p className="text-sm">
                Select a file from the explorer to start editing
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Status bar for editor */}
      {activeTab && (
        <div className="h-6 bg-[#007acc] flex items-center justify-between px-3 text-white text-xs">
          <div className="flex items-center space-x-4">
            <span>
              {activeTab.fileName}
            </span>
            <span>
              {findFileById(activeTab.fileId)?.fileType?.toUpperCase() || 'TXT'}
            </span>
          </div>
          
          <div className="flex items-center space-x-4">
            {activeTab.isDirty && (
              <span className="text-[#cce7f0]">Unsaved changes</span>
            )}
            <span>
              Lines: {activeTab.content.split('\n').length}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

// Default export for React.lazy() compatibility
export default TabbedEditor 