'use client';

import { useSearch } from '@/hooks/useSearch';
import type { SearchOptions, SearchResult } from '@/lib/types/search.types';
import { cn } from '@/lib/utils/cn';
import { AlertCircle, ChevronDown, ChevronRight, FileText, Search, X } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';

function SearchPanel() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<SearchOptions>({
    matchCase: false,
    wholeWord: false,
    useRegex: false,
    includeComments: true,
    includeBinary: false,
    maxResults: 500,
    contextLines: 0,
  });
  const [expandedFiles, setExpandedFiles] = useState<Set<string>>(new Set());

  // Use the search hook
  const { search, results, isSearching, error, totalCount, searchTime, clearResults } = useSearch({
    debounceMs: 300,
    cacheResults: true,
    onError: err => console.error('Search error:', err),
  });

  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) {
      clearResults();
      return;
    }

    await search(searchQuery, filters);
  }, [searchQuery, filters, search, clearResults]);

  // Auto-expand first file when results change
  useEffect(() => {
    if (results.length > 0) {
      const firstFile = results[0].file;
      setExpandedFiles(new Set([firstFile]));
    }
  }, [results]);

  // Trigger search on Enter key
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter') {
        handleSearch();
      }
    },
    [handleSearch]
  );

  // Clear search and results
  const handleClearSearch = useCallback(() => {
    setSearchQuery('');
    clearResults();
    setExpandedFiles(new Set());
  }, [clearResults]);

  const toggleFileExpansion = (fileName: string) => {
    const newExpanded = new Set(expandedFiles);
    if (newExpanded.has(fileName)) {
      newExpanded.delete(fileName);
    } else {
      newExpanded.add(fileName);
    }
    setExpandedFiles(newExpanded);
  };

  // Group results by file
  const groupedResults = results.reduce(
    (acc, result) => {
      if (!acc[result.file]) {
        acc[result.file] = [];
      }
      acc[result.file].push(result);
      return acc;
    },
    {} as Record<string, SearchResult[]>
  );

  const getTypeIcon = (type: SearchResult['type']) => {
    switch (type) {
      case 'function':
        return '𝑓';
      case 'variable':
        return 'V';
      case 'tag':
        return 'T';
      default:
        return '"';
    }
  };

  const getTypeColor = (type: SearchResult['type']) => {
    switch (type) {
      case 'function':
        return 'text-[#dcdcaa]';
      case 'variable':
        return 'text-[#9cdcfe]';
      case 'tag':
        return 'text-[#4fc1ff]';
      default:
        return 'text-[#ce9178]';
    }
  };

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
            onChange={e => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full pl-8 pr-8 py-2 text-sm bg-[#3c3c3c] text-[#cccccc] placeholder-[#969696] rounded border border-[#3c3c3c] focus:border-[#007acc] focus:outline-none"
          />
          {searchQuery && (
            <button
              onClick={handleClearSearch}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#969696] hover:text-[#cccccc]"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Search Filters */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <button
            className={cn(
              'flex items-center space-x-1 px-2 py-1 rounded transition-colors',
              filters.matchCase
                ? 'bg-[#007acc] text-white'
                : 'bg-[#3c3c3c] text-[#cccccc] hover:bg-[#505050]'
            )}
            onClick={() => setFilters(prev => ({ ...prev, matchCase: !prev.matchCase }))}
          >
            <span>Aa</span>
            <span>Match Case</span>
          </button>

          <button
            className={cn(
              'flex items-center space-x-1 px-2 py-1 rounded transition-colors',
              filters.wholeWord
                ? 'bg-[#007acc] text-white'
                : 'bg-[#3c3c3c] text-[#cccccc] hover:bg-[#505050]'
            )}
            onClick={() => setFilters(prev => ({ ...prev, wholeWord: !prev.wholeWord }))}
          >
            <span>ab</span>
            <span>Whole Word</span>
          </button>

          <button
            className={cn(
              'flex items-center space-x-1 px-2 py-1 rounded transition-colors',
              filters.useRegex
                ? 'bg-[#007acc] text-white'
                : 'bg-[#3c3c3c] text-[#cccccc] hover:bg-[#505050]'
            )}
            onClick={() => setFilters(prev => ({ ...prev, useRegex: !prev.useRegex }))}
          >
            <span>.*</span>
            <span>Regex</span>
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

      {/* Error Display */}
      {error && (
        <div className="p-3 bg-[#5a1d1d] border border-[#f14c4c] rounded m-2">
          <div className="flex items-center space-x-2 text-[#f14c4c]">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">{error.message}</span>
          </div>
        </div>
      )}

      {/* Results */}
      <div className="flex-1 overflow-auto">
        {results.length === 0 && searchQuery && !isSearching && !error ? (
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
                  onKeyDown={e => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      toggleFileExpansion(fileName);
                    }
                  }}
                  className="flex items-center w-full p-2 hover:bg-[#2a2d2e] rounded transition-colors"
                  aria-expanded={expandedFiles.has(fileName)}
                  aria-label={`${expandedFiles.has(fileName) ? 'Collapse' : 'Expand'} ${fileName}`}
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
                    {fileResults.map(result => (
                      <div
                        key={result.id}
                        className="p-2 hover:bg-[#2a2d2e] rounded cursor-pointer transition-colors"
                        onClick={() => console.log('Navigate to:', result.file, result.line)}
                      >
                        <div className="flex items-center space-x-2 text-xs mb-1">
                          <span className={cn('font-mono', getTypeColor(result.type))}>
                            {getTypeIcon(result.type)}
                          </span>
                          <span className="text-[#969696]">Line {result.line}</span>
                        </div>
                        <div className="text-sm text-[#cccccc] font-mono">
                          {result.content
                            .split(new RegExp(`(${result.match})`, 'gi'))
                            .map((part, partIndex) =>
                              part.toLowerCase() === result.match.toLowerCase() ? (
                                <mark
                                  key={`${result.id}-match-${partIndex}`}
                                  className="bg-[#664c00] text-[#ffffff] px-1 rounded"
                                >
                                  {part}
                                </mark>
                              ) : (
                                <span key={`${result.id}-text-${partIndex}`}>{part}</span>
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
        <div className="p-2 border-t border-[#3c3c3c] text-xs text-[#969696] flex justify-between">
          <span>
            {totalCount > results.length
              ? `Showing ${results.length} of ${totalCount}`
              : totalCount}{' '}
            result{totalCount !== 1 ? 's' : ''} in {Object.keys(groupedResults).length} file
            {Object.keys(groupedResults).length !== 1 ? 's' : ''}
          </span>
          {searchTime > 0 && <span>{searchTime}ms</span>}
        </div>
      )}
    </div>
  );
}

export default SearchPanel;

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
