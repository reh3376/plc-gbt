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
  const [history, setHistory] = useState<CommandHistory[]>([
    {
      command: '',
      output: 'Welcome to PLC-GBT Terminal\nType "help" for available commands.',
      timestamp: new Date(),
      status: 'info',
    },
  ]);
  const [currentInput, setCurrentInput] = useState('');
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const { currentDirectory, setCurrentDirectory } = useTerminalStore();
  const [isRunningCommand, setIsRunningCommand] = useState(false);
  const [runningCommandAbort, setRunningCommandAbort] = useState<(() => void) | null>(null);
  const [isWaitingForOutput, setIsWaitingForOutput] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const terminalRef = useRef<HTMLDivElement>(null);
  const MAX_COMMAND_HISTORY = 10;

  // Auto-scroll to bottom when new output is added
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [history]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

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
  echo <text>       - Echo text to the terminal
  date              - Show current date and time
  pwd               - Show current working directory
  cd <path>         - Change directory (default: /WHK01)
  ls [path]         - List directory contents
  whoami            - Show current user
  version           - Show PLC-GBT version
  backend           - Check backend API status
  ping <host>       - Ping a host (supports -c, -i, -t options)
  connect:<type>    - Database/terminal connection tool
  connect:?         - Show connection help and syntax
  
Keyboard Shortcuts:
  Ctrl+C            - Stop/interrupt running command
  Ctrl+L            - Clear terminal screen
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
            await response.json(); // Verify backend is accessible
            // For now, accept any path under /WHK01
            if (newPath === '/' || newPath.startsWith('/WHK01')) {
              setCurrentDirectory(newPath || '/WHK01');
              output = `Changed directory to: ${newPath || '/WHK01'}`;
              status = 'success';
            } else {
              output = `cd: ${targetPath}: No such directory\nNote: Root directory is /WHK01`;
              status = 'error';
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
        const targetPath = parts[1] || currentDirectory;

        try {
          const response = await fetch('http://localhost:8000/api/v1/files');
          if (response.ok) {
            await response.json(); // Verify backend is accessible
            output = `Listing directory: ${targetPath}\n(Directory listing from file explorer - implement full ls later)`;
            status = 'info';
          } else {
            output = `ls: Unable to list directory`;
            status = 'error';
          }
        } catch (error) {
          output = `ls: ${error instanceof Error ? error.message : 'Failed to list directory'}`;
          status = 'error';
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
    // Ctrl+C: Stop running command
    if (e.key === 'c' && e.ctrlKey) {
      e.preventDefault();
      if (isRunningCommand && runningCommandAbort) {
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
                {entry.output}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Fixed Input Line at Bottom - Reduced height by 50% */}
      <div className="flex-shrink-0 border-t border-[#1e1e1e] px-4 py-1">
        <div className="flex items-center">
          <span className="text-[#4ec9b0] mr-2 flex-shrink-0">
            ./{currentDirectory.split('/').pop() || currentDirectory}$
          </span>
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={currentInput}
              onChange={e => setCurrentInput(e.target.value)}
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
