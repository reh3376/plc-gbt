/**
 * Documentation Layout - AI Task Orchestrator TypeScript Implementation
 *
 * @description Layout component for node documentation pages
 * @compliance Strict TypeScript - zero `any` types policy
 * @features Navigation sidebar, search functionality, responsive design
 */

'use client';

import { ArrowLeft, BookOpen, Filter, Search, X } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import React, { useCallback, useState } from 'react';

import { getNavigationItems } from '@/lib/docs/client-navigation';
import {
  getAvailableCategories,
  getSearchSuggestions,
  searchDocumentation,
  type SearchResult,
} from '@/lib/docs/client-search';
import { cn } from '@/lib/utils/cn';

interface DocLayoutProps {
  readonly children: React.ReactNode;
}

interface DocNavItem {
  readonly title: string;
  readonly href: string;
  readonly category: string;
}

// Generate navigation items from client-safe static data
const DOC_NAVIGATION: ReadonlyArray<DocNavItem> = getNavigationItems();

// Group navigation by category
const GROUPED_NAVIGATION = DOC_NAVIGATION.reduce((acc, item) => {
  if (!acc[item.category]) {
    acc[item.category] = [];
  }
  acc[item.category].push(item);
  return acc;
}, {} as Record<string, DocNavItem[]>);

export default function DocsLayout({ children }: Readonly<DocLayoutProps>): React.JSX.Element {
  const pathname = usePathname();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<ReadonlyArray<SearchResult>>([]);
  const [suggestions, setSuggestions] = useState<ReadonlyArray<string>>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState<ReadonlyArray<string>>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [sidebarOpen] = useState(true);

  const availableCategories = getAvailableCategories();

  // Handle search with debouncing
  const performSearch = useCallback((query: string, categories: ReadonlyArray<string>) => {
    if (query.trim()) {
      const results = searchDocumentation({
        query,
        categories: categories.length > 0 ? categories : undefined,
        maxResults: 15,
      });
      setSearchResults(results);
    } else {
      setSearchResults([]);
    }
  }, []);

  // Handle search input changes
  const handleSearchChange = useCallback(
    (value: string) => {
      setSearchQuery(value);

      if (value.length >= 2) {
        const searchSuggestions = getSearchSuggestions(value, 5);
        setSuggestions(searchSuggestions);
        setShowSuggestions(true);
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }

      performSearch(value, selectedCategories);
    },
    [performSearch, selectedCategories]
  );

  // Handle category filter changes
  const handleCategoryToggle = useCallback(
    (category: string) => {
      const newCategories = selectedCategories.includes(category)
        ? selectedCategories.filter(c => c !== category)
        : [...selectedCategories, category];

      setSelectedCategories(newCategories);
      performSearch(searchQuery, newCategories);
    },
    [selectedCategories, searchQuery, performSearch]
  );

  // Clear search
  const clearSearch = useCallback(() => {
    setSearchQuery('');
    setSearchResults([]);
    setSuggestions([]);
    setShowSuggestions(false);
  }, []);

  // Filter navigation based on search results or show all
  const filteredNavigation =
    searchResults.length > 0
      ? searchResults.map(result => ({
          title: result.item.title,
          href: result.item.href,
          category: result.item.category,
          score: result.score,
          highlights: result.highlights,
        }))
      : null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="px-2.5">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              {/* Logo and Title - matching main UI - positioned at far left */}
              <div className="flex items-center space-x-2">
                <div className="relative w-7 h-5">
                  {/* Background element for logo visibility */}
                  <div className="absolute inset-0 bg-gray-100 dark:bg-gray-700 rounded-sm border border-gray-200 dark:border-gray-600" />
                  {/* Logo with higher z-index */}
                  <img
                    src="/whk-logo.png"
                    alt="PLC-GBT Logo"
                    className="relative w-7 h-5 object-contain z-10"
                  />
                </div>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  PLC-GBT Industrial Automation IDE
                </span>
              </div>
              <div className="h-6 border-l border-gray-300 dark:border-gray-600" />
              <button
                onClick={() => {
                  // Close current tab and go back to the originating tab
                  if (typeof window !== 'undefined') {
                    window.close();
                    // If window.close() doesn't work (same tab), navigate back
                    if (!window.closed) {
                      window.location.href = '/workflow';
                    }
                  }
                }}
                className="flex items-center space-x-2 text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <span className="text-sm font-medium">Back to Workflow</span>
              </button>
              <div className="h-6 border-l border-gray-300 dark:border-gray-600" />
              <div className="flex items-center space-x-2">
                <BookOpen className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Node Documentation
                </h1>
              </div>
            </div>

            {/* Enhanced Search */}
            <div className="relative w-80">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search documentation..."
                value={searchQuery}
                onChange={e => handleSearchChange(e.target.value)}
                onFocus={() => setShowSuggestions(suggestions.length > 0)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                className={cn(
                  'w-full pl-10 pr-12 py-2 border border-gray-300 dark:border-gray-600',
                  'rounded-lg bg-white dark:bg-gray-700',
                  'text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400',
                  'focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                  'transition-all duration-200'
                )}
              />

              {/* Clear Search Button */}
              {searchQuery && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="absolute right-8 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              )}

              {/* Filter Toggle */}
              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className={cn(
                  'absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4',
                  'text-gray-400 hover:text-gray-600 transition-colors',
                  selectedCategories.length > 0 && 'text-blue-500'
                )}
              >
                <Filter className="w-4 h-4" />
              </button>

              {/* Search Suggestions */}
              {showSuggestions && suggestions.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg z-50">
                  {suggestions.map(suggestion => (
                    <button
                      key={suggestion}
                      type="button"
                      onClick={() => {
                        handleSearchChange(suggestion);
                        setShowSuggestions(false);
                      }}
                      className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 first:rounded-t-lg last:rounded-b-lg"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              )}

              {/* Category Filters */}
              {showFilters && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg z-50 p-4">
                  <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
                    Filter by Category
                  </h4>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {availableCategories.map(category => (
                      <label key={category} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={selectedCategories.includes(category)}
                          onChange={() => handleCategoryToggle(category)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300">{category}</span>
                      </label>
                    ))}
                  </div>
                  {selectedCategories.length > 0 && (
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedCategories([]);
                        performSearch(searchQuery, []);
                      }}
                      className="mt-2 text-xs text-blue-600 hover:text-blue-800"
                    >
                      Clear filters
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="px-2.5 py-2.5">
        <div className="flex gap-2.5">
          {/* Sidebar */}
          <aside className={cn('w-80 flex-shrink-0', !sidebarOpen && 'hidden')}>
            <div className="sticky top-2.5">
              <nav className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 max-h-[calc(100vh-80px)] overflow-y-auto">
                {filteredNavigation ? (
                  // Enhanced search results
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        Search Results ({filteredNavigation.length})
                      </h3>
                      {selectedCategories.length > 0 && (
                        <span className="text-xs text-blue-600 dark:text-blue-400">Filtered</span>
                      )}
                    </div>
                    <div className="space-y-2">
                      {filteredNavigation.map(item => (
                        <Link
                          key={item.href}
                          href={item.href}
                          className={cn(
                            'block px-3 py-3 rounded-md text-sm transition-colors border',
                            pathname === item.href
                              ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800'
                              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 border-transparent hover:border-gray-200 dark:hover:border-gray-600'
                          )}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <div className="font-medium">{item.title}</div>
                            {'score' in item && (
                              <div className="text-xs text-gray-400">{Math.round(item.score)}%</div>
                            )}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                            {item.category}
                          </div>
                          {'highlights' in item &&
                            item.highlights &&
                            item.highlights.length > 0 && (
                              <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                                {item.highlights.slice(0, 2).map(highlight => (
                                  <div key={highlight} className="truncate">
                                    {highlight}
                                  </div>
                                ))}
                              </div>
                            )}
                        </Link>
                      ))}
                    </div>

                    {/* Search tips */}
                    {filteredNavigation.length === 0 && searchQuery && (
                      <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                        <p className="text-sm text-yellow-800 dark:text-yellow-200">
                          No results found for &quot;{searchQuery}&quot;
                        </p>
                        <p className="text-xs text-yellow-600 dark:text-yellow-300 mt-1">
                          Try different keywords or check the category filters
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  // Grouped navigation
                  <div className="space-y-6">
                    {Object.entries(GROUPED_NAVIGATION).map(([category, items]) => (
                      <div key={category}>
                        <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
                          {category}
                        </h3>
                        <div className="space-y-1">
                          {items.map(item => (
                            <Link
                              key={item.href}
                              href={item.href}
                              className={cn(
                                'block px-3 py-2 rounded-md text-sm transition-colors',
                                pathname === item.href
                                  ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                              )}
                            >
                              {item.title}
                            </Link>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </nav>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 min-w-0">
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-auto max-h-[calc(100vh-80px)]">
              <div className="p-6">{children}</div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
