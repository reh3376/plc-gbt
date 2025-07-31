/**
 * File Upload API Route - AI Task Orchestrator TypeScript Implementation
 *
 * @description Handles multipart file uploads with type safety
 * @compliance Strict TypeScript - zero `any` types policy
 * @features File validation, size limits, MIME type checking
 */

import type { FileItem, FileOperationResult } from '@/lib/types/file-explorer.types';
import { existsSync } from 'fs';
import { mkdir, writeFile } from 'fs/promises';
import { NextRequest, NextResponse } from 'next/server';
import { extname, join } from 'path';

// Configuration
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
// Allow all file extensions - no restrictions
const ALLOWED_EXTENSIONS: string[] = []; // Empty array means all extensions allowed
const PROJECT_ROOT = process.env.PROJECT_FILES_ROOT || join(process.cwd(), 'project-files');

// File validation interface
interface FileValidationResult {
  isValid: boolean;
  error?: string;
  fileSize?: number;
  extension?: string;
}

// Validate uploaded file
function validateFile(file: File): FileValidationResult {
  const extension = extname(file.name).toLowerCase();

  // Check file size
  if (file.size > MAX_FILE_SIZE) {
    return {
      isValid: false,
      error: `File size exceeds ${MAX_FILE_SIZE / (1024 * 1024)}MB limit`,
      fileSize: file.size,
    };
  }

  // Check file extension (skip if no restrictions)
  if (ALLOWED_EXTENSIONS.length > 0 && !ALLOWED_EXTENSIONS.includes(extension)) {
    return {
      isValid: false,
      error: `File type ${extension} not allowed. Allowed types: ${ALLOWED_EXTENSIONS.join(', ')}`,
      extension,
    };
  }

  // Check file name
  if (file.name.includes('..') || /[<>:"/\\|?*]/.test(file.name)) {
    return {
      isValid: false,
      error: 'Invalid characters in filename',
    };
  }

  return {
    isValid: true,
    fileSize: file.size,
    extension,
  };
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

// Ensure project directory exists
async function ensureProjectDirectory(): Promise<void> {
  if (!existsSync(PROJECT_ROOT)) {
    await mkdir(PROJECT_ROOT, { recursive: true });
  }
}

/**
 * GET /api/v1/files/upload - Test route reachability
 */
export async function GET(): Promise<NextResponse> {
  console.log('🔧 UPLOAD API - GET request received - route is reachable');
  return NextResponse.json({
    message: 'Upload API route is reachable',
    timestamp: new Date().toISOString(),
  });
}

/**
 * POST /api/v1/files/upload - Upload multiple files
 */
export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    const formData = await request.formData();
    const files = formData.getAll('files') as File[];
    const targetPath = formData.get('targetPath') as string;
    const overwrite = formData.get('overwrite') === 'true';

    // Validate request
    if (!files || files.length === 0) {
      return NextResponse.json(
        {
          success: false,
          message: 'No files provided',
          error: 'Validation error',
        },
        { status: 400 }
      );
    }

    if (!targetPath) {
      return NextResponse.json(
        {
          success: false,
          message: 'Target path is required',
          error: 'Validation error',
        },
        { status: 400 }
      );
    }

    // Validate each file
    const validationErrors: string[] = [];
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const validation = validateFile(file);

      if (!validation.isValid) {
        validationErrors.push(`File ${i + 1} (${file.name}): ${validation.error}`);
      }
    }

    if (validationErrors.length > 0) {
      return NextResponse.json(
        {
          success: false,
          message: 'File validation failed',
          error: validationErrors.join('; '),
        },
        { status: 400 }
      );
    }

    await ensureProjectDirectory();

    // Process uploads
    const uploadedFiles: FileItem[] = [];
    const uploadErrors: string[] = [];

    for (const file of files) {
      try {
        // Sanitize paths
        const sanitizedTargetPath = targetPath.replace(/^\/+/, '').replace(/\.\.+/g, '');

        // Sanitize filename (frontend now sends just filename, not folder paths)
        const sanitizedFileName = file.name.replace(/[<>:"/\\|?*]/g, '_');

        const targetDir = join(PROJECT_ROOT, sanitizedTargetPath);
        const filePath = join(targetDir, sanitizedFileName);

        // Check if file exists
        if (existsSync(filePath) && !overwrite) {
          uploadErrors.push(`File ${file.name} already exists (use overwrite=true to replace)`);
          continue;
        }

        // Ensure target directory exists
        await mkdir(targetDir, { recursive: true });

        // Write file
        const buffer = await file.arrayBuffer();
        await writeFile(filePath, Buffer.from(buffer));

        // Create file item response
        const relativePath = join(sanitizedTargetPath, sanitizedFileName).replace(/\\/g, '/');
        const uploadedFile: FileItem = {
          id: relativePath,
          name: sanitizedFileName,
          type: 'file',
          path: `/${relativePath}`,
          size: file.size,
          extension: extname(sanitizedFileName),
          mimeType: getMimeType(extname(sanitizedFileName)),
          lastModified: new Date(),
        };

        uploadedFiles.push(uploadedFile);
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
        uploadErrors.push(
          `Failed to upload ${file.name}: ${error instanceof Error ? error.message : 'Unknown error'}`
        );
      }
    }

    // Return results
    const hasErrors = uploadErrors.length > 0;
    const hasSuccesses = uploadedFiles.length > 0;

    if (!hasSuccesses && hasErrors) {
      // All uploads failed
      return NextResponse.json(
        {
          success: false,
          message: 'All file uploads failed',
          error: uploadErrors.join('; '),
        },
        { status: 500 }
      );
    }

    // Some or all uploads succeeded
    const response: FileOperationResult = {
      success: true,
      message: hasErrors
        ? `${uploadedFiles.length} files uploaded, ${uploadErrors.length} failed`
        : `${uploadedFiles.length} files uploaded successfully`,
      data: uploadedFiles,
      ...(hasErrors && { error: uploadErrors.join('; ') }),
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('POST /api/v1/files/upload error:', error);

    // Mock upload success for development
    const mockFile: FileItem = {
      id: `mock-upload-${Date.now()}`,
      name: 'uploaded-file.json',
      type: 'file',
      path: '/uploads/uploaded-file.json',
      size: 1024,
      extension: '.json',
      mimeType: 'application/json',
      lastModified: new Date(),
    };

    return NextResponse.json(
      {
        success: false,
        message: 'Upload failed, returning mock data for development',
        error: error instanceof Error ? error.message : 'Unknown error',
        data: [mockFile],
      },
      { status: 500 }
    );
  }
}
