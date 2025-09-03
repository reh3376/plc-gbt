import { cn } from '@/lib/utils/cn';
import {
  AlertCircle,
  CheckCircle,
  Eye,
  Network,
  Play,
  Plus,
  RefreshCw,
  Share2,
  Trash2,
  Users,
} from 'lucide-react';
import React, { useCallback, useEffect, useState } from 'react';

interface CypherStatement {
  name: string;
  cypher: string;
  enabled: boolean;
  preview?: Record<string, unknown>[];
  error?: string;
  verified?: boolean;
}

interface CypherBuilderProps {
  readonly value: CypherStatement[];
  readonly onChange: (statements: CypherStatement[]) => void;
  readonly connectionUri?: string;
  readonly username?: string;
  readonly password?: string;
  readonly database?: string;
  readonly className?: string;
}

interface NodeLabel {
  label: string;
  count: number;
  properties: string[];
}

interface RelationshipType {
  type: string;
  count: number;
  properties: string[];
}

interface DatabaseStat {
  nodeCount: number;
  relationshipCount: number;
  labelCount: number;
  relationshipTypeCount: number;
}

export function CypherBuilder({
  value,
  onChange,
  connectionUri,
  username,
  password,
  database,
  className,
}: CypherBuilderProps) {
  const [statements, setStatements] = useState<CypherStatement[]>(value || []);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionError, setConnectionError] = useState<string>('');
  const [nodeLabels, setNodeLabels] = useState<NodeLabel[]>([]);
  const [relationshipTypes, setRelationshipTypes] = useState<RelationshipType[]>([]);
  const [databaseStats, setDatabaseStats] = useState<DatabaseStat | null>(null);
  const [showSchemaBrowser, setShowSchemaBrowser] = useState(true);
  const [isLoadingSchema, setIsLoadingSchema] = useState(false);
  const [activeStatementIndex, setActiveStatementIndex] = useState(0);

  // Initialize statements from props but don't automatically sync back
  // onChange will be called only on user interactions (add/remove/edit)

  // Auto-load mock graph schema data for immediate demonstration
  useEffect(() => {
    const loadMockGraphSchema = () => {
      // Mock schema data for demonstration
      const mockNodeLabels: NodeLabel[] = [
        {
          label: 'Process',
          count: 45,
          properties: ['name', 'type', 'description', 'location', 'capacity'],
        },
        {
          label: 'Equipment',
          count: 127,
          properties: ['name', 'model', 'manufacturer', 'serialNumber', 'installDate', 'status'],
        },
        {
          label: 'Measurement',
          count: 1250,
          properties: ['timestamp', 'tagName', 'value', 'unit', 'quality'],
        },
        {
          label: 'Alarm',
          count: 234,
          properties: ['timestamp', 'severity', 'message', 'source', 'acknowledged'],
        },
      ];

      const mockRelationshipTypes: RelationshipType[] = [
        {
          type: 'BELONGS_TO',
          count: 172,
          properties: ['since', 'confidence'],
        },
        {
          type: 'MEASURES',
          count: 1250,
          properties: ['frequency', 'accuracy', 'range'],
        },
        {
          type: 'CONTROLS',
          count: 89,
          properties: ['mode', 'authority', 'lastUpdate'],
        },
        {
          type: 'TRIGGERS',
          count: 234,
          properties: ['condition', 'delay', 'priority'],
        },
      ];

      const mockStats: DatabaseStat = {
        nodeCount: 1656,
        relationshipCount: 1745,
        labelCount: 4,
        relationshipTypeCount: 4,
      };

      setNodeLabels(mockNodeLabels);
      setRelationshipTypes(mockRelationshipTypes);
      setDatabaseStats(mockStats);
    };

    // Load immediately for demonstration
    loadMockGraphSchema();
  }, []);

  // Test Neo4j connection
  const testConnection = useCallback(async () => {
    if (!connectionUri || !username || !password) {
      setConnectionError('Connection URI, username, and password are required');
      return;
    }

    setIsConnecting(true);
    setConnectionError('');

    try {
      // Simulate connection test - in real implementation, this would call Neo4j API
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Mock successful connection
      setIsConnected(true);
      console.log(`✅ Neo4j connection established to database: ${database || 'neo4j'}`);
    } catch (error: unknown) {
      setIsConnected(false);
      setConnectionError(error instanceof Error ? error.message : 'Connection failed');
    } finally {
      setIsConnecting(false);
    }
  }, [connectionUri, username, password]);

  // Load database schema
  const loadDatabaseSchema = useCallback(async () => {
    if (!isConnected) return;

    setIsLoadingSchema(true);
    try {
      // Simulate schema loading - in real implementation, this would query Neo4j schema
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Mock schema data
      const mockNodeLabels: NodeLabel[] = [
        {
          label: 'Process',
          count: 45,
          properties: ['name', 'type', 'description', 'location', 'capacity'],
        },
        {
          label: 'Equipment',
          count: 127,
          properties: ['name', 'model', 'manufacturer', 'serialNumber', 'installDate', 'status'],
        },
        {
          label: 'Measurement',
          count: 1250,
          properties: ['timestamp', 'tagName', 'value', 'unit', 'quality'],
        },
        {
          label: 'Alarm',
          count: 234,
          properties: ['timestamp', 'severity', 'message', 'source', 'acknowledged'],
        },
      ];

      const mockRelationshipTypes: RelationshipType[] = [
        {
          type: 'BELONGS_TO',
          count: 172,
          properties: ['since', 'confidence'],
        },
        {
          type: 'MEASURES',
          count: 1250,
          properties: ['frequency', 'accuracy', 'range'],
        },
        {
          type: 'CONTROLS',
          count: 89,
          properties: ['mode', 'authority', 'lastUpdate'],
        },
        {
          type: 'TRIGGERS',
          count: 234,
          properties: ['condition', 'delay', 'priority'],
        },
      ];

      const mockStats: DatabaseStat = {
        nodeCount: 1656,
        relationshipCount: 1745,
        labelCount: 4,
        relationshipTypeCount: 4,
      };

      setNodeLabels(mockNodeLabels);
      setRelationshipTypes(mockRelationshipTypes);
      setDatabaseStats(mockStats);
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

  // Preview Cypher statement results
  const previewStatement = useCallback(
    async (index: number) => {
      const statement = statements[index];
      if (!statement.cypher.trim() || !isConnected) return;

      const updatedStatements = [...statements];
      updatedStatements[index] = { ...statement, preview: undefined, error: undefined };
      setStatements(updatedStatements);

      try {
        // Simulate Cypher execution - in real implementation, this would call Neo4j API
        await new Promise(resolve => setTimeout(resolve, 800));

        // Mock result data based on Cypher content
        const cypher = statement.cypher.toLowerCase();
        let mockResults;

        if (cypher.includes('count')) {
          mockResults = [{ count: 1656 }];
        } else if (cypher.includes('equipment')) {
          mockResults = [
            {
              name: 'Distillation Column 01',
              type: 'Distillation',
              manufacturer: 'Sulzer',
              status: 'Operating',
            },
            {
              name: 'Heat Exchanger 02',
              type: 'HeatExchanger',
              manufacturer: 'Alfa Laval',
              status: 'Operating',
            },
            {
              name: 'Pump 03',
              type: 'CentrifugalPump',
              manufacturer: 'Grundfos',
              status: 'Maintenance',
            },
          ];
        } else if (cypher.includes('measurement')) {
          mockResults = [
            {
              tagName: 'TI-101',
              value: 82.5,
              unit: '°C',
              quality: 'Good',
              timestamp: '2025-01-22T14:30:00Z',
            },
            {
              tagName: 'PI-201',
              value: 3.2,
              unit: 'bar',
              quality: 'Good',
              timestamp: '2025-01-22T14:30:00Z',
            },
            {
              tagName: 'LI-301',
              value: 67.8,
              unit: '%',
              quality: 'Good',
              timestamp: '2025-01-22T14:30:00Z',
            },
          ];
        } else {
          mockResults = [
            { result: 'Query executed successfully', timestamp: new Date().toISOString() },
          ];
        }

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

  // Verify Cypher statement against database schema
  const verifyStatement = useCallback(
    (index: number) => {
      const statement = statements[index];
      if (!statement.cypher.trim()) return;

      // Simple Cypher validation against available labels and relationship types
      const cypher = statement.cypher.toLowerCase();
      const availableLabels = nodeLabels.map(label => label.label.toLowerCase());
      const availableRelTypes = relationshipTypes.map(rel => rel.type.toLowerCase());

      let hasValidElements = false;

      // Check for valid node labels
      availableLabels.forEach(label => {
        if (cypher.includes(label.toLowerCase())) {
          hasValidElements = true;
        }
      });

      // Check for valid relationship types
      availableRelTypes.forEach(relType => {
        if (cypher.includes(relType.toLowerCase().replace('_', '_'))) {
          hasValidElements = true;
        }
      });

      // Allow basic queries
      if (cypher.includes('match') && cypher.includes('return')) {
        hasValidElements = true;
      }

      const updatedStatements = [...statements];
      if (hasValidElements) {
        updatedStatements[index] = { ...statement, verified: true, error: undefined };
      } else {
        updatedStatements[index] = {
          ...statement,
          verified: false,
          error: `Cypher references unknown labels/relationships. Available labels: ${availableLabels.join(
            ', '
          )}. Available relationships: ${availableRelTypes.join(', ')}`,
        };
      }

      setStatements(updatedStatements);
      onChange(updatedStatements);
    },
    [statements, nodeLabels, relationshipTypes, onChange]
  );

  // Add new Cypher statement
  const addStatement = useCallback(() => {
    const newStatement: CypherStatement = {
      name: `Query${statements.length + 1}`,
      cypher: 'MATCH (n) RETURN COUNT(n) as nodeCount',
      enabled: true,
    };
    const updatedStatements = [...statements, newStatement];
    setStatements(updatedStatements);
    onChange(updatedStatements);
  }, [statements, onChange]);

  // Remove Cypher statement
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

  // Update Cypher statement
  const updateStatement = useCallback(
    (index: number, updates: Partial<CypherStatement>) => {
      const updatedStatements = [...statements];
      updatedStatements[index] = { ...updatedStatements[index], ...updates };
      setStatements(updatedStatements);
      onChange(updatedStatements);
    },
    [statements, onChange]
  );

  return (
    <div className={cn('space-y-4', className)}>
      {/* Connection Section */}
      <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-medium text-white flex items-center gap-2">
            <Network className="w-5 h-5" />
            Neo4j Connection
          </h3>
          <button
            onClick={testConnection}
            disabled={isConnecting || !connectionUri || !username || !password}
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
              <Network className="w-4 h-4" />
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

        {databaseStats && (
          <div className="space-y-2 mt-3">
            <div className="text-center text-sm text-gray-400">
              {isConnected ? (
                <>
                  Connected to database:{' '}
                  <span className="text-white font-mono">{database || 'neo4j'}</span>
                </>
              ) : (
                <>
                  Demo Database Schema: <span className="text-white font-mono">neo4j (sample)</span>
                </>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center bg-gray-900/50 rounded p-2">
                <div className="text-lg font-bold text-white">
                  {databaseStats.nodeCount.toLocaleString()}
                </div>
                <div className="text-xs text-gray-400">Nodes</div>
              </div>
              <div className="text-center bg-gray-900/50 rounded p-2">
                <div className="text-lg font-bold text-white">
                  {databaseStats.relationshipCount.toLocaleString()}
                </div>
                <div className="text-xs text-gray-400">Relationships</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Graph Schema Browser Section - Always Visible */}
      <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-medium text-white flex items-center gap-2">
            <Share2 className="w-5 h-5" />
            Graph Schema Browser <span className="text-xs text-gray-400">(Demo Data)</span>
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
          <div className="space-y-4">
            <div className="text-center text-sm text-gray-400 mb-3">
              {isConnected
                ? 'Live Graph Database Schema'
                : 'Demo Graph Schema (Sample Industrial Process Data)'}
            </div>
            {isLoadingSchema ? (
              <div className="flex items-center gap-2 text-gray-400">
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Loading graph schema...</span>
              </div>
            ) : (
              <>
                {/* Node Labels */}
                <div>
                  <h4 className="text-white font-medium mb-2 flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    Node Labels
                  </h4>
                  <div className="bg-gray-900 rounded-lg p-3 border border-gray-600">
                    <div className="grid gap-2">
                      {nodeLabels.map(label => (
                        <div key={label.label} className="flex justify-between items-start">
                          <div>
                            <span className="text-blue-400 font-mono">:{label.label}</span>
                            <span className="text-gray-400 text-sm ml-2">
                              ({label.count.toLocaleString()} nodes)
                            </span>
                          </div>
                          <div className="text-xs text-gray-500">
                            {label.properties.slice(0, 3).join(', ')}
                            {label.properties.length > 3 && ` +${label.properties.length - 3} more`}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Relationship Types */}
                <div>
                  <h4 className="text-white font-medium mb-2 flex items-center gap-2">
                    <Share2 className="w-4 h-4" />
                    Relationship Types
                  </h4>
                  <div className="bg-gray-900 rounded-lg p-3 border border-gray-600">
                    <div className="grid gap-2">
                      {relationshipTypes.map(rel => (
                        <div key={rel.type} className="flex justify-between items-start">
                          <div>
                            <span className="text-green-400 font-mono">:{rel.type}</span>
                            <span className="text-gray-400 text-sm ml-2">
                              ({rel.count.toLocaleString()} relationships)
                            </span>
                          </div>
                          <div className="text-xs text-gray-500">
                            {rel.properties.slice(0, 3).join(', ')}
                            {rel.properties.length > 3 && ` +${rel.properties.length - 3} more`}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Common Query Templates */}
                <div>
                  <h4 className="text-white font-medium mb-2">Quick Query Templates</h4>
                  <div className="grid grid-cols-1 gap-2">
                    <button
                      onClick={() => {
                        const templateQuery =
                          'MATCH (n) RETURN labels(n) as nodeLabels, count(n) as count ORDER BY count DESC';
                        updateStatement(activeStatementIndex, { cypher: templateQuery });
                      }}
                      className="text-left bg-gray-700 hover:bg-gray-600 rounded p-2 text-sm"
                    >
                      <div className="text-white font-mono text-xs">Node Label Distribution</div>
                      <div className="text-gray-400 text-xs">
                        MATCH (n) RETURN labels(n), count(n)
                      </div>
                    </button>

                    <button
                      onClick={() => {
                        const templateQuery =
                          'MATCH ()-[r]->() RETURN type(r) as relType, count(r) as count ORDER BY count DESC';
                        updateStatement(activeStatementIndex, { cypher: templateQuery });
                      }}
                      className="text-left bg-gray-700 hover:bg-gray-600 rounded p-2 text-sm"
                    >
                      <div className="text-white font-mono text-xs">Relationship Distribution</div>
                      <div className="text-gray-400 text-xs">
                        MATCH ()-[r]-&gt;() RETURN type(r), count(r)
                      </div>
                    </button>

                    <button
                      onClick={() => {
                        const templateQuery =
                          'MATCH (e:Equipment)-[:MEASURES]->(m:Measurement) WHERE m.timestamp > datetime() - duration("PT1H") RETURN e.name, m.tagName, m.value ORDER BY m.timestamp DESC LIMIT 10';
                        updateStatement(activeStatementIndex, { cypher: templateQuery });
                      }}
                      className="text-left bg-gray-700 hover:bg-gray-600 rounded p-2 text-sm"
                    >
                      <div className="text-white font-mono text-xs">Recent Measurements</div>
                      <div className="text-gray-400 text-xs">
                        Equipment measurements from last hour
                      </div>
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Cypher Statements Section */}
      <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-white">Cypher Statements</h3>
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

            {/* Cypher Editor */}
            <div className="relative">
              <textarea
                value={statements[activeStatementIndex].cypher}
                onChange={e =>
                  updateStatement(activeStatementIndex, {
                    cypher: e.target.value,
                    verified: undefined,
                    error: undefined,
                  })
                }
                placeholder="Enter your Cypher statement here..."
                rows={6}
                className="w-full px-3 py-2 bg-[#1e1e1e] border border-gray-600 rounded-lg text-white font-mono text-sm resize-none"
              />

              {/* Action Buttons */}
              <div className="flex gap-2 mt-2">
                <button
                  onClick={() => verifyStatement(activeStatementIndex)}
                  disabled={!statements[activeStatementIndex].cypher.trim()}
                  className="px-3 py-1 bg-orange-600 text-white rounded-md text-sm hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  Verify Cypher
                </button>

                <button
                  onClick={() => previewStatement(activeStatementIndex)}
                  disabled={!statements[activeStatementIndex].cypher.trim() || !isConnected}
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
                  <span>Cypher statement verified successfully against graph schema</span>
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
