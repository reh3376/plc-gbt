/**
 * File Content API Routes - Proxy to FastAPI Backend
 *
 * Handles file content read/write operations
 */

import { NextRequest, NextResponse } from 'next/server';

// Backend API base URL
const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';

/**
 * GET /api/v1/files/{id}/content - Get file content
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse> {
  try {
    const { id: fileId } = await params;

    // Proxy to backend
    const response = await fetch(
      `${BACKEND_API_URL}/api/v1/files/${encodeURIComponent(fileId)}/content`,
      {
        headers: {
          Accept: 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('File content read error:', error);

    return NextResponse.json(
      {
        success: false,
        message: 'Failed to read file content',
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * PUT /api/v1/files/{id}/content - Update file content
 */
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse> {
  try {
    const { id: fileId } = await params;
    const body = await request.json();

    // Proxy to backend
    const response = await fetch(
      `${BACKEND_API_URL}/api/v1/files/${encodeURIComponent(fileId)}/content`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify(body),
      }
    );

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('File content save error:', error);

    return NextResponse.json(
      {
        success: false,
        message: 'Failed to save file content',
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
