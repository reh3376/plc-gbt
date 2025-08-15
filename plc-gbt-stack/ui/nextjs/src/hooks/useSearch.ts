/**
 * useSearch Hook - AI Task Orchestrator TypeScript Implementation
 *
 * @description React hook for search API integration
 * @compliance Strict TypeScript - zero `any` types policy
 * @features Debouncing, caching, and error handling
 */

import type {
  SearchOptions,
  SearchRequest,
  SearchResponse,
  SearchResult,
  SearchScope,
} from '@/lib/types/search.types';
import { useCallback, useRef, useState } from 'react';

interface UseSearchOptions {
  debounceMs?: number;
  cacheResults?: boolean;
  onError?: (error: Error) => void;
}

interface UseSearchReturn {
  search: (query: string, options?: Partial<SearchOptions>, scope?: SearchScope) => Promise<void>;
  results: SearchResult[];
  isSearching: boolean;
  error: Error | null;
  totalCount: number;
  searchTime: number;
  clearResults: () => void;
  cancelSearch: () => void;
}

export function useSearch(options: UseSearchOptions = {}): UseSearchReturn {
  const { debounceMs = 300, cacheResults = true, onError } = options;

  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [searchTime, setSearchTime] = useState(0);

  const abortControllerRef = useRef<AbortController | null>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const cacheRef = useRef<Map<string, SearchResponse>>(new Map());

  const performSearch = useCallback(
    async (query: string, searchOptions?: Partial<SearchOptions>, scope?: SearchScope) => {
      // Cancel any pending search
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Clear previous error
      setError(null);

      // Handle empty query
      if (!query.trim()) {
        setResults([]);
        setTotalCount(0);
        setSearchTime(0);
        return;
      }

      // Check cache
      const cacheKey = JSON.stringify({ query, searchOptions, scope });
      if (cacheResults && cacheRef.current.has(cacheKey)) {
        const cached = cacheRef.current.get(cacheKey)!;
        setResults(cached.results);
        setTotalCount(cached.totalCount);
        setSearchTime(cached.searchTime);
        return;
      }

      // Create new abort controller
      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      setIsSearching(true);

      try {
        const searchRequest: SearchRequest = {
          query,
          options: {
            matchCase: false,
            wholeWord: false,
            useRegex: false,
            includeComments: true,
            includeBinary: false,
            maxResults: 500,
            contextLines: 0,
            ...searchOptions,
          },
          scope,
        };

        const response = await fetch('/api/v1/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(searchRequest),
          signal: abortController.signal,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error?.message || `Search failed: ${response.statusText}`);
        }

        const searchResponse: SearchResponse = await response.json();

        // Update state
        setResults(searchResponse.results);
        setTotalCount(searchResponse.totalCount);
        setSearchTime(searchResponse.searchTime);

        // Cache results
        if (cacheResults) {
          cacheRef.current.set(cacheKey, searchResponse);

          // Limit cache size
          if (cacheRef.current.size > 50) {
            const firstKey = cacheRef.current.keys().next().value;
            if (firstKey) {
              cacheRef.current.delete(firstKey);
            }
          }
        }
      } catch (err) {
        // Ignore abort errors
        if (err instanceof Error && err.name === 'AbortError') {
          return;
        }

        const error = err instanceof Error ? err : new Error('Search failed');
        setError(error);

        if (onError) {
          onError(error);
        }
      } finally {
        setIsSearching(false);
        abortControllerRef.current = null;
      }
    },
    [cacheResults, onError]
  );

  const search = useCallback(
    (query: string, options?: Partial<SearchOptions>, scope?: SearchScope): Promise<void> => {
      return new Promise(resolve => {
        // Clear existing debounce timer
        if (debounceTimerRef.current) {
          clearTimeout(debounceTimerRef.current);
        }

        // Set new debounce timer
        debounceTimerRef.current = setTimeout(async () => {
          await performSearch(query, options, scope);
          resolve();
        }, debounceMs);
      });
    },
    [performSearch, debounceMs]
  );

  const clearResults = useCallback(() => {
    setResults([]);
    setTotalCount(0);
    setSearchTime(0);
    setError(null);
  }, []);

  const cancelSearch = useCallback(() => {
    // Cancel debounce timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
      debounceTimerRef.current = null;
    }

    // Cancel ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    setIsSearching(false);
  }, []);

  return {
    search,
    results,
    isSearching,
    error,
    totalCount,
    searchTime,
    clearResults,
    cancelSearch,
  };
}
