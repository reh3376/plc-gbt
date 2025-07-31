/**
 * File Management API Routes - AI Task Orchestrator TypeScript Implementation
 *
 * @description RESTful API endpoints for file management operations
 * @compliance Strict TypeScript - zero `any` types policy
 * @integration Supports both real filesystem and mock data fallback
 */

import type {
  CreateFileRequest,
  FileItem,
  FileOperationResult,
} from '@/lib/types/file-explorer.types';
import { existsSync } from 'fs';
import { mkdir, readdir, stat, writeFile } from 'fs/promises';
import { NextRequest, NextResponse } from 'next/server';
import { extname, join } from 'path';

// Safe project root path
const PROJECT_ROOT = process.env.PROJECT_FILES_ROOT || join(process.cwd(), 'project-files');

// Ensure project directory exists
async function ensureProjectDirectory(): Promise<void> {
  if (!existsSync(PROJECT_ROOT)) {
    await mkdir(PROJECT_ROOT, { recursive: true });
  }
}

// Convert filesystem entry to FileItem
async function createFileItem(
  fullPath: string,
  relativePath: string,
  name: string
): Promise<FileItem> {
  try {
    const stats = await stat(fullPath);
    const isDirectory = stats.isDirectory();

    const fileItem: FileItem = {
      id: relativePath.replace(/\\/g, '/'),
      name: name,
      type: isDirectory ? 'folder' : 'file',
      path: relativePath.replace(/\\/g, '/'),
      size: isDirectory ? undefined : stats.size,
      lastModified: stats.mtime,
      extension: isDirectory ? undefined : extname(name),
      mimeType: isDirectory ? undefined : getMimeType(extname(name)),
    };

    // Load children for folders
    if (isDirectory) {
      try {
        const children = await readdir(fullPath);
        const childItems: FileItem[] = [];

        for (const childName of children) {
          const childPath = join(fullPath, childName);
          const childRelativePath = join(relativePath, childName);
          const childItem = await createFileItem(childPath, childRelativePath, childName);
          childItems.push(childItem);
        }

        fileItem.children = childItems;
        fileItem.isExpanded = false;
      } catch (error) {
        console.warn(`Failed to read directory ${fullPath}:`, error);
        fileItem.children = [];
      }
    }

    return fileItem;
  } catch (error) {
    throw new Error(
      `Failed to create file item for ${fullPath}: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

// Get MIME type for file extension
function getMimeType(extension: string): string {
  const mimeTypes: Record<string, string> = {
    '.acd': 'application/x-acd',
    '.l5x': 'application/xml',
    '.json': 'application/json',
    '.txt': 'text/plain',
    '.csv': 'text/csv',
    '.md': 'text/markdown',
    '.js': 'application/javascript',
    '.ts': 'application/typescript',
    '.py': 'text/x-python',
  };

  return mimeTypes[extension.toLowerCase()] || 'application/octet-stream';
}

// Mock data fallback
function getMockFiles(): FileItem[] {
  return [
    {
      id: 'root-projects',
      name: 'PLC Projects',
      type: 'folder',
      path: '/projects',
      isExpanded: true,
      children: [
        {
          id: 'distillation-control',
          name: 'Distillation_Control.acd',
          type: 'file',
          path: '/projects/Distillation_Control.acd',
          size: 1024000,
          extension: '.acd',
          mimeType: 'application/x-acd',
          lastModified: new Date('2024-01-15T10:30:00Z'),
        },
        {
          id: 'boiler-safety',
          name: 'Boiler_Safety.l5x',
          type: 'file',
          path: '/projects/Boiler_Safety.l5x',
          size: 512000,
          extension: '.l5x',
          mimeType: 'application/xml',
          lastModified: new Date('2024-01-14T15:45:00Z'),
        },
        {
          id: 'control-loops',
          name: 'Control_Loops',
          type: 'folder',
          path: '/projects/Control_Loops',
          isExpanded: false,
          children: [
            {
              id: 'pid-temperature',
              name: 'PID_Temperature.acd',
              type: 'file',
              path: '/projects/Control_Loops/PID_Temperature.acd',
              size: 256000,
              extension: '.acd',
              mimeType: 'application/x-acd',
              lastModified: new Date('2024-01-13T09:15:00Z'),
            },
          ],
        },
      ],
    },
    {
      id: 'root-workflows',
      name: 'Workflows',
      type: 'folder',
      path: '/workflows',
      isExpanded: false,
      children: [
        {
          id: 'startup-sequence',
          name: 'Startup_Sequence.workflow',
          type: 'file',
          path: '/workflows/Startup_Sequence.workflow',
          size: 8192,
          extension: '.workflow',
          mimeType: 'application/json',
          lastModified: new Date('2024-01-12T14:20:00Z'),
        },
      ],
    },
  ];
}

/**
 * GET /api/v1/files - Retrieve file tree
 */
export async function GET(): Promise<NextResponse> {
  try {
    await ensureProjectDirectory();

    // Try to read from filesystem
    try {
      const children = await readdir(PROJECT_ROOT);
      const fileItems: FileItem[] = [];

      for (const name of children) {
        const fullPath = join(PROJECT_ROOT, name);
        const relativePath = `/${name}`;
        const item = await createFileItem(fullPath, relativePath, name);
        fileItems.push(item);
      }

      const response = {
        success: true,
        message: `Loaded ${fileItems.length} files from filesystem`,
        data: fileItems,
      };

      return NextResponse.json(response);
    } catch (fsError) {
      // Fallback to mock data
      console.warn('Filesystem read failed, using mock data:', fsError);

      const response = {
        success: true,
        message: 'Loaded files (mock data)',
        data: getMockFiles(),
      };

      return NextResponse.json(response);
    }
  } catch (error) {
    console.error('GET /api/v1/files error:', error);

    return NextResponse.json(
      {
        success: false,
        message: 'Failed to retrieve files',
        error: error instanceof Error ? error.message : 'Unknown error',
        data: getMockFiles(), // Always provide fallback data
      },
      { status: 500 }
    );
  }
}

/**
 * POST /api/v1/files - Create file or folder
 */
export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    const body: CreateFileRequest = await request.json();

    // Validate request
    if (!body.name || !body.type || !body.parentPath) {
      return NextResponse.json(
        {
          success: false,
          message: 'Missing required fields: name, type, parentPath',
          error: 'Validation error',
        },
        { status: 400 }
      );
    }

    await ensureProjectDirectory();

    // Construct safe file path
    const sanitizedParentPath = body.parentPath.replace(/^\/+/, '').replace(/\.\.+/g, '');
    const sanitizedFileName = body.name.replace(/[<>:"/\\|?*]/g, '_'); // Remove invalid characters
    const targetDir = join(PROJECT_ROOT, sanitizedParentPath);
    const targetPath = join(targetDir, sanitizedFileName);

    try {
      // Ensure parent directory exists
      await mkdir(targetDir, { recursive: true });

      if (body.type === 'folder') {
        await mkdir(targetPath, { recursive: true });
      } else {
        await writeFile(targetPath, body.content || '', 'utf8');
      }

      // Create response file item
      const relativePath = join(sanitizedParentPath, sanitizedFileName).replace(/\\/g, '/');
      const newFile: FileItem = {
        id: relativePath,
        name: sanitizedFileName,
        type: body.type,
        path: `/${relativePath}`,
        size: body.type === 'file' ? (body.content || '').length : undefined,
        extension: body.type === 'file' ? extname(sanitizedFileName) : undefined,
        mimeType: body.type === 'file' ? getMimeType(extname(sanitizedFileName)) : undefined,
        lastModified: new Date(),
        ...(body.type === 'folder' && { children: [], isExpanded: false }),
      };

      const response: FileOperationResult = {
        success: true,
        message: `${body.type === 'file' ? 'File' : 'Folder'} created successfully`,
        data: newFile,
      };

      return NextResponse.json(response);
    } catch (fsError) {
      // Return mock success for offline development
      console.warn('Filesystem write failed, returning mock success:', fsError);

      const mockFile: FileItem = {
        id: `mock-${Date.now()}`,
        name: body.name,
        type: body.type,
        path: `${body.parentPath}/${body.name}`.replace('//', '/'),
        size: body.type === 'file' ? (body.content || '').length : undefined,
        extension: body.type === 'file' ? extname(body.name) : undefined,
        mimeType: body.type === 'file' ? getMimeType(extname(body.name)) : undefined,
        lastModified: new Date(),
        ...(body.type === 'folder' && { children: [], isExpanded: false }),
      };

      const response: FileOperationResult = {
        success: true,
        message: `${body.type === 'file' ? 'File' : 'Folder'} created successfully (mock mode)`,
        data: mockFile,
      };

      return NextResponse.json(response);
    }
  } catch (error) {
    console.error('POST /api/v1/files error:', error);

    return NextResponse.json(
      {
        success: false,
        message: 'Failed to create file/folder',
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
