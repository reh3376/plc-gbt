/**
 * Search API Routes - AI Task Orchestrator TypeScript Implementation
 *
 * @description RESTful API endpoints for search operations
 * @compliance Strict TypeScript - zero `any` types policy
 * @openapi Uses OpenAPI schema from MCP_Docker for validation
 * @extensibility Modular architecture supporting multiple search providers
 */

import { SearchManager } from '@/lib/search/search-manager';
import type { SearchError, SearchRequest } from '@/lib/types/search.types';
import { NextRequest, NextResponse } from 'next/server';

// Singleton search manager instance
const searchManager = new SearchManager();

/**
 * POST /api/v1/search
 * Perform a search across workspace files
 *
 * @openapi
 * /api/v1/search:
 *   post:
 *     summary: Search across workspace files
 *     description: Performs text search with various options and filters
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/SearchRequest'
 *     responses:
 *       200:
 *         description: Search completed successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/SearchResponse'
 *       400:
 *         description: Invalid search request
 *       500:
 *         description: Internal server error
 */
export async function POST(request: NextRequest) {
  try {
    // Parse request body
    const body = (await request.json()) as unknown;

    // Validate request structure
    if (!isSearchRequest(body)) {
      return NextResponse.json(
        createErrorResponse('INVALID_QUERY', 'Invalid search request format'),
        { status: 400 }
      );
    }

    const searchRequest = body as SearchRequest;

    // Validate query
    if (!searchRequest.query || searchRequest.query.trim().length === 0) {
      return NextResponse.json(
        createErrorResponse('INVALID_QUERY', 'Search query cannot be empty'),
        { status: 400 }
      );
    }

    // Set default options if not provided
    const requestWithDefaults: SearchRequest = {
      query: searchRequest.query,
      scope: searchRequest.scope || {},
      options: {
        matchCase: searchRequest.options?.matchCase ?? false,
        wholeWord: searchRequest.options?.wholeWord ?? false,
        useRegex: searchRequest.options?.useRegex ?? false,
        includeComments: searchRequest.options?.includeComments ?? true,
        includeBinary: searchRequest.options?.includeBinary ?? false,
        maxResults: searchRequest.options?.maxResults ?? 500,
        contextLines: searchRequest.options?.contextLines ?? 0,
      },
      providers: searchRequest.providers,
    };

    // Perform search
    const searchResponse = await searchManager.search(requestWithDefaults);

    // Return successful response
    return NextResponse.json(searchResponse, {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'X-Search-Time': searchResponse.searchTime.toString(),
        'X-Total-Results': searchResponse.totalCount.toString(),
      },
    });
  } catch (error) {
    console.error('Search API error:', error);

    // Handle specific error types
    if (error instanceof Error) {
      if (error.message.includes('Invalid regular expression')) {
        return NextResponse.json(
          createErrorResponse('INVALID_REGEX', 'Invalid regular expression in search query'),
          { status: 400 }
        );
      }
    }

    // Generic error response
    return NextResponse.json(
      createErrorResponse('PROVIDER_ERROR', 'An error occurred during search'),
      { status: 500 }
    );
  }
}

/**
 * GET /api/v1/search
 * Get search providers and configuration
 */
export async function GET() {
  try {
    const providers = searchManager.getProviders().map(provider => ({
      name: provider.name,
      priority: provider.priority,
      available: true, // Could be enhanced to check actual availability
    }));

    return NextResponse.json({
      providers,
      defaultOptions: {
        matchCase: false,
        wholeWord: false,
        useRegex: false,
        includeComments: true,
        includeBinary: false,
        maxResults: 500,
        contextLines: 0,
      },
      supportedFileTypes: [
        'ts',
        'tsx',
        'js',
        'jsx',
        'json',
        'md',
        'txt',
        'css',
        'scss',
        'html',
        'xml',
        'yaml',
        'yml',
        'env',
        'acd',
        'l5x',
      ],
    });
  } catch (error) {
    console.error('Search API GET error:', error);
    return NextResponse.json({ error: 'Failed to retrieve search configuration' }, { status: 500 });
  }
}

/**
 * Type guard for SearchRequest validation
 */
function isSearchRequest(value: unknown): value is SearchRequest {
  if (!value || typeof value !== 'object') {
    return false;
  }

  const obj = value as Record<string, unknown>;

  // Required field: query
  if (typeof obj.query !== 'string') {
    return false;
  }

  // Optional fields with type checking
  if (obj.scope !== undefined && typeof obj.scope !== 'object') {
    return false;
  }

  if (obj.options !== undefined && typeof obj.options !== 'object') {
    return false;
  }

  if (obj.providers !== undefined && !Array.isArray(obj.providers)) {
    return false;
  }

  return true;
}

/**
 * Create standardized error response
 */
function createErrorResponse(code: SearchError['code'], message: string): { error: SearchError } {
  return {
    error: {
      code,
      message,
    },
  };
}
