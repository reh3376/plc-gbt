'use client'

import { useState } from 'react'
import { 
  Folder, 
  FolderOpen, 
  FileText, 
  ChevronRight, 
  ChevronDown,
  Plus,
  RefreshCw
} from 'lucide-react'
import { cn } from '@/lib/utils/cn'

interface FileItem {
  id: string
  name: string
  type: 'file' | 'folder'
  children?: FileItem[]
  isExpanded?: boolean
}

// Mock file structure
const mockFiles: FileItem[] = [
  {
    id: '1',
    name: 'PLC Projects',
    type: 'folder',
    isExpanded: true,
    children: [
      {
        id: '2',
        name: 'Distillation_Control.acd',
        type: 'file',
      },
      {
        id: '3',
        name: 'Boiler_Safety.l5x',
        type: 'file',
      },
      {
        id: '4',
        name: 'Control_Loops',
        type: 'folder',
        children: [
          {
            id: '5',
            name: 'Temperature_PID.json',
            type: 'file',
          },
          {
            id: '6',
            name: 'Pressure_Control.json',
            type: 'file',
          },
        ],
      },
    ],
  },
  {
    id: '7',
    name: 'Workflows',
    type: 'folder',
    children: [
      {
        id: '8',
        name: 'Startup_Sequence.workflow',
        type: 'file',
      },
      {
        id: '9',
        name: 'Emergency_Shutdown.workflow',
        type: 'file',
      },
    ],
  },
]

export function FileExplorer() {
  const [files, setFiles] = useState<FileItem[]>(mockFiles)

  const toggleFolder = (id: string) => {
    const updateFiles = (items: FileItem[]): FileItem[] => {
      return items.map(item => {
        if (item.id === id && item.type === 'folder') {
          return { ...item, isExpanded: !item.isExpanded }
        }
        if (item.children) {
          return { ...item, children: updateFiles(item.children) }
        }
        return item
      })
    }
    
    setFiles(updateFiles(files))
  }

  const renderFileItem = (item: FileItem, depth = 0) => {
    const isFolder = item.type === 'folder'
    const Icon = isFolder 
      ? (item.isExpanded ? FolderOpen : Folder)
      : FileText

    return (
      <div key={item.id}>
        <div
          className={cn(
            "flex items-center py-1 px-2 hover:bg-[#2a2d2e] cursor-pointer text-sm",
            "select-none"
          )}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
          onClick={() => isFolder ? toggleFolder(item.id) : undefined}
        >
          {isFolder && (
            <div className="w-4 h-4 flex items-center justify-center mr-1">
              {item.isExpanded ? (
                <ChevronDown className="w-3 h-3 text-[#cccccc]" />
              ) : (
                <ChevronRight className="w-3 h-3 text-[#cccccc]" />
              )}
            </div>
          )}
          
          <Icon className={cn(
            "w-4 h-4 mr-2 flex-shrink-0",
            isFolder ? "text-[#dcb67a]" : "text-[#519aba]"
          )} />
          
          <span className="text-[#cccccc] truncate">{item.name}</span>
        </div>

        {isFolder && item.isExpanded && item.children && (
          <div>
            {item.children.map(child => renderFileItem(child, depth + 1))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header with actions */}
      <div className="flex items-center justify-between p-2 border-b border-[#3c3c3c]">
        <span className="text-[#cccccc] text-sm font-medium">Files</span>
        <div className="flex space-x-1">
          <button
            className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] rounded transition-colors"
            title="New File"
          >
            <Plus className="w-4 h-4 text-[#cccccc]" />
          </button>
          <button
            className="w-6 h-6 flex items-center justify-center hover:bg-[#3c3c3c] rounded transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4 text-[#cccccc]" />
          </button>
        </div>
      </div>

      {/* File tree */}
      <div className="flex-1 overflow-auto">
        {files.map(item => renderFileItem(item))}
      </div>
    </div>
  )
} 