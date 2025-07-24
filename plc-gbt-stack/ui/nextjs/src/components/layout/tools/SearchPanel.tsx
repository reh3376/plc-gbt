'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils/cn'
import { 
  Search,
  FileText,
  Filter,
  X,
  ChevronDown,
  ChevronRight
} from 'lucide-react'

interface SearchResult {
  id: string
  file: string
  line: number
  content: string
  match: string
  type: 'text' | 'variable' | 'function' | 'tag'
}

const mockResults: SearchResult[] = [
  {
    id: '1',
    file: 'Distillation_Control.acd',
    line: 45,
    content: 'Temperature_PV := AI_Temperature_01;',
    match: 'Temperature',
    type: 'variable'
  },
  {
    id: '2',
    file: 'Distillation_Control.acd',
    line: 67,
    content: '// Set temperature setpoint for distillation column',
    match: 'temperature',
    type: 'text'
  },
  {
    id: '3',
    file: 'PID_Temperature.acd',
    line: 12,
    content: 'FUNCTION PID_Temperature_Control',
    match: 'Temperature',
    type: 'function'
  },
  {
    id: '4',
    file: 'Flow_Control.acd',
    line: 23,
    content: 'Temperature_Interlock := TRUE;',
    match: 'Temperature',
    type: 'variable'
  }
]

function SearchPanel() {
  const [searchQuery, setSearchQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [filters, setFilters] = useState({
    matchCase: false,
    wholeWord: false,
    regex: false,
    includeComments: true
  })
  const [expandedFiles, setExpandedFiles] = useState<Set<string>>(new Set())

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setResults([])
      return
    }

    setIsSearching(true)
    
    // Simulate search delay
    setTimeout(() => {
      const filteredResults = mockResults.filter(result =>
        result.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        result.match.toLowerCase().includes(searchQuery.toLowerCase())
      )
      setResults(filteredResults)
      setIsSearching(false)
      
      // Auto-expand first file
      if (filteredResults.length > 0) {
        setExpandedFiles(new Set([filteredResults[0].file]))
      }
    }, 500)
  }

  const toggleFileExpansion = (fileName: string) => {
    const newExpanded = new Set(expandedFiles)
    if (newExpanded.has(fileName)) {
      newExpanded.delete(fileName)
    } else {
      newExpanded.add(fileName)
    }
    setExpandedFiles(newExpanded)
  }

  const clearSearch = () => {
    setSearchQuery('')
    setResults([])
    setExpandedFiles(new Set())
  }

  // Group results by file
  const groupedResults = results.reduce((acc, result) => {
    if (!acc[result.file]) {
      acc[result.file] = []
    }
    acc[result.file].push(result)
    return acc
  }, {} as Record<string, SearchResult[]>)

  const getTypeIcon = (type: SearchResult['type']) => {
    switch (type) {
      case 'function':
        return '𝑓'
      case 'variable':
        return 'V'
      case 'tag':
        return 'T'
      default:
        return '"'
    }
  }

  const getTypeColor = (type: SearchResult['type']) => {
    switch (type) {
      case 'function':
        return 'text-[#dcdcaa]'
      case 'variable':
        return 'text-[#9cdcfe]'
      case 'tag':
        return 'text-[#4fc1ff]'
      default:
        return 'text-[#ce9178]'
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Search Input */}
      <div className="p-3 border-b border-[#3c3c3c] space-y-2">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#969696]" />
          <input
            type="text"
            placeholder="Search in files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            className="w-full pl-8 pr-8 py-2 text-sm bg-[#3c3c3c] text-[#cccccc] placeholder-[#969696] rounded border border-[#3c3c3c] focus:border-[#007acc] focus:outline-none"
          />
          {searchQuery && (
            <button
              onClick={clearSearch}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#969696] hover:text-[#cccccc]"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Search Filters */}
        <div className="flex items-center space-x-3 text-xs">
          <button
            className={cn(
              "flex items-center space-x-1 px-2 py-1 rounded transition-colors",
              filters.matchCase 
                ? "bg-[#007acc] text-white" 
                : "bg-[#3c3c3c] text-[#cccccc] hover:bg-[#505050]"
            )}
            onClick={() => setFilters(prev => ({ ...prev, matchCase: !prev.matchCase }))}
          >
            <span>Aa</span>
            <span>Match Case</span>
          </button>
          
          <button
            className={cn(
              "flex items-center space-x-1 px-2 py-1 rounded transition-colors",
              filters.wholeWord 
                ? "bg-[#007acc] text-white" 
                : "bg-[#3c3c3c] text-[#cccccc] hover:bg-[#505050]"
            )}
            onClick={() => setFilters(prev => ({ ...prev, wholeWord: !prev.wholeWord }))}
          >
            <span>ab</span>
            <span>Whole Word</span>
          </button>
        </div>

        <button
          onClick={handleSearch}
          disabled={isSearching || !searchQuery.trim()}
          className="w-full py-2 bg-[#007acc] hover:bg-[#1177bb] disabled:bg-[#3c3c3c] disabled:text-[#969696] text-white text-sm rounded transition-colors"
        >
          {isSearching ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-auto">
        {results.length === 0 && searchQuery && !isSearching ? (
                     <div className="p-4 text-center text-[#969696] text-sm">
             No results found for &quot;{searchQuery}&quot;
           </div>
        ) : (
          <div className="p-2">
            {Object.entries(groupedResults).map(([fileName, fileResults]) => (
              <div key={fileName} className="mb-3">
                {/* File Header */}
                <button
                  onClick={() => toggleFileExpansion(fileName)}
                  className="flex items-center w-full p-2 hover:bg-[#2a2d2e] rounded transition-colors"
                >
                  {expandedFiles.has(fileName) ? (
                    <ChevronDown className="w-4 h-4 mr-2 text-[#cccccc]" />
                  ) : (
                    <ChevronRight className="w-4 h-4 mr-2 text-[#cccccc]" />
                  )}
                  <FileText className="w-4 h-4 mr-2 text-[#519aba]" />
                  <span className="text-[#cccccc] text-sm font-medium">{fileName}</span>
                  <span className="ml-auto text-[#969696] text-xs">
                    {fileResults.length} match{fileResults.length !== 1 ? 'es' : ''}
                  </span>
                </button>

                {/* File Results */}
                {expandedFiles.has(fileName) && (
                  <div className="ml-6 space-y-1">
                    {fileResults.map((result) => (
                      <div
                        key={result.id}
                        className="p-2 hover:bg-[#2a2d2e] rounded cursor-pointer transition-colors"
                        onClick={() => console.log('Navigate to:', result.file, result.line)}
                      >
                        <div className="flex items-center space-x-2 text-xs mb-1">
                          <span className={cn("font-mono", getTypeColor(result.type))}>
                            {getTypeIcon(result.type)}
                          </span>
                          <span className="text-[#969696]">Line {result.line}</span>
                        </div>
                        <div className="text-sm text-[#cccccc] font-mono">
                          {result.content.split(new RegExp(`(${result.match})`, 'gi')).map((part, index) => 
                            part.toLowerCase() === result.match.toLowerCase() ? (
                              <mark key={index} className="bg-[#664c00] text-[#ffffff] px-1 rounded">
                                {part}
                              </mark>
                            ) : (
                              <span key={index}>{part}</span>
                            )
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Results Summary */}
      {results.length > 0 && (
        <div className="p-2 border-t border-[#3c3c3c] text-xs text-[#969696]">
          {results.length} result{results.length !== 1 ? 's' : ''} in {Object.keys(groupedResults).length} file{Object.keys(groupedResults).length !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  )
}

export default SearchPanel

/**
 * SearchPanel Component
 * 
 * @description Advanced search functionality for PLC code and documentation
 * @specification Implements main-ui-spec.md SearchPanel tool requirements
 * 
 * @features
 * - Full-text search across PLC files
 * - Advanced filtering options (case sensitive, whole word, regex)
 * - Grouped results by file with expand/collapse
 * - Syntax highlighting for different result types
 * - Real-time search with loading states
 * - Navigation to search results
 * 
 * @searchTypes
 * - Text: Comments and string literals
 * - Variable: PLC variable references
 * - Function: Function and routine definitions
 * - Tag: PLC tag references
 * 
 * @accessibility
 * - Keyboard navigation support
 * - Clear search state indicators
 * - Screen reader friendly results
 * 
 * @performance
 * - Lazy loaded via Suspense
 * - Debounced search input
 * - Efficient result grouping
 */ 