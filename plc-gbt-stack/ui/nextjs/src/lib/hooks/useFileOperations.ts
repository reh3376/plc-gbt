/**
 * File Operations Hook - AI Task Orchestrator TypeScript Implementation
 *
 * @description React hook for managing file operations with state
 * @compliance Strict TypeScript with comprehensive error handling
 * @integration API client integration with optimistic updates
 */

import { FileOperationAPIError, fileOperationsAPI } from '@/lib/api/file-operations';
import type {
  CreateFileRequest,
  DeleteFileRequest,
  FileExplorerState,
  FileItem,
  FileOperationResult,
  MoveFileRequest,
  RenameFileRequest,
  UploadFileRequest,
} from '@/lib/types/file-explorer.types';
import { useCallback, useEffect, useRef, useState } from 'react';

// Hook configuration
interface UseFileOperationsConfig {
  autoRefresh?: boolean;
  refreshInterval?: number;
  enableOptimisticUpdates?: boolean;
  onError?: (error: FileOperationAPIError) => void;
  onSuccess?: (operation: string, result: FileOperationResult) => void;
}

// Hook return type
interface UseFileOperationsReturn {
  // State
  files: FileItem[];
  isLoading: boolean;
  error: string | null;
  selectedFileId: string | null;

  // Operations
  createFile: (request: CreateFileRequest) => Promise<FileOperationResult>;
  createFolder: (request: CreateFileRequest) => Promise<FileOperationResult>;
  uploadFiles: (request: UploadFileRequest) => Promise<FileOperationResult>;
  deleteFile: (request: DeleteFileRequest) => Promise<FileOperationResult>;
  renameFile: (request: RenameFileRequest) => Promise<FileOperationResult>;
  moveFile: (request: MoveFileRequest) => Promise<FileOperationResult>;
  refreshFiles: () => Promise<void>;

  // UI State Management
  selectFile: (fileId: string | null) => void;
  expandFolder: (folderId: string) => void;
  collapseFolder: (folderId: string) => void;
  toggleFolder: (folderId: string) => void;

  // Utility functions
  findFileById: (fileId: string) => FileItem | null;
  getFilesByType: (type: 'file' | 'folder') => FileItem[];
  searchFiles: (query: string) => FileItem[];
}

/**
 * Custom hook for file operations
 *
 * @param config Configuration options for the hook
 * @returns File operations state and methods
 */
export function useFileOperations(config: UseFileOperationsConfig = {}): UseFileOperationsReturn {
  const {
    autoRefresh = false,
    refreshInterval = 30000, // 30 seconds
    enableOptimisticUpdates = true,
    onError,
    onSuccess,
  } = config;

  // State management
  const [state, setState] = useState<FileExplorerState>({
    files: [],
    selectedFileId: null,
    expandedFolders: new Set<string>(),
    isLoading: false,
    error: null,
  });

  // Refs for cleanup
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const loadFilesRef = useRef<(() => Promise<void>) | null>(null);

  // Helper function to update files in state
  const updateFilesInState = useCallback((updater: (files: FileItem[]) => FileItem[]) => {
    setState(prev => ({
      ...prev,
      files: updater(prev.files),
    }));
  }, []);

  // Helper function to handle API errors
  const handleError = useCallback(
    (error: unknown, operation: string) => {
      const apiError =
        error instanceof FileOperationAPIError
          ? error
          : new FileOperationAPIError(
              error instanceof Error ? error.message : 'Unknown error',
              0,
              operation
            );

      setState(prev => ({
        ...prev,
        error: apiError.message,
        isLoading: false,
      }));

      onError?.(apiError);
      console.error(`File operation failed (${operation}):`, apiError);
    },
    [onError]
  );

  // Helper function to handle API success
  const handleSuccess = useCallback(
    (operation: string, result: FileOperationResult) => {
      setState(prev => ({
        ...prev,
        error: null,
      }));

      onSuccess?.(operation, result);
    },
    [onSuccess]
  );

  // Recursive helper to find file by ID
  const findFileById = useCallback(
    (fileId: string, files: FileItem[] = state.files): FileItem | null => {
      for (const file of files) {
        if (file.id === fileId) {
          return file;
        }
        if (file.children) {
          const found = findFileById(fileId, file.children);
          if (found) return found;
        }
      }
      return null;
    },
    [state.files]
  );

  // Recursive helper to update file in tree
  const updateFileInTree = useCallback(
    (files: FileItem[], fileId: string, updater: (file: FileItem) => FileItem): FileItem[] => {
      return files.map(file => {
        if (file.id === fileId) {
          return updater(file);
        }
        if (file.children) {
          return {
            ...file,
            children: updateFileInTree(file.children, fileId, updater),
          };
        }
        return file;
      });
    },
    []
  );

  // Recursive helper to remove file from tree
  const removeFileFromTree = useCallback((files: FileItem[], fileId: string): FileItem[] => {
    return files
      .filter(file => file.id !== fileId)
      .map(file => {
        if (file.children) {
          return {
            ...file,
            children: removeFileFromTree(file.children, fileId),
          };
        }
        return file;
      });
  }, []);

  // Helper function to update expanded state in file tree
  const updateExpandedStateInFiles = useCallback(
    (files: FileItem[], expandedFolders: Set<string>): FileItem[] => {
      return files.map(file => {
        const updatedFile = {
          ...file,
          isExpanded: file.type === 'folder' ? expandedFolders.has(file.id) : undefined,
        };

        if (file.children) {
          updatedFile.children = updateExpandedStateInFiles(file.children, expandedFolders);
        }

        return updatedFile;
      });
    },
    []
  );

  // Helper to add file to correct parent folder in tree
  const addFileToTree = useCallback(
    (files: FileItem[], newFile: FileItem, parentPath: string): FileItem[] => {
      console.log('🌳 TREE UPDATE - Adding file to tree:', {
        newFile,
        parentPath,
        currentFiles: files.length,
      });

      // If parentPath is root ("/"), add to root level
      if (parentPath === '/' || parentPath === '') {
        console.log('🌳 TREE UPDATE - Adding to root level');
        return [...files, newFile];
      }

      // Find the parent folder and add the file to its children
      const addToParent = (fileList: FileItem[]): FileItem[] => {
        return fileList.map(file => {
          if (file.type === 'folder' && file.path === parentPath) {
            console.log('🌳 TREE UPDATE - Found parent folder:', file.name, 'adding child');
            return {
              ...file,
              children: [...(file.children || []), newFile],
              isExpanded: true, // Expand folder to show new file
            };
          }
          if (file.children) {
            return {
              ...file,
              children: addToParent(file.children),
            };
          }
          return file;
        });
      };

      const updatedFiles = addToParent(files);
      console.log('🌳 TREE UPDATE - Tree updated, files count:', updatedFiles.length);
      return updatedFiles;
    },
    []
  );

  // Load files from API
  const loadFiles = useCallback(async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const files = await fileOperationsAPI.getFiles();

      setState(prev => ({
        ...prev,
        files,
        isLoading: false,
        error: null,
      }));
    } catch (error) {
      handleError(error, 'loadFiles');
    }
  }, [handleError]);

  // Update ref whenever loadFiles changes
  useEffect(() => {
    loadFilesRef.current = loadFiles;
  }, [loadFiles]);

  // Create file operation
  const createFile = useCallback(
    async (request: CreateFileRequest): Promise<FileOperationResult> => {
      try {
        setState(prev => ({ ...prev, isLoading: true }));

        const result = await fileOperationsAPI.createFile(request);

        if (result.success && result.data && enableOptimisticUpdates) {
          // Add new file to state optimistically
          const newFile = result.data as FileItem;
          updateFilesInState(files => addFileToTree(files, newFile, request.parentPath));
        }

        handleSuccess('createFile', result);
        setState(prev => ({ ...prev, isLoading: false }));

        return result;
      } catch (error) {
        handleError(error, 'createFile');
        throw error;
      }
    },
    [enableOptimisticUpdates, updateFilesInState, handleSuccess, handleError, addFileToTree]
  );

  // Create folder operation
  const createFolder = useCallback(
    async (request: CreateFileRequest): Promise<FileOperationResult> => {
      const folderRequest: CreateFileRequest = { ...request, type: 'folder' };
      return createFile(folderRequest);
    },
    [createFile]
  );

  // Upload files operation
  const uploadFiles = useCallback(
    async (request: UploadFileRequest): Promise<FileOperationResult> => {
      try {
        setState(prev => ({ ...prev, isLoading: true }));

        const result = await fileOperationsAPI.uploadFiles(request);

        if (result.success && result.data && enableOptimisticUpdates) {
          // Add uploaded files to state
          const uploadedFiles = Array.isArray(result.data) ? result.data : [result.data];
          updateFilesInState(files => [...files, ...uploadedFiles]);
        }

        handleSuccess('uploadFiles', result);
        setState(prev => ({ ...prev, isLoading: false }));

        return result;
      } catch (error) {
        handleError(error, 'uploadFiles');
        throw error;
      }
    },
    [enableOptimisticUpdates, updateFilesInState, handleSuccess, handleError]
  );

  // Delete file operation
  const deleteFile = useCallback(
    async (request: DeleteFileRequest): Promise<FileOperationResult> => {
      try {
        setState(prev => ({ ...prev, isLoading: true }));

        if (enableOptimisticUpdates) {
          // Remove file from state optimistically
          updateFilesInState(files => removeFileFromTree(files, request.id));
        }

        const result = await fileOperationsAPI.deleteFile(request);

        if (!result.success && enableOptimisticUpdates) {
          // Revert optimistic update on failure
          await loadFiles();
        }

        handleSuccess('deleteFile', result);
        setState(prev => ({ ...prev, isLoading: false }));

        return result;
      } catch (error) {
        handleError(error, 'deleteFile');
        // Revert optimistic update on error
        if (enableOptimisticUpdates) {
          await loadFiles();
        }
        throw error;
      }
    },
    [
      enableOptimisticUpdates,
      updateFilesInState,
      removeFileFromTree,
      handleSuccess,
      handleError,
      loadFiles,
    ]
  );

  // Rename file operation
  const renameFile = useCallback(
    async (request: RenameFileRequest): Promise<FileOperationResult> => {
      try {
        setState(prev => ({ ...prev, isLoading: true }));

        if (enableOptimisticUpdates) {
          // Update file name optimistically
          updateFilesInState(files =>
            updateFileInTree(files, request.id, file => ({ ...file, name: request.newName }))
          );
        }

        const result = await fileOperationsAPI.renameFile(request);

        if (!result.success && enableOptimisticUpdates) {
          // Revert optimistic update on failure
          await loadFiles();
        }

        handleSuccess('renameFile', result);
        setState(prev => ({ ...prev, isLoading: false }));

        return result;
      } catch (error) {
        handleError(error, 'renameFile');
        // Revert optimistic update on error
        if (enableOptimisticUpdates) {
          await loadFiles();
        }
        throw error;
      }
    },
    [
      enableOptimisticUpdates,
      updateFilesInState,
      updateFileInTree,
      handleSuccess,
      handleError,
      loadFiles,
    ]
  );

  // Move file operation
  const moveFile = useCallback(
    async (request: MoveFileRequest): Promise<FileOperationResult> => {
      try {
        setState(prev => ({ ...prev, isLoading: true }));

        const result = await fileOperationsAPI.moveFile(request);

        // For move operations, refresh to get accurate tree structure while preserving expanded state
        if (result.success) {
          // Save current expanded folders state
          const currentExpandedFolders = new Set(state.expandedFolders);
          console.log(
            '💾 MOVE FILE - Preserving expanded folders:',
            Array.from(currentExpandedFolders)
          );

          await loadFiles();

          // Restore expanded folders state after refresh
          setState(prev => ({
            ...prev,
            expandedFolders: currentExpandedFolders,
            files: updateExpandedStateInFiles(prev.files, currentExpandedFolders),
          }));

          console.log('♻️ MOVE FILE - Restored expanded folders state');
        }

        handleSuccess('moveFile', result);
        setState(prev => ({ ...prev, isLoading: false }));

        return result;
      } catch (error) {
        handleError(error, 'moveFile');
        throw error;
      }
    },
    [handleSuccess, handleError, loadFiles, state.expandedFolders, updateExpandedStateInFiles]
  );

  // Refresh files
  const refreshFiles = useCallback(async () => {
    await loadFiles();
  }, [loadFiles]);

  // UI State Management
  const selectFile = useCallback((fileId: string | null) => {
    setState(prev => ({
      ...prev,
      selectedFileId: fileId,
    }));
  }, []);

  const expandFolder = useCallback(
    (folderId: string) => {
      setState(prev => ({
        ...prev,
        expandedFolders: new Set([...prev.expandedFolders, folderId]),
      }));

      // Also update the file's isExpanded property
      updateFilesInState(files =>
        updateFileInTree(files, folderId, file => ({ ...file, isExpanded: true }))
      );
    },
    [updateFilesInState, updateFileInTree]
  );

  const collapseFolder = useCallback(
    (folderId: string) => {
      setState(prev => {
        const newExpandedFolders = new Set(prev.expandedFolders);
        newExpandedFolders.delete(folderId);
        return {
          ...prev,
          expandedFolders: newExpandedFolders,
        };
      });

      // Also update the file's isExpanded property
      updateFilesInState(files =>
        updateFileInTree(files, folderId, file => ({ ...file, isExpanded: false }))
      );
    },
    [updateFilesInState, updateFileInTree]
  );

  const toggleFolder = useCallback(
    (folderId: string) => {
      const isExpanded = state.expandedFolders.has(folderId);
      if (isExpanded) {
        collapseFolder(folderId);
      } else {
        expandFolder(folderId);
      }
    },
    [state.expandedFolders, expandFolder, collapseFolder]
  );

  // Utility functions
  const getFilesByType = useCallback(
    (type: 'file' | 'folder'): FileItem[] => {
      const collectFiles = (files: FileItem[]): FileItem[] => {
        const result: FileItem[] = [];
        for (const file of files) {
          if (file.type === type) {
            result.push(file);
          }
          if (file.children) {
            result.push(...collectFiles(file.children));
          }
        }
        return result;
      };
      return collectFiles(state.files);
    },
    [state.files]
  );

  const searchFiles = useCallback(
    (query: string): FileItem[] => {
      const searchTerm = query.toLowerCase();
      const collectMatches = (files: FileItem[]): FileItem[] => {
        const result: FileItem[] = [];
        for (const file of files) {
          if (
            file.name.toLowerCase().includes(searchTerm) ||
            file.path.toLowerCase().includes(searchTerm)
          ) {
            result.push(file);
          }
          if (file.children) {
            result.push(...collectMatches(file.children));
          }
        }
        return result;
      };
      return collectMatches(state.files);
    },
    [state.files]
  );

  // Effects
  useEffect(() => {
    // Initial load - call loadFiles directly without dependency
    const initialLoad = async () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      abortControllerRef.current = new AbortController();

      setState(prev => ({ ...prev, isLoading: true, error: null }));

      try {
        console.log('🔄 LOADING FILES - Fetching from API...');
        const files = await fileOperationsAPI.getFiles();
        console.log('✅ LOADING FILES - API response:', { count: files.length, files });

        setState(prev => ({
          ...prev,
          files,
          isLoading: false,
          error: null,
        }));
      } catch (error) {
        console.error('❌ LOADING FILES - API failed:', error);
        const apiError =
          error instanceof FileOperationAPIError
            ? error
            : new FileOperationAPIError(
                error instanceof Error ? error.message : 'Unknown error',
                0,
                'loadFiles'
              );

        setState(prev => ({
          ...prev,
          error: apiError.message,
          isLoading: false,
        }));

        onError?.(apiError);
        console.error('File operation failed (loadFiles):', apiError);
      }
    };

    initialLoad();

    // Cleanup on unmount
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, []); // Empty dependency array - this should only run once on mount

  useEffect(() => {
    // Auto refresh setup
    if (autoRefresh && refreshInterval > 0) {
      refreshIntervalRef.current = setInterval(() => {
        // Use ref to avoid dependency on loadFiles function
        loadFilesRef.current?.();
      }, refreshInterval);

      return () => {
        if (refreshIntervalRef.current) {
          clearInterval(refreshIntervalRef.current);
        }
      };
    }
  }, [autoRefresh, refreshInterval]); // Removed loadFiles dependency

  return {
    // State
    files: state.files,
    isLoading: state.isLoading,
    error: state.error,
    selectedFileId: state.selectedFileId,

    // Operations
    createFile,
    createFolder,
    uploadFiles,
    deleteFile,
    renameFile,
    moveFile,
    refreshFiles,

    // UI State Management
    selectFile,
    expandFolder,
    collapseFolder,
    toggleFolder,

    // Utility functions
    findFileById: (fileId: string) => findFileById(fileId),
    getFilesByType,
    searchFiles,
  };
}
