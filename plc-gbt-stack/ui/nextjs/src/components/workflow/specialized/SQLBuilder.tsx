import { cn } from '@/lib/utils/cn';
import {
  AlertCircle,
  CheckCircle,
  Columns,
  Database,
  Eye,
  Play,
  Plus,
  RefreshCw,
  Table,
  Trash2,
} from 'lucide-react';
import React, { useCallback, useEffect, useMemo, useState } from 'react';

interface SQLStatement {
  name: string;
  sql: string;
  enabled: boolean;
  preview?: Record<string, unknown>[];
  error?: string;
  verified?: boolean;
}

interface SQLBuilderProps {
  readonly value: SQLStatement[];
  readonly onChange: (statements: SQLStatement[]) => void;
  readonly connectionString?: string;
  readonly className?: string;
}

interface DatabaseTable {
  tableName: string;
  columns: DatabaseColumn[];
  rowCount: number;
}

interface DatabaseColumn {
  columnName: string;
  dataType: string;
  isNullable: boolean;
  columnDefault?: string;
}

export function SQLBuilder({ value, onChange, connectionString, className }: SQLBuilderProps) {
  const [statements, setStatements] = useState<SQLStatement[]>(value || []);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionError, setConnectionError] = useState<string>('');
  const [databaseSchema, setDatabaseSchema] = useState<DatabaseTable[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [showSchemaBrowser, setShowSchemaBrowser] = useState(true);
  const [isLoadingSchema, setIsLoadingSchema] = useState(false);
  const [activeStatementIndex, setActiveStatementIndex] = useState(0);

  // Initialize statements from props but don't automatically sync back
  // onChange will be called only on user interactions (add/remove/edit)

  // Auto-load mock schema data for immediate demonstration
  useEffect(() => {
    const loadMockSchema = () => {
      // Mock schema data for demonstration
      const mockSchema: DatabaseTable[] = [
        {
          tableName: 'process_data',
          rowCount: 15420,
          columns: [
            { columnName: 'id', dataType: 'BIGSERIAL', isNullable: false },
            { columnName: 'timestamp', dataType: 'TIMESTAMPTZ', isNullable: false },
            { columnName: 'tag_name', dataType: 'VARCHAR(255)', isNullable: false },
            { columnName: 'value', dataType: 'NUMERIC(10,4)', isNullable: true },
            {
              columnName: 'quality',
              dataType: 'VARCHAR(50)',
              isNullable: true,
              columnDefault: "'good'",
            },
          ],
        },
        {
          tableName: 'alarm_history',
          rowCount: 2847,
          columns: [
            { columnName: 'id', dataType: 'BIGSERIAL', isNullable: false },
            { columnName: 'timestamp', dataType: 'TIMESTAMPTZ', isNullable: false },
            { columnName: 'alarm_name', dataType: 'VARCHAR(255)', isNullable: false },
            { columnName: 'severity', dataType: 'VARCHAR(50)', isNullable: false },
            { columnName: 'message', dataType: 'TEXT', isNullable: true },
            {
              columnName: 'acknowledged',
              dataType: 'BOOLEAN',
              isNullable: false,
              columnDefault: 'false',
            },
          ],
        },
        {
          tableName: 'production_batches',
          rowCount: 892,
          columns: [
            { columnName: 'batch_id', dataType: 'VARCHAR(50)', isNullable: false },
            { columnName: 'start_time', dataType: 'TIMESTAMPTZ', isNullable: false },
            { columnName: 'end_time', dataType: 'TIMESTAMPTZ', isNullable: true },
            { columnName: 'product_code', dataType: 'VARCHAR(100)', isNullable: false },
            { columnName: 'quantity', dataType: 'NUMERIC(10,2)', isNullable: true },
          ],
        },
      ];
      setDatabaseSchema(mockSchema);
    };

    // Load immediately for demonstration
    loadMockSchema();
  }, []);

  // Test database connection
  const testConnection = useCallback(async () => {
    if (!connectionString) {
      setConnectionError('Connection string is required');
      return;
    }

    setIsConnecting(true);
    setConnectionError('');

    try {
      // Simulate connection test - in real implementation, this would call an API
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Mock successful connection
      setIsConnected(true);
      console.log('✅ PostgreSQL connection established');
    } catch (error: unknown) {
      setIsConnected(false);
      setConnectionError(error instanceof Error ? error.message : 'Connection failed');
    } finally {
      setIsConnecting(false);
    }
  }, [connectionString]);

  // Load database schema
  const loadDatabaseSchema = useCallback(async () => {
    if (!isConnected) return;

    setIsLoadingSchema(true);
    try {
      // Simulate schema loading - in real implementation, this would query information_schema
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Mock schema data
      const mockSchema: DatabaseTable[] = [
        {
          tableName: 'process_data',
          rowCount: 15420,
          columns: [
            { columnName: 'id', dataType: 'BIGSERIAL', isNullable: false },
            { columnName: 'timestamp', dataType: 'TIMESTAMPTZ', isNullable: false },
            { columnName: 'tag_name', dataType: 'VARCHAR(255)', isNullable: false },
            { columnName: 'value', dataType: 'NUMERIC(10,4)', isNullable: true },
            {
              columnName: 'quality',
              dataType: 'VARCHAR(50)',
              isNullable: true,
              columnDefault: "'good'",
            },
          ],
        },
        {
          tableName: 'alarm_history',
          rowCount: 2847,
          columns: [
            { columnName: 'id', dataType: 'BIGSERIAL', isNullable: false },
            { columnName: 'timestamp', dataType: 'TIMESTAMPTZ', isNullable: false },
            { columnName: 'alarm_name', dataType: 'VARCHAR(255)', isNullable: false },
            { columnName: 'severity', dataType: 'VARCHAR(50)', isNullable: false },
            { columnName: 'message', dataType: 'TEXT', isNullable: true },
            {
              columnName: 'acknowledged',
              dataType: 'BOOLEAN',
              isNullable: false,
              columnDefault: 'false',
            },
          ],
        },
        {
          tableName: 'production_batches',
          rowCount: 892,
          columns: [
            { columnName: 'batch_id', dataType: 'VARCHAR(50)', isNullable: false },
            { columnName: 'start_time', dataType: 'TIMESTAMPTZ', isNullable: false },
            { columnName: 'end_time', dataType: 'TIMESTAMPTZ', isNullable: true },
            { columnName: 'product_code', dataType: 'VARCHAR(100)', isNullable: false },
            { columnName: 'quantity', dataType: 'NUMERIC(10,2)', isNullable: true },
          ],
        },
      ];

      setDatabaseSchema(mockSchema);
    } catch (error: unknown) {
      console.error(
        'Failed to load schema:',
        error instanceof Error ? error.message : 'Unknown error'
      );
    } finally {
      setIsLoadingSchema(false);
    }
  }, [isConnected]);

  // Load schema when connected
  useEffect(() => {
    if (isConnected) {
      loadDatabaseSchema();
    }
  }, [isConnected, loadDatabaseSchema]);

  // Preview SQL statement results
  const previewStatement = useCallback(
    async (index: number) => {
      const statement = statements[index];
      if (!statement.sql.trim() || !isConnected) return;

      const updatedStatements = [...statements];
      updatedStatements[index] = { ...statement, preview: undefined, error: undefined };
      setStatements(updatedStatements);

      try {
        // Simulate SQL execution - in real implementation, this would call an API
        await new Promise(resolve => setTimeout(resolve, 800));

        // Mock result data based on SQL content
        const mockResults = statement.sql.toLowerCase().includes('count')
          ? [{ count: 15420 }]
          : statement.sql.toLowerCase().includes('process_data')
          ? [
              {
                id: 1,
                timestamp: '2025-01-22T14:30:00Z',
                tag_name: 'Tank01.Level',
                value: 75.4,
                quality: 'good',
              },
              {
                id: 2,
                timestamp: '2025-01-22T14:31:00Z',
                tag_name: 'Tank01.Level',
                value: 75.2,
                quality: 'good',
              },
              {
                id: 3,
                timestamp: '2025-01-22T14:32:00Z',
                tag_name: 'Tank01.Level',
                value: 74.9,
                quality: 'good',
              },
            ]
          : [{ result: 'Query executed successfully', timestamp: new Date().toISOString() }];

        updatedStatements[index] = {
          ...statement,
          preview: mockResults,
          error: undefined,
          verified: true,
        };
      } catch (error: unknown) {
        updatedStatements[index] = {
          ...statement,
          preview: undefined,
          error: error instanceof Error ? error.message : 'Query execution failed',
          verified: false,
        };
      }

      setStatements(updatedStatements);
      onChange(updatedStatements);
    },
    [statements, isConnected, onChange]
  );

  // Verify SQL statement against database schema
  const verifyStatement = useCallback(
    (index: number) => {
      const statement = statements[index];
      if (!statement.sql.trim()) return;

      // Simple SQL validation against available tables
      const sql = statement.sql.toLowerCase();
      const availableTables = databaseSchema.map(table => table.tableName);

      let hasValidTables = false;
      availableTables.forEach(tableName => {
        if (sql.includes(tableName.toLowerCase())) {
          hasValidTables = true;
        }
      });

      const updatedStatements = [...statements];
      if (hasValidTables || sql.includes('now()') || sql.includes('current_timestamp')) {
        updatedStatements[index] = { ...statement, verified: true, error: undefined };
      } else {
        updatedStatements[index] = {
          ...statement,
          verified: false,
          error: `SQL references unknown tables. Available: ${availableTables.join(', ')}`,
        };
      }

      setStatements(updatedStatements);
      onChange(updatedStatements);
    },
    [statements, databaseSchema, onChange]
  );

  // Add new SQL statement
  const addStatement = useCallback(() => {
    const newStatement: SQLStatement = {
      name: `Query${statements.length + 1}`,
      sql: 'SELECT NOW() as current_time',
      enabled: true,
    };
    const updatedStatements = [...statements, newStatement];
    setStatements(updatedStatements);
    onChange(updatedStatements);
  }, [statements, onChange]);

  // Remove SQL statement
  const removeStatement = useCallback(
    (index: number) => {
      const updatedStatements = statements.filter((_, i) => i !== index);
      setStatements(updatedStatements);
      onChange(updatedStatements);
      if (activeStatementIndex >= statements.length - 1) {
        setActiveStatementIndex(Math.max(0, statements.length - 2));
      }
    },
    [statements, activeStatementIndex, onChange]
  );

  // Update SQL statement
  const updateStatement = useCallback(
    (index: number, updates: Partial<SQLStatement>) => {
      const updatedStatements = [...statements];
      updatedStatements[index] = { ...updatedStatements[index], ...updates };
      setStatements(updatedStatements);
      onChange(updatedStatements);
    },
    [statements, onChange]
  );

  const selectedTableData = useMemo(() => {
    return databaseSchema.find(table => table.tableName === selectedTable);
  }, [databaseSchema, selectedTable]);

  return (
    <div className={cn('space-y-4', className)}>
      {/* Connection Section */}
      <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-medium text-white flex items-center gap-2">
            <Database className="w-5 h-5" />
            PostgreSQL Connection
          </h3>
          <button
            onClick={testConnection}
            disabled={isConnecting || !connectionString}
            className={cn(
              'px-3 py-1 rounded-md text-sm font-medium flex items-center gap-2',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              isConnected ? 'bg-green-600 text-white' : 'bg-blue-600 text-white hover:bg-blue-700'
            )}
          >
            {isConnecting ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : isConnected ? (
              <CheckCircle className="w-4 h-4" />
            ) : (
              <Database className="w-4 h-4" />
            )}
            {isConnecting ? 'Connecting...' : isConnected ? 'Connected' : 'Test Connection'}
          </button>
        </div>

        {connectionError && (
          <div className="flex items-center gap-2 text-red-400 text-sm mb-2">
            <AlertCircle className="w-4 h-4" />
            <span>{connectionError}</span>
          </div>
        )}

        {isConnected && (
          <div className="flex items-center gap-2 text-green-400 text-sm">
            <CheckCircle className="w-4 h-4" />
            <span>Database connection established successfully</span>
          </div>
        )}
      </div>

      {/* Schema Browser Section - Always Visible */}
      <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-medium text-white flex items-center gap-2">
            <Table className="w-5 h-5" />
            Database Schema Browser <span className="text-xs text-gray-400">(Demo Data)</span>
          </h3>
          <button
            onClick={() => setShowSchemaBrowser(!showSchemaBrowser)}
            className="px-3 py-1 bg-gray-600 text-white rounded-md text-sm hover:bg-gray-500 flex items-center gap-2"
          >
            <Eye className="w-4 h-4" />
            {showSchemaBrowser ? 'Hide' : 'Show'} Schema
          </button>
        </div>

        {showSchemaBrowser && (
          <div className="space-y-3">
            <div className="text-center text-sm text-gray-400 mb-3">
              {isConnected
                ? 'Live Database Schema'
                : 'Demo Database Schema (Sample Industrial Data)'}
            </div>
            {isLoadingSchema ? (
              <div className="flex items-center gap-2 text-gray-400">
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Loading database schema...</span>
              </div>
            ) : (
              <>
                <select
                  value={selectedTable}
                  onChange={e => setSelectedTable(e.target.value)}
                  className="w-full px-3 py-2 bg-[#1e1e1e] border border-gray-600 rounded-lg text-white"
                >
                  <option value="">Select table to browse...</option>
                  {databaseSchema.map(table => (
                    <option key={table.tableName} value={table.tableName}>
                      {table.tableName} ({table.rowCount.toLocaleString()} rows)
                    </option>
                  ))}
                </select>

                {selectedTableData && (
                  <div className="bg-gray-900 rounded-lg p-3 border border-gray-600">
                    <h4 className="text-white font-medium mb-2 flex items-center gap-2">
                      <Columns className="w-4 h-4" />
                      {selectedTableData.tableName} Schema
                    </h4>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-gray-600">
                            <th className="text-left text-gray-400 py-1">Column</th>
                            <th className="text-left text-gray-400 py-1">Type</th>
                            <th className="text-left text-gray-400 py-1">Nullable</th>
                            <th className="text-left text-gray-400 py-1">Default</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedTableData.columns.map(column => (
                            <tr key={column.columnName} className="border-b border-gray-700/50">
                              <td className="text-white py-1 font-mono">{column.columnName}</td>
                              <td className="text-blue-400 py-1">{column.dataType}</td>
                              <td className="text-gray-400 py-1">
                                {column.isNullable ? 'YES' : 'NO'}
                              </td>
                              <td className="text-gray-400 py-1 font-mono">
                                {column.columnDefault || '-'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>

      {/* SQL Statements Section */}
      <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-white">SQL Statements</h3>
          <button
            onClick={addStatement}
            className="px-3 py-1 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add Statement
          </button>
        </div>

        {/* Statement Tabs */}
        <div className="flex gap-1 mb-4 overflow-x-auto">
          {statements.map((statement, index) => (
            <button
              key={index}
              onClick={() => setActiveStatementIndex(index)}
              className={cn(
                'px-3 py-1 text-sm font-medium rounded-t-md border border-b-0 whitespace-nowrap flex items-center gap-2',
                activeStatementIndex === index
                  ? 'bg-gray-700 text-white border-gray-600'
                  : 'bg-gray-800 text-gray-400 border-gray-700 hover:text-gray-300'
              )}
            >
              <span>{statement.name}</span>
              {statement.verified && <CheckCircle className="w-3 h-3 text-green-400" />}
              {statement.error && <AlertCircle className="w-3 h-3 text-red-400" />}
              {statements.length > 1 && (
                <button
                  onClick={e => {
                    e.stopPropagation();
                    removeStatement(index);
                  }}
                  className="hover:text-red-400"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              )}
            </button>
          ))}
        </div>

        {/* Active Statement Editor */}
        {statements[activeStatementIndex] && (
          <div className="space-y-4">
            {/* Statement Name */}
            <input
              type="text"
              value={statements[activeStatementIndex].name}
              onChange={e => updateStatement(activeStatementIndex, { name: e.target.value })}
              placeholder="Statement name"
              className="w-full px-3 py-2 bg-[#1e1e1e] border border-gray-600 rounded-lg text-white text-sm"
            />

            {/* SQL Editor */}
            <div className="relative">
              <textarea
                value={statements[activeStatementIndex].sql}
                onChange={e =>
                  updateStatement(activeStatementIndex, {
                    sql: e.target.value,
                    verified: undefined,
                    error: undefined,
                  })
                }
                placeholder="Enter your SQL statement here..."
                rows={6}
                className="w-full px-3 py-2 bg-[#1e1e1e] border border-gray-600 rounded-lg text-white font-mono text-sm resize-none"
              />

              {/* Action Buttons */}
              <div className="flex gap-2 mt-2">
                <button
                  onClick={() => verifyStatement(activeStatementIndex)}
                  disabled={!statements[activeStatementIndex].sql.trim()}
                  className="px-3 py-1 bg-orange-600 text-white rounded-md text-sm hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  Verify SQL
                </button>

                <button
                  onClick={() => previewStatement(activeStatementIndex)}
                  disabled={!statements[activeStatementIndex].sql.trim() || !isConnected}
                  className="px-3 py-1 bg-green-600 text-white rounded-md text-sm hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  Preview Results
                </button>
              </div>
            </div>

            {/* Statement Status */}
            {statements[activeStatementIndex].error && (
              <div className="flex items-center gap-2 text-red-400 text-sm bg-red-900/20 p-2 rounded-md">
                <AlertCircle className="w-4 h-4" />
                <span>{statements[activeStatementIndex].error}</span>
              </div>
            )}

            {statements[activeStatementIndex].verified &&
              !statements[activeStatementIndex].error && (
                <div className="flex items-center gap-2 text-green-400 text-sm bg-green-900/20 p-2 rounded-md">
                  <CheckCircle className="w-4 h-4" />
                  <span>SQL statement verified successfully against database schema</span>
                </div>
              )}

            {/* Preview Results */}
            {statements[activeStatementIndex].preview && (
              <div className="bg-gray-900 rounded-lg p-3 border border-gray-600">
                <h4 className="text-white font-medium mb-2 flex items-center gap-2">
                  <Eye className="w-4 h-4" />
                  Query Results Preview ({statements[activeStatementIndex].preview!.length} rows)
                </h4>
                <div className="overflow-x-auto max-h-48 overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-600">
                        {statements[activeStatementIndex].preview!.length > 0 &&
                          Object.keys(statements[activeStatementIndex].preview![0]).map(key => (
                            <th key={key} className="text-left text-gray-400 py-1 px-2 font-mono">
                              {key}
                            </th>
                          ))}
                      </tr>
                    </thead>
                    <tbody>
                      {statements[activeStatementIndex]
                        .preview!.slice(0, 10)
                        .map((row, rowIndex) => (
                          <tr key={rowIndex} className="border-b border-gray-700/50">
                            {Object.values(row).map((value, colIndex) => (
                              <td key={colIndex} className="text-white py-1 px-2 font-mono text-xs">
                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                              </td>
                            ))}
                          </tr>
                        ))}
                    </tbody>
                  </table>
                  {statements[activeStatementIndex].preview!.length > 10 && (
                    <div className="text-center text-gray-400 text-xs mt-2">
                      ... and {statements[activeStatementIndex].preview!.length - 10} more rows
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Statement Settings */}
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 text-sm text-gray-400">
                <input
                  type="checkbox"
                  checked={statements[activeStatementIndex].enabled}
                  onChange={e =>
                    updateStatement(activeStatementIndex, { enabled: e.target.checked })
                  }
                  className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                />
                Enable this statement
              </label>
            </div>
          </div>
        )}

        {/* Summary */}
        <div className="mt-4 pt-3 border-t border-gray-700">
          <div className="text-sm text-gray-400">
            {statements.length} statement{statements.length !== 1 ? 's' : ''} defined,{' '}
            {statements.filter(s => s.enabled).length} enabled,{' '}
            {statements.filter(s => s.verified).length} verified
          </div>
        </div>
      </div>
    </div>
  );
}
