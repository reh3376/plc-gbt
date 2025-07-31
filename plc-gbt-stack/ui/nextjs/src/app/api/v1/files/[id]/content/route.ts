import { promises as fs } from 'fs';
import { NextRequest, NextResponse } from 'next/server';
import { join } from 'path';

interface RouteContext {
  params: Promise<{ id: string }>;
}

// GET /api/v1/files/[id]/content - Read file content
export async function GET(request: NextRequest, context: RouteContext) {
  try {
    const { id } = await context.params;
    const decodedId = decodeURIComponent(id);

    console.log('📖 READ FILE CONTENT - Request for:', decodedId);

    // Security: Prevent directory traversal
    if (decodedId.includes('..') || decodedId.includes('~')) {
      console.warn('📖 READ FILE CONTENT - Invalid file path:', decodedId);
      return NextResponse.json({ error: 'Invalid file path' }, { status: 400 });
    }

    // Convert file ID to actual file path
    const basePath = process.cwd();
    const projectFilesPath = join(basePath, 'project-files');
    const filePath = join(
      projectFilesPath,
      decodedId.startsWith('/') ? decodedId.slice(1) : decodedId
    );

    console.log('📖 READ FILE CONTENT - Reading from:', filePath);

    try {
      const content = await fs.readFile(filePath, 'utf-8');
      console.log('📖 READ FILE CONTENT - Successfully read, length:', content.length);

      return new NextResponse(content, {
        status: 200,
        headers: {
          'Content-Type': 'text/plain; charset=utf-8',
        },
      });
    } catch (fileError: unknown) {
      const err = fileError as NodeJS.ErrnoException;
      console.error('📖 READ FILE CONTENT - File read error:', err.message);

      if (err.code === 'ENOENT') {
        return NextResponse.json({ error: 'File not found' }, { status: 404 });
      }

      return NextResponse.json({ error: 'Failed to read file' }, { status: 500 });
    }
  } catch (error: unknown) {
    console.error('📖 READ FILE CONTENT - Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// PUT /api/v1/files/[id]/content - Write file content
export async function PUT(request: NextRequest, context: RouteContext) {
  try {
    const { id } = await context.params;
    const decodedId = decodeURIComponent(id);
    const body = await request.json();

    console.log('💾 WRITE FILE CONTENT - Request for:', decodedId);
    console.log('💾 WRITE FILE CONTENT - Content length:', body.content?.length);

    if (!body.content && body.content !== '') {
      return NextResponse.json({ error: 'Content is required' }, { status: 400 });
    }

    // Security: Prevent directory traversal
    if (decodedId.includes('..') || decodedId.includes('~')) {
      console.warn('💾 WRITE FILE CONTENT - Invalid file path:', decodedId);
      return NextResponse.json({ error: 'Invalid file path' }, { status: 400 });
    }

    // Convert file ID to actual file path
    const basePath = process.cwd();
    const projectFilesPath = join(basePath, 'project-files');
    const filePath = join(
      projectFilesPath,
      decodedId.startsWith('/') ? decodedId.slice(1) : decodedId
    );

    console.log('💾 WRITE FILE CONTENT - Writing to:', filePath);

    try {
      await fs.writeFile(filePath, body.content, 'utf-8');
      console.log('💾 WRITE FILE CONTENT - Successfully written');

      return NextResponse.json(
        {
          success: true,
          message: 'File content updated successfully',
          fileId: decodedId,
          contentLength: body.content.length,
        },
        { status: 200 }
      );
    } catch (fileError: unknown) {
      const err = fileError as Error;
      console.error('💾 WRITE FILE CONTENT - File write error:', err.message);

      return NextResponse.json({ error: 'Failed to write file' }, { status: 500 });
    }
  } catch (error: unknown) {
    console.error('💾 WRITE FILE CONTENT - Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
