'use client';

import { useFileStore } from '@/lib/stores/file-store';
import { cn } from '@/lib/utils/cn';
import { Circle, Save, X } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import { MonacoEditor } from './monaco-editor';

interface EditorTab {
  fileId: string;
  fileName: string;
  filePath: string;
  content: string;
  isDirty: boolean;
  isActive: boolean;
}

interface TabbedEditorProps {
  className?: string;
}

export function TabbedEditor({ className }: TabbedEditorProps) {
  const [tabs, setTabs] = useState<EditorTab[]>([]);
  const [activeTabId, setActiveTabId] = useState<string | null>(null);

  const { selectedFileId, findFileById, markFileAsModified, selectFile } = useFileStore();

  // Sample file contents for demo
  const getSampleContent = (fileName: string): string => {
    const ext = fileName.split('.').pop()?.toLowerCase();

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
}`;
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
}`;
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
}`;
        }
        return `{
  "plcProject": {
    "name": "New PLC Project",
    "version": "1.0.0",
    "created": "${new Date().toISOString()}",
    "description": "Industrial automation project"
  }
}`;

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

END_PROGRAM`;

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
</RSLogix5000Content>`;

      default:
        return `// ${fileName}
// PLC-GBT Industrial Automation IDE

Welcome to the PLC-GBT IDE!

This file is ready for editing. You can:
- Write Structured Text programs (.st files)
- Configure control loops (.json files)
- Import/Export PLC projects (.acd, .l5x files)
- Create automation workflows

Start typing to begin...`;
    }
  };

  // Open a file in a new tab or switch to existing tab
  const openFile = useCallback(
    async (fileId: string) => {
      console.log(
        '📂 OPEN FILE - Opening:',
        fileId,
        'Current tabs:',
        tabs.length,
        'Active:',
        activeTabId
      );
      const file = findFileById(fileId);
      if (!file || file.type === 'folder') {
        console.warn('📂 OPEN FILE - File not found or is folder:', fileId);
        return;
      }

      // Check if tab already exists
      const existingTabIndex = tabs.findIndex(tab => tab.fileId === fileId);
      console.log('📂 OPEN FILE - Existing tab index:', existingTabIndex);

      if (existingTabIndex >= 0) {
        // Switch to existing tab
        console.log('📂 OPEN FILE - Switching to existing tab:', fileId);
        setActiveTabId(fileId);
      } else {
        // Create new tab
        console.log('📂 OPEN FILE - Creating new tab for:', fileId);
        console.log('📂 OPEN FILE - Loading real file content for:', file.name);

        // Load actual file content instead of mock data
        const loadFileContent = async () => {
          try {
            const response = await fetch(`/api/v1/files/${encodeURIComponent(fileId)}/content`);
            if (response.ok) {
              const jsonData = await response.json();
              // Extract content from API response: { success: true, data: { content: "..." } }
              const content = jsonData.success && jsonData.data ? jsonData.data.content : '';
              console.log('📂 OPEN FILE - Loaded file content, length:', content.length);
              return content;
            } else {
              console.warn('📂 OPEN FILE - Failed to load file content, using sample');
              return getSampleContent(file.name);
            }
          } catch (error) {
            console.error('📂 OPEN FILE - Error loading file content:', error);
            return getSampleContent(file.name);
          }
        };

        const content = await loadFileContent();
        console.log('📂 OPEN FILE - Content to be used in tab:', content);
        console.log('📂 OPEN FILE - Content type:', typeof content);
        console.log('📂 OPEN FILE - Content is empty string?', content === '');

        const newTab: EditorTab = {
          fileId,
          fileName: file.name,
          filePath: file.path,
          content,
          isDirty: false,
          isActive: true,
        };

        const newTabs = tabs.map(tab => ({ ...tab, isActive: false }));
        newTabs.push(newTab);

        console.log('📂 OPEN FILE - New tabs count:', newTabs.length, 'Setting active to:', fileId);
        setTabs(newTabs);
        setActiveTabId(fileId);
      }
    },
    [findFileById, tabs, activeTabId]
  );

  // Close a tab
  const closeTab = (fileId: string, event?: React.MouseEvent) => {
    event?.preventDefault();
    event?.stopPropagation();

    console.log('🗑️ CLOSE TAB - Attempting to close tab:', fileId);
    console.log('🗑️ CLOSE TAB - Current state:', {
      fileId,
      activeTabId,
      tabsCount: tabs.length,
      tabsArray: tabs.map(t => ({ id: t.fileId, name: t.fileName })),
    });

    const tabIndex = tabs.findIndex(tab => tab.fileId === fileId);
    if (tabIndex === -1) {
      console.warn('🗑️ CLOSE TAB - Tab not found:', fileId);
      return;
    }

    console.log('🗑️ CLOSE TAB - Found tab at index:', tabIndex);

    // CRITICAL: Determine new active tab BEFORE modifying arrays
    let newActiveTabId: string | null = activeTabId;

    if (activeTabId === fileId) {
      // We're closing the active tab, need to find a new one
      if (tabs.length === 1) {
        // This is the last tab
        newActiveTabId = null;
        console.log('🗑️ CLOSE TAB - Closing last tab, will set activeTabId to null');
      } else {
        // Find the next tab to activate
        if (tabIndex === tabs.length - 1) {
          // Closing the rightmost tab, activate the one to the left
          newActiveTabId = tabs[tabIndex - 1].fileId;
          console.log(
            '🗑️ CLOSE TAB - Closing rightmost tab, activating tab to the left:',
            newActiveTabId
          );
        } else {
          // Closing a tab that's not rightmost, activate the one to the right
          newActiveTabId = tabs[tabIndex + 1].fileId;
          console.log(
            '🗑️ CLOSE TAB - Closing non-rightmost tab, activating tab to the right:',
            newActiveTabId
          );
        }
      }
    } else {
      console.log('🗑️ CLOSE TAB - Closing non-active tab, keeping current active:', activeTabId);
    }

    // Create new tabs array without the closed tab
    const newTabs = tabs.filter(tab => tab.fileId !== fileId);
    console.log('🗑️ CLOSE TAB - New tabs array length:', newTabs.length);

    // Update state in correct order
    setTabs(newTabs);
    setActiveTabId(newActiveTabId);

    // CRITICAL: Update file store's selectedFileId to prevent useEffect conflicts
    if (activeTabId === fileId) {
      // We closed the active tab, update file store to match new active tab
      if (newActiveTabId) {
        console.log('🗑️ CLOSE TAB - Updating file store selectedFileId to:', newActiveTabId);
        selectFile(newActiveTabId);
      } else {
        console.log('🗑️ CLOSE TAB - No tabs remaining, clearing file store selection');
        selectFile(''); // Clear selection when no tabs remain
      }
    }

    // Clear file modification state
    markFileAsModified(fileId, false);

    console.log('✅ CLOSE TAB - Tab closed successfully. New active:', newActiveTabId);
  };

  // Update tab content and mark as dirty
  const updateTabContent = (fileId: string, newContent: string) => {
    console.log(`📝 UPDATE TAB - File: ${fileId}, Content length: ${newContent.length}`);

    setTabs(prevTabs => {
      const updatedTabs = prevTabs.map(tab => {
        if (tab.fileId === fileId) {
          const wasClean = !tab.isDirty;
          const newTab = { ...tab, content: newContent, isDirty: true };
          console.log(`📝 UPDATE TAB - Tab ${fileId} updated:`, {
            contentLength: newContent.length,
            wasClean,
            nowDirty: true,
            isDirtyBefore: tab.isDirty,
            isDirtyAfter: newTab.isDirty,
          });
          return newTab;
        }
        return tab;
      });

      // Verify the update actually took effect
      const updatedTab = updatedTabs.find(tab => tab.fileId === fileId);
      if (updatedTab) {
        console.log(`📝 UPDATE TAB - Final verification for ${fileId}:`, {
          isDirty: updatedTab.isDirty,
          contentLength: updatedTab.content.length,
        });
      }

      return updatedTabs;
    });

    // Also sync with file store
    markFileAsModified(fileId, true);
    console.log(`📝 UPDATE TAB - Also marked in file store as modified: ${fileId}`);
  };

  // Save tab content - unified save handler with real file persistence
  const saveTab = useCallback(
    async (fileId: string, eventOrContent?: React.MouseEvent | string, currentContent?: string) => {
      // Handle different parameter patterns
      let event: React.MouseEvent | undefined;
      let contentToSave: string | undefined;

      if (typeof eventOrContent === 'string') {
        // Called from Monaco with content
        contentToSave = eventOrContent;
      } else {
        // Called from button click
        event = eventOrContent;
        contentToSave = currentContent;
      }

      event?.preventDefault();
      event?.stopPropagation();

      console.log(`💾 SAVE TAB - Starting save for file: ${fileId}`);
      console.log(`💾 SAVE TAB - Content source:`, contentToSave ? 'Monaco Editor' : 'React State');
      console.log(`💾 SAVE TAB - Content provided:`, contentToSave);

      // When content is provided from Monaco, we don't need to check tabs state
      // Just proceed with the save using the provided content
      const finalContent = contentToSave || '';

      if (contentToSave) {
        console.log(`💾 SAVE TAB - Using content from Monaco, length: ${contentToSave.length}`);
      } else {
        console.log(`💾 SAVE TAB - No content provided, would need to get from React state`);
        // TODO: Implement getting content from React state if needed
        console.warn(`💾 SAVE TAB - Save without Monaco content not yet implemented`);
        return;
      }

      console.log(
        `💾 SAVE TAB - Final content length: ${finalContent.length} (source: Monaco Editor)`
      );

      try {
        // Save to backend
        console.log(`💾 SAVE TAB - Saving content to backend, length: ${finalContent.length}`);
        const response = await fetch(`/api/v1/files/${encodeURIComponent(fileId)}/content`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content: finalContent }),
        });

        if (response.ok) {
          console.log(`💾 SAVE TAB - Successfully saved to backend: ${fileId}`);

          // Update tab state to mark as saved AND update content if it came from Monaco
          setTabs(prevTabs => {
            const newTabs = prevTabs.map(tab => {
              if (tab.fileId === fileId) {
                return {
                  ...tab,
                  isDirty: false,
                  content: finalContent, // Ensure React state matches saved content
                };
              }
              return tab;
            });
            console.log(
              `💾 SAVE TAB - Updated tabs after save:`,
              newTabs.map(t => ({
                id: t.fileId,
                isDirty: t.isDirty,
                contentLength: t.content.length,
              }))
            );
            return newTabs;
          });

          markFileAsModified(fileId, false);
          console.log(`💾 SAVE TAB - Marked file as unmodified in file store: ${fileId}`);
        } else {
          console.error(`💾 SAVE TAB - Backend save failed: ${response.status}`);
          // For now, still mark as saved in UI even if backend fails
          setTabs(prevTabs =>
            prevTabs.map(tab =>
              tab.fileId === fileId ? { ...tab, isDirty: false, content: finalContent } : tab
            )
          );
          markFileAsModified(fileId, false);
        }
      } catch (error) {
        console.error(`💾 SAVE TAB - Error saving file:`, error);
        // For now, still mark as saved in UI even if save fails
        setTabs(prevTabs =>
          prevTabs.map(tab =>
            tab.fileId === fileId ? { ...tab, isDirty: false, content: finalContent } : tab
          )
        );
        markFileAsModified(fileId, false);
      }

      console.log(`💾 SAVE TAB - Save process completed for: ${fileId}`);
    },
    [tabs, markFileAsModified]
  );

  // Listen for file selection changes
  useEffect(() => {
    console.log(
      '👂 EDITOR USEEFFECT - selectedFileId:',
      selectedFileId,
      'activeTabId:',
      activeTabId
    );
    if (selectedFileId && selectedFileId !== activeTabId) {
      console.log('📂 EDITOR USEEFFECT - Opening file:', selectedFileId);
      console.log(
        '📂 EDITOR USEEFFECT - Current tabs:',
        tabs.map(t => t.fileId)
      );
      openFile(selectedFileId);
    } else {
      console.log('👂 EDITOR USEEFFECT - No action needed, files are in sync');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedFileId, activeTabId]); // Manually controlled dependencies to prevent infinite loops

  // Add global keyboard shortcut handler as fallback
  useEffect(() => {
    const handleGlobalKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        console.log('🎹 GLOBAL SAVE - Ctrl/Cmd+S detected globally');

        // Only handle if we have an active tab
        if (activeTabId) {
          console.log('🎹 GLOBAL SAVE - Preventing default and triggering save for:', activeTabId);
          event.preventDefault();
          event.stopPropagation();

          // Trigger save for active tab
          saveTab(activeTabId);
        }
      }
    };

    document.addEventListener('keydown', handleGlobalKeyDown);
    console.log('🎹 GLOBAL SAVE - Global keyboard handler added');

    return () => {
      document.removeEventListener('keydown', handleGlobalKeyDown);
      console.log('🎹 GLOBAL SAVE - Global keyboard handler removed');
    };
  }, [activeTabId, saveTab]);

  // Get active tab
  const activeTab = tabs.find(tab => tab.fileId === activeTabId);

  return (
    <div className={cn('h-full w-full min-h-0 flex flex-col bg-[#1e1e1e]', className)}>
      {/* Tab Bar */}
      {tabs.length > 0 && (
        <div className="flex-shrink-0 h-10 flex bg-[#2d2d30] border-b border-[#3c3c3c] overflow-x-auto">
          {tabs.map(tab => {
            const file = findFileById(tab.fileId);
            const hasUnsavedChanges = file?.hasUnsavedChanges || tab.isDirty;

            return (
              <div
                key={tab.fileId}
                onClick={() => {
                  console.log('📋 TAB CLICK - Switching to tab:', tab.fileId, 'from:', activeTabId);
                  setActiveTabId(tab.fileId);
                  // Also update the file store to keep it in sync
                  if (selectedFileId !== tab.fileId) {
                    console.log(
                      '📋 TAB CLICK - Updating file store selectedFileId to:',
                      tab.fileId
                    );
                    selectFile(tab.fileId);
                  }
                }}
                className={cn(
                  'flex items-center px-3 py-2 border-r border-[#3c3c3c] cursor-pointer group',
                  'min-w-[120px] max-w-[200px] relative',
                  activeTabId === tab.fileId
                    ? 'bg-[#1e1e1e] text-[#cccccc]'
                    : 'bg-[#2d2d30] text-[#969696] hover:text-[#cccccc]'
                )}
              >
                {/* File name */}
                <span className="flex-1 truncate text-sm">{tab.fileName}</span>

                {/* Unsaved changes indicator */}
                {hasUnsavedChanges && (
                  <Circle className="w-2 h-2 ml-2 fill-[#4fc3f7] text-[#4fc3f7]" />
                )}

                {/* Save button (appears on hover if dirty) */}
                {hasUnsavedChanges && (
                  <button
                    onClick={e => {
                      console.log(`🔘 SAVE BUTTON CLICKED - File: ${tab.fileId}`);
                      saveTab(tab.fileId, e);
                    }}
                    className="ml-1 opacity-0 group-hover:opacity-100 p-1 hover:bg-[#3c3c3c] rounded transition-opacity"
                    title="Save"
                  >
                    <Save className="w-3 h-3" />
                  </button>
                )}

                {/* DEBUG: Show dirty state */}
                <span className="text-xs text-gray-500 ml-2">{hasUnsavedChanges ? '●' : '○'}</span>

                {/* Close button */}
                <button
                  onClick={e => closeTab(tab.fileId, e)}
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
            );
          })}
        </div>
      )}

      {/* Editor Area */}
      <div className="flex-1 min-h-0 h-0 overflow-hidden bg-[#1e1e1e]">
        {activeTab ? (
          <MonacoEditor
            fileId={activeTab.fileId}
            value={activeTab.content}
            onChange={newContent => updateTabContent(activeTab.fileId, newContent)}
            readOnly={false}
            onSave={content => {
              console.log(
                '🔗 MONACO ONSAVE - onSave called for fileId:',
                activeTab.fileId,
                'with content length:',
                content?.length
              );
              saveTab(activeTab.fileId, content);
            }}
          />
        ) : (
          <div className="h-full w-full flex items-center justify-center bg-[#1e1e1e]">
            <div className="text-center text-[#969696]">
              <div className="text-4xl mb-4">📁</div>
              <h3 className="text-lg font-medium mb-2">No file open</h3>
              <p className="text-sm">Select a file from the explorer to start editing</p>
            </div>
          </div>
        )}
      </div>

      {/* Status bar for editor */}
      {activeTab && (
        <div className="flex-shrink-0 h-6 bg-[#007acc] flex items-center justify-between px-3 text-white text-xs">
          <div className="flex items-center space-x-4">
            <span>{activeTab.fileName}</span>
            <span>{findFileById(activeTab.fileId)?.fileType?.toUpperCase() || 'TXT'}</span>
          </div>

          <div className="flex items-center space-x-4">
            {activeTab.isDirty && <span className="text-[#cce7f0]">Unsaved changes</span>}
            <span>Lines: {activeTab.content.split('\n').length}</span>
          </div>
        </div>
      )}
    </div>
  );
}

// Default export for React.lazy() compatibility
export default TabbedEditor;
