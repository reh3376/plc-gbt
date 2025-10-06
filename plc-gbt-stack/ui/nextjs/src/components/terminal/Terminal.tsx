'use client';

import { useTerminalStore } from '@/lib/stores/terminal-store';
import { cn } from '@/lib/utils/cn';
import { KeyboardEvent, useEffect, useRef, useState } from 'react';

interface CommandHistory {
  command: string;
  output: string;
  timestamp: Date;
  status: 'success' | 'error' | 'info';
  directory?: string;
}

interface TerminalProps {
  className?: string;
}

export function Terminal({ className }: TerminalProps) {
  // Check for saved session to determine initial state
  const getInitialHistory = (): CommandHistory[] => {
    try {
      const savedSession = localStorage.getItem('plc-gbt-terminal-session');
      if (savedSession) {
        const session = JSON.parse(savedSession);
        if (session.history && Array.isArray(session.history)) {
          return session.history.map((entry: any) => ({
            ...entry,
            timestamp: new Date(entry.timestamp),
          }));
        }
      }
    } catch (error) {
      console.warn('Failed to load initial session:', error);
    }
    // Default welcome message if no saved session
    return [
      {
        command: '',
        output: 'Welcome to PLC-GBT Terminal\nType "help" for available commands.',
        timestamp: new Date(),
        status: 'info' as const,
      },
    ];
  };

  const getInitialCommandHistory = (): string[] => {
    try {
      const savedSession = localStorage.getItem('plc-gbt-terminal-session');
      if (savedSession) {
        const session = JSON.parse(savedSession);
        if (session.commandHistory && Array.isArray(session.commandHistory)) {
          return session.commandHistory;
        }
      }
    } catch (error) {
      console.warn('Failed to load command history:', error);
    }
    return [];
  };

  const [history, setHistory] = useState<CommandHistory[]>(getInitialHistory());
  const [currentInput, setCurrentInput] = useState('');
  const [commandHistory, setCommandHistory] = useState<string[]>(getInitialCommandHistory());
  const [historyIndex, setHistoryIndex] = useState(-1);
  const { currentDirectory, setCurrentDirectory } = useTerminalStore();
  const [isRunningCommand, setIsRunningCommand] = useState(false);
  const [runningCommandAbort, setRunningCommandAbort] = useState<(() => void) | null>(null);
  const [isWaitingForOutput, setIsWaitingForOutput] = useState(false);
  const [tabCompletions, setTabCompletions] = useState<string[]>([]);
  const [tabCompletionIndex, setTabCompletionIndex] = useState(0);
  const [isSearchMode, setIsSearchMode] = useState(false);
  const [searchResults, setSearchResults] = useState<string[]>([]);
  const [searchResultIndex, setSearchResultIndex] = useState(0);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const terminalRef = useRef<HTMLDivElement>(null);
  const MAX_COMMAND_HISTORY = 10;

  // Available commands for tab completion
  const AVAILABLE_COMMANDS = [
    'help',
    'clear',
    'clear-session',
    'echo',
    'date',
    'pwd',
    'cd',
    'ls',
    'cat',
    'touch',
    'mkdir',
    'rm',
    'whoami',
    'version',
    'backend',
    'ping',
    'connect:',
  ];

  // Syntax highlighting for output
  const highlightOutput = (output: string, command: string): React.ReactNode => {
    const trimmedCommand = command.trim().split(/\s+/)[0];

    // For ls command, highlight file types
    if (trimmedCommand === 'ls') {
      return highlightLsOutput(output);
    }

    // For cat command, highlight based on file extension
    if (trimmedCommand === 'cat') {
      const fileMatch = command.match(/cat\s+(.+)/);
      if (fileMatch) {
        const fileName = fileMatch[1].trim();
        return highlightFileContent(output, fileName);
      }
    }

    // Default: return plain text
    return output;
  };

  // Highlight ls output with colors for different file types
  const highlightLsOutput = (output: string): React.ReactNode => {
    const lines = output.split('\n');
    return (
      <>
        {lines.map((line, idx) => {
          // Skip empty lines or header lines
          if (!line.trim() || line.startsWith('total ')) {
            return (
              <span key={`line-${idx}`} className="text-[#cccccc]">
                {line}
                {'\n'}
              </span>
            );
          }

          // For column format, split by chunks of ~20 chars and highlight each item
          // Check if this looks like a column format (multiple items padded)
          const isColumnFormat = line.length > 25 && !line.includes('plc-gbt-user');

          if (isColumnFormat) {
            // Split into 20-char chunks (column width)
            const colWidth = 20;
            const items: string[] = [];
            for (let i = 0; i < line.length; i += colWidth) {
              const item = line.substring(i, i + colWidth);
              if (item.trim()) {
                items.push(item);
              }
            }

            return (
              <span key={`line-${idx}`}>
                {items.map((item, itemIdx) => {
                  const trimmedItem = item.trim();
                  return (
                    <span key={`item-${idx}-${itemIdx}`} className={getFileColor(trimmedItem)}>
                      {item}
                    </span>
                  );
                })}
                {'\n'}
              </span>
            );
          }

          // For long format or single items, highlight the whole line
          const parts = line.split(/\s+/);
          const fileName = parts[parts.length - 1];
          const color = getFileColor(fileName);

          return (
            <span key={`line-${idx}`} className={color}>
              {line}
              {'\n'}
            </span>
          );
        })}
      </>
    );
  };

  // Get color class for a file/folder name
  const getFileColor = (fileName: string): string => {
    // Check if it's a directory (ends with /)
    if (fileName.endsWith('/')) {
      return 'text-[#569cd6] font-semibold';
    }

    // Check file extensions for syntax highlighting
    if (fileName.match(/\.(md|txt|doc)$/i)) {
      return 'text-[#dcdcaa]';
    }

    if (fileName.match(/\.(json|yaml|yml|xml)$/i)) {
      return 'text-[#ce9178]';
    }

    if (fileName.match(/\.(js|ts|tsx|jsx|py|rb|go|rs)$/i)) {
      return 'text-[#4ec9b0]';
    }

    if (fileName.match(/\.(jpg|jpeg|png|gif|svg|ico)$/i)) {
      return 'text-[#c586c0]';
    }

    // Default color for other files (white)
    return 'text-[#cccccc]';
  };

  // Highlight file content based on file type
  const highlightFileContent = (content: string, fileName: string): React.ReactNode => {
    // For now, return plain content
    // Future: Add syntax highlighting for code files
    return content;
  };

  // Auto-scroll to bottom when new output is added
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [history]);

  // Focus input on mount and restore current directory
  useEffect(() => {
    inputRef.current?.focus();

    // Restore current directory from saved session
    try {
      const savedSession = localStorage.getItem('plc-gbt-terminal-session');
      if (savedSession) {
        const session = JSON.parse(savedSession);
        if (session.currentDirectory) {
          setCurrentDirectory(session.currentDirectory);
        }
      }
    } catch (error) {
      console.warn('Failed to restore current directory:', error);
    }
  }, [setCurrentDirectory]);

  // Save terminal session to localStorage whenever it changes
  useEffect(() => {
    try {
      const session = {
        commandHistory,
        currentDirectory,
        history: history.slice(-20), // Save last 20 entries only
        savedAt: new Date().toISOString(),
      };
      localStorage.setItem('plc-gbt-terminal-session', JSON.stringify(session));
    } catch (error) {
      console.warn('Failed to save terminal session:', error);
    }
  }, [commandHistory, currentDirectory, history]);

  // Get tab completion suggestions
  const getTabCompletions = async (input: string): Promise<string[]> => {
    const parts = input.trim().split(/\s+/);

    // If empty or just starting, suggest commands
    if (parts.length === 0 || input.trim() === '') {
      return AVAILABLE_COMMANDS;
    }

    const firstPart = parts[0];

    // If only one word and no space after, complete command name
    if (parts.length === 1 && !input.endsWith(' ')) {
      return AVAILABLE_COMMANDS.filter(cmd => cmd.startsWith(firstPart));
    }

    // For commands that take file/folder arguments, complete paths
    const pathCommands = ['cd', 'ls', 'cat', 'rm', 'touch', 'mkdir'];
    if (pathCommands.includes(firstPart)) {
      const lastPart = parts[parts.length - 1];

      // Fetch files/folders from current directory
      try {
        const response = await fetch('http://localhost:8000/api/v1/files');
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.data && data.data.files) {
            // Navigate to current directory in the tree
            const findDirectory = (nodes: any[], targetPath: string): any => {
              if (targetPath === '/WHK01' || targetPath === '/') {
                return nodes[0]; // WHK01 root
              }
              const searchPath = targetPath.replace(/^\/WHK01/, '');
              const segments = searchPath.split('/').filter(s => s);
              let current: any = nodes[0];
              for (const segment of segments) {
                if (!current || !current.children) return null;
                current = current.children.find(
                  (child: any) => child.name === segment && child.type === 'folder'
                );
                if (!current) return null;
              }
              return current;
            };

            const currentDir = findDirectory(data.data.files, currentDirectory);
            if (currentDir && currentDir.children) {
              // Get all file/folder names in current directory
              const names = currentDir.children.map((item: any) => item.name);

              // Filter by what user has typed
              if (lastPart && lastPart !== firstPart) {
                return names.filter((name: string) => name.startsWith(lastPart));
              }
              return names;
            }
          }
        }
      } catch (error) {
        console.warn('Tab completion: Failed to fetch files', error);
      }
    }

    return [];
  };

  // Search command history
  const searchCommandHistory = (query: string): string[] => {
    if (!query) return commandHistory;
    return commandHistory.filter(cmd => cmd.toLowerCase().includes(query.toLowerCase()));
  };

  const handleSearchMode = () => {
    if (!isSearchMode) {
      // Enter search mode
      setIsSearchMode(true);
      setSearchResults(commandHistory);
      setSearchResultIndex(commandHistory.length - 1);
      if (commandHistory.length > 0) {
        setCurrentInput(commandHistory[commandHistory.length - 1]);
      }
    } else {
      // Cycle to next match (backwards in time)
      if (searchResults.length > 0) {
        const nextIndex = searchResultIndex > 0 ? searchResultIndex - 1 : searchResults.length - 1;
        setSearchResultIndex(nextIndex);
        setCurrentInput(searchResults[nextIndex]);
      }
    }
  };

  const exitSearchMode = () => {
    setIsSearchMode(false);
    setSearchResults([]);
    setSearchResultIndex(0);
  };

  const handleInputChange = (value: string) => {
    setCurrentInput(value);

    if (isSearchMode) {
      // Update search results as user types
      const results = searchCommandHistory(value);
      setSearchResults(results);
      if (results.length > 0) {
        setSearchResultIndex(results.length - 1);
      }
    }
  };

  const handleTabCompletion = async () => {
    const completions = await getTabCompletions(currentInput);

    if (completions.length === 0) {
      // No completions available
      return;
    }

    if (completions.length === 1) {
      // Single completion - auto-complete
      const parts = currentInput.trim().split(/\s+/);
      if (parts.length === 1 && !currentInput.endsWith(' ')) {
        // Completing command name
        setCurrentInput(completions[0] + ' ');
      } else {
        // Completing file/folder name
        const lastSpaceIndex = currentInput.lastIndexOf(' ');
        const prefix = currentInput.substring(0, lastSpaceIndex + 1);
        setCurrentInput(prefix + completions[0]);
      }
      setTabCompletions([]);
      setTabCompletionIndex(0);
    } else {
      // Multiple completions - cycle through them
      if (
        tabCompletions.length === 0 ||
        JSON.stringify(tabCompletions) !== JSON.stringify(completions)
      ) {
        // First tab or different completions
        setTabCompletions(completions);
        setTabCompletionIndex(0);

        // Show available completions in output
        setHistory(prev => [
          ...prev,
          {
            command: '',
            output: `Possible completions:\n${completions.join('  ')}`,
            timestamp: new Date(),
            status: 'info',
          },
        ]);
      } else {
        // Cycle to next completion
        const nextIndex = (tabCompletionIndex + 1) % completions.length;
        setTabCompletionIndex(nextIndex);

        // Apply the completion
        const parts = currentInput.trim().split(/\s+/);
        if (parts.length === 1 && !currentInput.endsWith(' ')) {
          setCurrentInput(completions[nextIndex] + ' ');
        } else {
          const lastSpaceIndex = currentInput.lastIndexOf(' ');
          const prefix = currentInput.substring(0, lastSpaceIndex + 1);
          setCurrentInput(prefix + completions[nextIndex]);
        }
      }
    }
  };

  const executeCommand = async (command: string) => {
    const trimmedCommand = command.trim();

    if (!trimmedCommand) {
      return;
    }

    // Show waiting cursor (blinking box)
    setIsWaitingForOutput(true);

    // Add to command history (FIFO - max 10 commands)
    setCommandHistory(prev => {
      const newHistory = [...prev, trimmedCommand];
      // Keep only last 10 commands
      if (newHistory.length > MAX_COMMAND_HISTORY) {
        return newHistory.slice(-MAX_COMMAND_HISTORY);
      }
      return newHistory;
    });
    setHistoryIndex(-1);

    let output = '';
    let status: 'success' | 'error' | 'info' = 'success';

    try {
      // Built-in commands
      if (trimmedCommand === 'help') {
        output = `Available commands:
  help              - Show this help message
  clear             - Clear the terminal
  clear-session     - Clear saved terminal session from storage
  echo <text>       - Echo text to the terminal
  date              - Show current date and time
  pwd               - Show current working directory
  cd <path>         - Change directory (default: /WHK01)
  ls [options] [path] - List directory contents
    -l              Long format (permissions, size, date)
    -a              Show all files (including hidden)
    -A              Show hidden files (excluding . and ..)
  cat <file>        - Display file contents
  touch <file>      - Create a new empty file
  mkdir <dir>       - Create a new directory
  rm [-r] <path>    - Remove file or directory (-r for recursive)
  whoami            - Show current user
  version           - Show PLC-GBT version
  backend           - Check backend API status
  ping <host>       - Ping a host (supports -c, -i, -t options)
  connect:<type>    - Database/terminal connection tool
  connect:?         - Show connection help and syntax
  
Keyboard Shortcuts:
  Tab               - Auto-complete commands and file/folder names
  Ctrl+R            - Search command history (press again to cycle matches)
  Ctrl+C            - Stop/interrupt running command or exit search
  Ctrl+L            - Clear terminal screen
  Escape            - Exit search mode
  Shift+Enter       - Multi-line input (new line)
  Enter             - Execute command
  Arrow Up (↑)      - Cycle through command history (newest → oldest)
  Arrow Down (↓)    - Cycle through command history (oldest → newest)
  
Navigation:
  - Command history stores last 10 commands
  - History cycles continuously (wraps around)
  - Cursor changes to box (▯) while waiting for output`;
        status = 'info';
      } else if (trimmedCommand === 'clear') {
        setHistory([]);
        setCurrentInput('');
        return;
      } else if (trimmedCommand === 'clear-session') {
        // Clear saved session from localStorage
        try {
          localStorage.removeItem('plc-gbt-terminal-session');
          output = 'Terminal session cleared from storage';
          status = 'success';
          setHistory([]);
          setCommandHistory([]);
          setCurrentDirectory('/WHK01');
        } catch (error) {
          output = 'Failed to clear terminal session';
          status = 'error';
        }
      } else if (trimmedCommand.startsWith('echo ')) {
        output = trimmedCommand.substring(5);
        status = 'success';
      } else if (trimmedCommand === 'date') {
        output = new Date().toString();
        status = 'success';
      } else if (trimmedCommand === 'pwd') {
        output = currentDirectory;
        status = 'success';
      } else if (trimmedCommand.startsWith('cd')) {
        const parts = trimmedCommand.split(/\s+/);
        const targetPath = parts[1] || '/WHK01';

        // Normalize path
        let newPath = targetPath;
        if (!newPath.startsWith('/')) {
          newPath = currentDirectory === '/' ? `/${newPath}` : `${currentDirectory}/${newPath}`;
        }

        // Handle '..' for parent directory
        if (newPath.includes('..')) {
          const pathParts = newPath.split('/').filter(p => p);
          const resolvedParts: string[] = [];
          for (const part of pathParts) {
            if (part === '..') {
              resolvedParts.pop();
            } else if (part !== '.') {
              resolvedParts.push(part);
            }
          }
          newPath = '/' + resolvedParts.join('/');
        }

        // Verify directory exists via backend
        try {
          const response = await fetch('http://localhost:8000/api/v1/files');
          if (response.ok) {
            const data = await response.json();

            // Function to find directory in tree
            const findDirectory = (nodes: any[], targetPath: string): any => {
              // Special case: /WHK01 or / refers to root
              if (targetPath === '/WHK01' || targetPath === '/') {
                return nodes[0]; // WHK01 root is first node
              }

              // Remove /WHK01 prefix if present
              const searchPath = targetPath.replace(/^\/WHK01/, '');

              // Split path into segments
              const segments = searchPath.split('/').filter(s => s);

              // Navigate through tree
              let current: any = nodes[0]; // Start at WHK01 root

              for (const segment of segments) {
                if (!current || !current.children) {
                  return null;
                }

                current = current.children.find(
                  (child: any) => child.name === segment && child.type === 'folder'
                );

                if (!current) {
                  return null;
                }
              }

              return current;
            };

            const directory = findDirectory(data.data.files, newPath);

            if (!directory) {
              output = `cd: ${targetPath}: No such file or directory`;
              status = 'error';
            } else {
              setCurrentDirectory(newPath || '/WHK01');
              output = `Changed directory to: ${newPath || '/WHK01'}`;
              status = 'success';
            }
          } else {
            output = `cd: Unable to verify directory`;
            status = 'error';
          }
        } catch {
          output = `cd: ${targetPath}: Directory verification failed`;
          status = 'error';
        }
      } else if (trimmedCommand.startsWith('ls')) {
        const parts = trimmedCommand.split(/\s+/);
        let targetPath = currentDirectory;
        let longFormat = false;

        // Parse ls flags and path
        for (let i = 1; i < parts.length; i++) {
          if (parts[i].startsWith('-')) {
            const flags = parts[i].substring(1);
            if (flags.includes('l')) longFormat = true;
            // Note: -a and -A flags parsed but not yet implemented
          } else {
            // This is a path argument
            targetPath = parts[i];
          }
        }

        // Normalize path
        if (!targetPath.startsWith('/')) {
          targetPath =
            currentDirectory === '/' ? `/${targetPath}` : `${currentDirectory}/${targetPath}`;
        }

        try {
          const response = await fetch('http://localhost:8000/api/v1/files');
          if (response.ok) {
            const data = await response.json();

            // Find directory by building the path from root
            const findDirectory = (nodes: any[], targetPath: string): any => {
              // Special case: /WHK01 or / refers to root
              if (targetPath === '/WHK01' || targetPath === '/') {
                return nodes[0]; // WHK01 root is first node
              }

              // Remove /WHK01 prefix if present
              const searchPath = targetPath.replace(/^\/WHK01/, '');

              // Split path into segments
              const segments = searchPath.split('/').filter(s => s);

              // Navigate through tree
              let current: any = nodes[0]; // Start at WHK01 root

              for (const segment of segments) {
                if (!current || !current.children) {
                  return null;
                }

                current = current.children.find(
                  (child: any) => child.name === segment && child.type === 'folder'
                );

                if (!current) {
                  return null;
                }
              }

              return current;
            };

            const directory = findDirectory(data.data.files, targetPath);

            if (!directory) {
              output = `ls: cannot access '${targetPath}': No such file or directory`;
              status = 'error';
            } else {
              const items = directory.children || [];

              if (items.length === 0) {
                output = `(empty directory)`;
                status = 'info';
              } else {
                if (longFormat) {
                  // Long format: permissions, size, date, name
                  const lines: string[] = [];
                  lines.push(`total ${items.length}`);

                  for (const item of items) {
                    const type = item.type === 'folder' ? 'd' : '-';
                    const perms = item.isImmutable ? 'r--r--r--' : 'rw-r--r--';
                    const size = item.size || 0;
                    const date = item.modified
                      ? new Date(item.modified).toLocaleDateString()
                      : new Date().toLocaleDateString();
                    const name = item.type === 'folder' ? `${item.name}/` : item.name;

                    lines.push(
                      `${type}${perms}  1 plc-gbt-user  plc-gbt  ${size
                        .toString()
                        .padStart(8)} ${date} ${name}`
                    );
                  }

                  output = lines.join('\n');
                } else {
                  // Simple format: just names in columns
                  const names = items.map((item: any) =>
                    item.type === 'folder' ? `${item.name}/` : item.name
                  );

                  // Display in columns (4 columns)
                  const colWidth = 20;
                  const cols = 4;
                  const rows = Math.ceil(names.length / cols);
                  const lines: string[] = [];

                  for (let row = 0; row < rows; row++) {
                    const rowItems: string[] = [];
                    for (let col = 0; col < cols; col++) {
                      const idx = row + col * rows;
                      if (idx < names.length) {
                        rowItems.push(names[idx].padEnd(colWidth));
                      }
                    }
                    lines.push(rowItems.join(''));
                  }

                  output = lines.join('\n');
                }
                status = 'success';
              }
            }
          } else {
            output = `ls: Unable to access file system`;
            status = 'error';
          }
        } catch (error) {
          output = `ls: ${error instanceof Error ? error.message : 'Failed to list directory'}`;
          status = 'error';
        }
      } else if (trimmedCommand.startsWith('cat')) {
        // Read file contents
        const parts = trimmedCommand.split(/\s+/);
        const filePath = parts[1];

        if (!filePath) {
          output = 'cat: missing file operand\nUsage: cat <file>';
          status = 'error';
        } else {
          try {
            // Normalize path
            let fullPath = filePath;
            if (!fullPath.startsWith('/')) {
              fullPath =
                currentDirectory === '/' ? `/${fullPath}` : `${currentDirectory}/${fullPath}`;
            }

            const response = await fetch(
              `http://localhost:8000/api/v1/files/content?path=${encodeURIComponent(fullPath)}`
            );

            if (response.ok) {
              const data = await response.json();
              if (data.success && data.data && data.data.content !== undefined) {
                output = data.data.content || ''; // Empty string is valid for empty files
                status = 'success';
              } else {
                output = `cat: ${filePath}: Unable to read file`;
                status = 'error';
              }
            } else if (response.status === 404) {
              output = `cat: ${filePath}: No such file or directory`;
              status = 'error';
            } else {
              output = `cat: ${filePath}: Error reading file (HTTP ${response.status})`;
              status = 'error';
            }
          } catch (error) {
            output = `cat: ${error instanceof Error ? error.message : 'Failed to read file'}`;
            status = 'error';
          }
        }
      } else if (trimmedCommand.startsWith('touch')) {
        // Create new file
        const parts = trimmedCommand.split(/\s+/);
        const fileName = parts[1];

        if (!fileName) {
          output = 'touch: missing file operand\nUsage: touch <file>';
          status = 'error';
        } else {
          try {
            // Normalize path
            let fullPath = fileName;
            if (!fullPath.startsWith('/')) {
              fullPath =
                currentDirectory === '/' ? `/${fullPath}` : `${currentDirectory}/${fullPath}`;
            }

            // Remove /WHK01 prefix if present (backend expects relative paths)
            const normalizedPath = fullPath.replace(/^\/WHK01/, '');

            // Determine folder from path
            const pathParts = normalizedPath.split('/').filter(p => p);
            const fileNameOnly = pathParts.pop() || fileName;
            const parentPath = pathParts.length > 0 ? '/' + pathParts.join('/') : '/';

            const response = await fetch('http://localhost:8000/api/v1/files', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                name: fileNameOnly,
                type: 'file',
                content: '',
                parentPath: parentPath,
              }),
            });

            if (response.ok) {
              output = `Created file: ${fileName}`;
              status = 'success';

              // Trigger file explorer refresh
              window.dispatchEvent(
                new CustomEvent('fileSystemChange', {
                  detail: { operation: 'touch', path: fileName },
                })
              );
            } else {
              const errorData = await response.json();
              output = `touch: ${fileName}: ${errorData.message || 'Failed to create file'}`;
              status = 'error';
            }
          } catch (error) {
            output = `touch: ${error instanceof Error ? error.message : 'Failed to create file'}`;
            status = 'error';
          }
        }
      } else if (trimmedCommand.startsWith('mkdir')) {
        // Create new directory
        const parts = trimmedCommand.split(/\s+/);
        const dirName = parts[1];

        if (!dirName) {
          output = 'mkdir: missing operand\nUsage: mkdir <directory>';
          status = 'error';
        } else {
          try {
            // Normalize path
            let fullPath = dirName;
            if (!fullPath.startsWith('/')) {
              fullPath =
                currentDirectory === '/' ? `/${fullPath}` : `${currentDirectory}/${fullPath}`;
            }

            // Remove /WHK01 prefix if present (backend expects relative paths)
            const normalizedPath = fullPath.replace(/^\/WHK01/, '');

            // Determine parent folder and directory name
            const pathParts = normalizedPath.split('/').filter(p => p);
            const dirNameOnly = pathParts.pop() || dirName;
            const parentPath = pathParts.length > 0 ? '/' + pathParts.join('/') : '/';

            const response = await fetch('http://localhost:8000/api/v1/files', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                name: dirNameOnly,
                type: 'folder',
                parentPath: parentPath,
              }),
            });

            if (response.ok) {
              output = `Created directory: ${dirName}`;
              status = 'success';

              // Trigger file explorer refresh
              window.dispatchEvent(
                new CustomEvent('fileSystemChange', {
                  detail: { operation: 'mkdir', path: dirName },
                })
              );
            } else {
              const errorData = await response.json();
              output = `mkdir: ${dirName}: ${errorData.message || 'Failed to create directory'}`;
              status = 'error';
            }
          } catch (error) {
            output = `mkdir: ${
              error instanceof Error ? error.message : 'Failed to create directory'
            }`;
            status = 'error';
          }
        }
      } else if (trimmedCommand.startsWith('rm')) {
        // Delete file or directory
        const parts = trimmedCommand.split(/\s+/);
        let recursive = false;
        let targetPath = '';

        // Parse flags
        for (let i = 1; i < parts.length; i++) {
          if (parts[i] === '-r' || parts[i] === '-rf') {
            recursive = true;
          } else if (!parts[i].startsWith('-')) {
            targetPath = parts[i];
          }
        }

        if (!targetPath) {
          output = 'rm: missing operand\nUsage: rm [-r] <file|directory>';
          status = 'error';
        } else {
          try {
            // Normalize path
            let fullPath = targetPath;
            if (!fullPath.startsWith('/')) {
              fullPath =
                currentDirectory === '/' ? `/${fullPath}` : `${currentDirectory}/${fullPath}`;
            }

            // First, check if it's a file or folder
            const filesResponse = await fetch('http://localhost:8000/api/v1/files');
            if (!filesResponse.ok) {
              output = `rm: Unable to access file system`;
              status = 'error';
            } else {
              const filesData = await filesResponse.json();

              // Find item by navigating the tree structure
              const findItem = (nodes: any[], targetPath: string): any => {
                // Remove /WHK01 prefix if present
                const searchPath = targetPath.replace(/^\/WHK01/, '');

                // Split path into segments
                const segments = searchPath.split('/').filter(s => s);

                if (segments.length === 0) {
                  return null; // Can't delete root
                }

                // Navigate through tree
                let current: any = nodes[0]; // Start at WHK01 root

                for (let i = 0; i < segments.length; i++) {
                  const segment = segments[i];

                  if (!current || !current.children) {
                    return null;
                  }

                  // Last segment: find file or folder
                  if (i === segments.length - 1) {
                    return current.children.find((child: any) => child.name === segment);
                  }

                  // Intermediate segments: must be folders
                  current = current.children.find(
                    (child: any) => child.name === segment && child.type === 'folder'
                  );

                  if (!current) {
                    return null;
                  }
                }

                return null;
              };

              const item = findItem(filesData.data.files, fullPath);

              if (!item) {
                output = `rm: cannot remove '${targetPath}': No such file or directory`;
                status = 'error';
              } else if (item.isImmutable) {
                output = `rm: cannot remove '${targetPath}': Permission denied (immutable system file)`;
                status = 'error';
              } else if (item.type === 'folder' && !recursive) {
                output = `rm: cannot remove '${targetPath}': Is a directory (use -r for recursive delete)`;
                status = 'error';
              } else {
                // Perform delete
                const deleteResponse = await fetch(
                  `http://localhost:8000/api/v1/files/${item.id}`,
                  {
                    method: 'DELETE',
                  }
                );

                if (deleteResponse.ok) {
                  output = `Removed: ${targetPath}`;
                  status = 'success';

                  // Trigger file explorer refresh
                  window.dispatchEvent(
                    new CustomEvent('fileSystemChange', {
                      detail: { operation: 'rm', path: targetPath },
                    })
                  );
                } else {
                  const errorData = await deleteResponse.json();
                  output = `rm: ${targetPath}: ${errorData.message || 'Failed to remove'}`;
                  status = 'error';
                }
              }
            }
          } catch (error) {
            output = `rm: ${error instanceof Error ? error.message : 'Failed to remove'}`;
            status = 'error';
          }
        }
      } else if (trimmedCommand === 'whoami') {
        output = 'plc-gbt-user';
        status = 'success';
      } else if (trimmedCommand === 'version') {
        output = 'PLC-GBT v1.0.0\nNext.js 15.4.2\nReact 18.3.1';
        status = 'success';
      } else if (trimmedCommand === 'backend') {
        // Check backend API status
        try {
          const response = await fetch('http://localhost:8000/api/v1/health');
          if (response.ok) {
            const data = await response.json();
            output = `Backend API Status: ${data.status}\nAPI Version: ${
              data.version || 'N/A'
            }\nEndpoint: http://localhost:8000`;
            status = 'success';
          } else {
            output = `Backend API Error: HTTP ${response.status}`;
            status = 'error';
          }
        } catch (error) {
          output = `Backend API Error: ${
            error instanceof Error ? error.message : 'Connection failed'
          }`;
          status = 'error';
        }
      } else if (trimmedCommand.startsWith('ping')) {
        const parts = trimmedCommand.split(/\s+/);

        // Parse command line arguments
        let count = 4; // Default to 4 pings
        let interval = 1;
        let targetHost = '';

        // Find the host (non-option argument)
        for (let idx = 1; idx < parts.length; idx++) {
          const arg = parts[idx];
          if (arg === '-c' && parts[idx + 1]) {
            count = parseInt(parts[idx + 1], 10);
            idx++;
          } else if (arg === '-i' && parts[idx + 1]) {
            interval = parseFloat(parts[idx + 1]);
            idx++;
          } else if (arg === '-t' && parts[idx + 1]) {
            // TTL option - parse but don't use in simulation
            idx++;
          } else if (!arg.startsWith('-')) {
            targetHost = arg;
          }
        }

        if (!targetHost) {
          output = `ping: usage: ping [-c count] [-i interval] [-t ttl] <host>
  -c count    Stop after sending count packets (default: 4)
  -i interval Wait interval seconds between packets (default: 1)
  -t ttl      Set Time To Live
  
Examples:
  ping 10.4.8.15
  ping -c 10 google.com
  ping -c 4 -i 2 192.168.1.1`;
          status = 'info';
        } else {
          // Clear input immediately
          setCurrentInput('');

          // Add command to output immediately (without output yet)
          setHistory(prev => [
            ...prev,
            {
              command: trimmedCommand,
              output: '', // Will be updated later
              timestamp: new Date(),
              status: 'info',
              directory: currentDirectory,
            },
          ]);

          // Keep waiting cursor active (already set by executeCommand)
          // setIsWaitingForOutput(true); // Already set at start of executeCommand
          setIsRunningCommand(true);
          let pingCount = 0;
          let stopped = false;

          const abortPing = () => {
            stopped = true;
            setIsRunningCommand(false);
            setRunningCommandAbort(null);
            setIsWaitingForOutput(false);
          };

          setRunningCommandAbort(() => abortPing);

          // Check if host is reachable (simulate by checking IP format or known hosts)
          const isValidIP = /^(\d{1,3}\.){3}\d{1,3}$/.test(targetHost);
          const isLocalhost = targetHost === 'localhost' || targetHost === '127.0.0.1';

          // Simulate unreachable hosts (private ranges that might be offline)
          const isUnreachable =
            isValidIP &&
            (targetHost.startsWith('10.') ||
              targetHost.startsWith('192.168.') ||
              targetHost.startsWith('172.')) &&
            Math.random() > 0.5; // 50% chance to be unreachable for private IPs

          const pingOutput: string[] = [`PING ${targetHost} (${targetHost}): 56 data bytes`];

          const doPing = async () => {
            // Small delay to ensure state updates are rendered
            await new Promise(resolve => setTimeout(resolve, 50));

            if (isUnreachable) {
              // Simulate unreachable host
              for (let i = 0; i < 3 && !stopped; i++) {
                pingOutput.push(`Request timeout for icmp_seq ${i + 1}`);
                await new Promise(resolve => setTimeout(resolve, interval * 1000));
              }
              pingOutput.push(`\nDestination Host Unreachable`);
              pingOutput.push(`\n--- ${targetHost} ping statistics ---`);
              pingOutput.push(`3 packets transmitted, 0 packets received, 100.0% packet loss`);

              output = pingOutput.join('\n');
              status = 'error';
            } else {
              // Successful ping
              let successCount = 0;
              while (!stopped && pingCount < count) {
                pingCount++;
                successCount++;
                const time = (Math.random() * 50 + 10).toFixed(3);
                const ttl = isLocalhost ? 64 : Math.floor(Math.random() * 10) + 50;
                pingOutput.push(
                  `64 bytes from ${targetHost}: icmp_seq=${pingCount} ttl=${ttl} time=${time} ms`
                );

                if (pingCount < count) {
                  await new Promise(resolve => setTimeout(resolve, interval * 1000));
                }
              }

              if (stopped) {
                pingOutput.push('');
              }

              pingOutput.push(`\n--- ${targetHost} ping statistics ---`);
              const loss = stopped ? Math.round(((pingCount - successCount) / pingCount) * 100) : 0;
              pingOutput.push(
                `${pingCount} packets transmitted, ${successCount} packets received, ${loss}% packet loss`
              );

              if (successCount > 0) {
                const avgTime = (Math.random() * 20 + 20).toFixed(3);
                const minTime = (parseFloat(avgTime) - 10).toFixed(3);
                const maxTime = (parseFloat(avgTime) + 15).toFixed(3);
                pingOutput.push(`round-trip min/avg/max = ${minTime}/${avgTime}/${maxTime} ms`);
              }

              output = pingOutput.join('\n');
              status = 'success';
            }

            setIsRunningCommand(false);
            setRunningCommandAbort(null);
            setIsWaitingForOutput(false); // Stop waiting cursor

            // Update the last history entry with output
            setHistory(prev => {
              const newHistory = [...prev];
              if (newHistory.length > 0) {
                newHistory[newHistory.length - 1] = {
                  command: trimmedCommand,
                  output,
                  timestamp: new Date(),
                  status,
                  directory: currentDirectory,
                };
              }
              return newHistory;
            });
          };

          doPing();
          return; // Don't add to history again
        }
      } else if (trimmedCommand.startsWith('connect:')) {
        const input = trimmedCommand.substring(8).trim();

        if (input === '?' || input === '' || input === 'help') {
          output = `Connection Tool - Usage:

Syntax:
  connect:type://user:pass@host:port/database

Connection Types:
  postgresql://  - PostgreSQL database
  mysql://       - MySQL database
  mongodb://     - MongoDB database
  redis://       - Redis cache
  ssh://         - SSH terminal connection
  telnet://      - Telnet connection

Examples:
  connect:postgresql://plc-user:password@localhost:5433/plc_automation_db
  connect:mysql://root:password@192.168.1.10:3306/industrial_db
  connect:ssh://admin@192.168.1.100:22
  connect:redis://localhost:6379

Options:
  ?              - Show this help
  disconnect     - Close current connection
  status         - Show connection status

Note: For security, use environment variables for credentials.`;
          status = 'info';
        } else if (input === 'disconnect') {
          output = 'No active connection to disconnect.';
          status = 'info';
        } else if (input === 'status') {
          output = 'Connection status: Not connected';
          status = 'info';
        } else if (input.includes('://')) {
          // Parse connection string
          try {
            const url = new URL(input);
            const protocol = url.protocol.replace(':', '');
            const host = url.hostname;
            const port = url.port;
            const database = url.pathname.replace('/', '');
            const username = url.username;

            // Build connection attempt message
            let connectionDetails = `Protocol: ${protocol}\n`;
            connectionDetails += `Host: ${host}\n`;
            if (port) connectionDetails += `Port: ${port}\n`;
            if (username) connectionDetails += `Username: ${username}\n`;
            if (database) connectionDetails += `Database: ${database}\n`;

            output = `Attempting to connect to ${protocol}://${host}${
              port ? ':' + port : ''
            }...\n\n${connectionDetails}\n⚠️  Connection functionality will be implemented with backend integration.\n✓  Connection string parsed successfully.`;
            status = 'info';
          } catch (error) {
            output = `Invalid connection string format. Type 'connect:?' for help.\n\nError: ${
              error instanceof Error ? error.message : 'Unknown error'
            }`;
            status = 'error';
          }
        } else {
          output = `Invalid connection syntax. Type 'connect:?' for help.`;
          status = 'error';
        }
      } else {
        output = `Command not found: ${trimmedCommand}\nType "help" for available commands.`;
        status = 'error';
      }
    } catch (error) {
      output = `Error: ${error instanceof Error ? error.message : 'Unknown error'}`;
      status = 'error';
    }

    // Add command and output to history
    setHistory(prev => [
      ...prev,
      {
        command: trimmedCommand,
        output,
        timestamp: new Date(),
        status,
        directory: currentDirectory,
      },
    ]);

    // Stop waiting cursor
    setIsWaitingForOutput(false);

    // Clear input
    setCurrentInput('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl+R: Search command history
    if (e.key === 'r' && e.ctrlKey) {
      e.preventDefault();
      handleSearchMode();
      return;
    }

    // Escape: Exit search mode
    if (e.key === 'Escape' && isSearchMode) {
      e.preventDefault();
      exitSearchMode();
      return;
    }

    // Tab: Auto-completion (not in search mode)
    if (e.key === 'Tab' && !isSearchMode) {
      e.preventDefault();
      handleTabCompletion();
      return;
    }

    // Reset tab completions on any other key
    if (e.key !== 'Tab' && tabCompletions.length > 0) {
      setTabCompletions([]);
      setTabCompletionIndex(0);
    }

    // Ctrl+C: Stop running command or exit search mode
    if (e.key === 'c' && e.ctrlKey) {
      e.preventDefault();
      if (isSearchMode) {
        exitSearchMode();
        setCurrentInput('');
      } else if (isRunningCommand && runningCommandAbort) {
        runningCommandAbort();
        setHistory(prev => [
          ...prev,
          {
            command: '',
            output: '^C (Interrupted)',
            timestamp: new Date(),
            status: 'info',
          },
        ]);
        setCurrentInput('');
      }
      return;
    }

    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent newline in textarea
      if (isSearchMode) {
        exitSearchMode();
      }
      executeCommand(currentInput);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (commandHistory.length > 0) {
        // Cycle through last 10 commands, starting with most recent
        // Up arrow: go backwards in time (newer to older)
        let newIndex: number;
        if (historyIndex === -1) {
          // Start from most recent command
          newIndex = commandHistory.length - 1;
        } else if (historyIndex === 0) {
          // Wrap around to newest command
          newIndex = commandHistory.length - 1;
        } else {
          // Go to previous (older) command
          newIndex = historyIndex - 1;
        }
        setHistoryIndex(newIndex);
        setCurrentInput(commandHistory[newIndex] || '');
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (commandHistory.length > 0) {
        // Down arrow: go forwards in time (older to newer)
        let newIndex: number;
        if (historyIndex === -1) {
          // Start from oldest command
          newIndex = 0;
        } else if (historyIndex === commandHistory.length - 1) {
          // Wrap around to oldest command
          newIndex = 0;
        } else {
          // Go to next (newer) command
          newIndex = historyIndex + 1;
        }
        setHistoryIndex(newIndex);
        setCurrentInput(commandHistory[newIndex] || '');
      }
    } else if (e.key === 'l' && e.ctrlKey) {
      // Ctrl+L - clear terminal
      e.preventDefault();
      setHistory([]);
    }
  };

  const handleTerminalClick = () => {
    inputRef.current?.focus();
  };

  const getStatusColor = (status: CommandHistory['status']) => {
    switch (status) {
      case 'success':
        return 'text-[#4ec9b0]';
      case 'error':
        return 'text-[#f48771]';
      case 'info':
        return 'text-[#569cd6]';
      default:
        return 'text-[#cccccc]';
    }
  };

  return (
    <div
      onClick={handleTerminalClick}
      className={cn(
        'h-full w-full bg-[#0c0c0c] flex flex-col font-mono text-sm text-[#cccccc] cursor-text',
        className
      )}
    >
      {/* Scrollable Command History */}
      <div ref={terminalRef} className="flex-1 overflow-y-auto p-4 pb-2">
        {history.map((entry, index) => (
          <div key={index} className="mb-2">
            {entry.command && (
              <div className="flex items-start">
                <span className="text-[#4ec9b0] mr-2 flex-shrink-0">
                  ./
                  {entry.directory?.split('/').pop() ||
                    entry.directory ||
                    currentDirectory.split('/').pop()}
                  $
                </span>
                <span className="text-white break-words">{entry.command}</span>
              </div>
            )}
            {entry.output && (
              <div
                className={cn(
                  'whitespace-pre-wrap ml-0 mt-1 break-words',
                  getStatusColor(entry.status)
                )}
              >
                {entry.status === 'success' && entry.command
                  ? highlightOutput(entry.output, entry.command)
                  : entry.output}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Fixed Input Line at Bottom - Reduced height by 50% */}
      <div className="flex-shrink-0 border-t border-[#1e1e1e] px-4 py-1">
        {/* Search mode indicator */}
        {isSearchMode && (
          <div className="text-[#569cd6] text-xs mb-1">
            (reverse-i-search)
            {searchResults.length > 0
              ? `: ${searchResultIndex + 1}/${searchResults.length} matches`
              : ': no matches'}
          </div>
        )}
        <div className="flex items-center">
          <span className="text-[#4ec9b0] mr-2 flex-shrink-0">
            {isSearchMode
              ? '(search)'
              : `./${currentDirectory.split('/').pop() || currentDirectory}$`}
          </span>
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={currentInput}
              onChange={e => handleInputChange(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              className="w-full bg-transparent text-white resize-none overflow-hidden p-0 m-0"
              style={{
                minHeight: '0.625rem',
                maxHeight: '5rem',
                lineHeight: '0.625rem',
                border: 'none',
                outline: 'none',
                boxShadow: 'none',
              }}
              spellCheck={false}
              autoComplete="off"
              aria-label="Terminal input"
              onInput={e => {
                // Auto-resize textarea based on content
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = `${Math.min(target.scrollHeight, 80)}px`;
              }}
            />
            {/* Cursor: blinking line normally, blinking box when waiting for output */}
            {currentInput.length === 0 && (
              <span
                className={cn(
                  'absolute left-0 top-0 animate-pulse text-white pointer-events-none',
                  isWaitingForOutput ? 'font-bold' : ''
                )}
              >
                {isWaitingForOutput ? '▯' : '|'}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Terminal Component
 *
 * @description Interactive terminal interface for advanced users
 * @specification Implements VS Code-style terminal from main-ui-spec.md
 *
 * @features
 * - Command execution with history
 * - Built-in commands (help, clear, echo, date, etc.)
 * - Backend API integration
 * - Keyboard shortcuts (Ctrl+C, Ctrl+L, Arrow keys)
 * - Command history navigation
 * - Auto-scroll to bottom
 * - Click-to-focus
 *
 * @shortcuts
 * - Enter: Execute command
 * - Ctrl+C: Clear current input
 * - Ctrl+L: Clear terminal
 * - Arrow Up/Down: Navigate command history
 *
 * @commands
 * - help: Show available commands
 * - clear: Clear terminal
 * - echo <text>: Echo text
 * - date: Show current date/time
 * - pwd: Show working directory
 * - whoami: Show current user
 * - version: Show PLC-GBT version
 * - backend: Check backend API status
 */
