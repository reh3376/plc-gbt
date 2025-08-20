/**
 * Node Documentation Index - AI Task Orchestrator TypeScript Implementation
 *
 * @description Main documentation index page for all industrial nodes
 * @compliance Strict TypeScript - zero `any` types policy
 * @features Category-based navigation, search functionality, progress tracking
 */

'use client';

import { BookOpen, ExternalLink, Search, Settings } from 'lucide-react';
import Link from 'next/link';
import React, { useMemo, useState } from 'react';

import { cn } from '@/lib/utils/cn';

interface DocCategory {
  readonly name: string;
  readonly description: string;
  readonly nodes: ReadonlyArray<{
    readonly nodeType: string;
    readonly title: string;
    readonly description: string;
    readonly complexity: 'basic' | 'intermediate' | 'advanced';
    readonly hasExternalDocs: boolean;
  }>;
}

const DOCUMENTATION_CATEGORIES: ReadonlyArray<DocCategory> = [
  {
    name: 'Control & Optimization',
    description: 'Advanced control algorithms and optimization techniques',
    nodes: [
      { nodeType: 'pid-controller', title: 'PID Controller', description: 'Classical PID control algorithm', complexity: 'basic', hasExternalDocs: false },
      { nodeType: 'mpc-controller', title: 'MPC Controller', description: 'Model Predictive Control', complexity: 'advanced', hasExternalDocs: false },
      { nodeType: 'imc-controller', title: 'IMC Controller', description: 'Internal Model Control', complexity: 'advanced', hasExternalDocs: false },
      { nodeType: 'feedforward-controller', title: 'Feedforward Controller', description: 'Disturbance compensation', complexity: 'intermediate', hasExternalDocs: false },
      { nodeType: 'kalman-filter', title: 'Kalman Filter', description: 'State estimation filter', complexity: 'advanced', hasExternalDocs: false },
      { nodeType: 'quadratic-programming', title: 'Quadratic Programming', description: 'QP optimization solver', complexity: 'advanced', hasExternalDocs: false },
      { nodeType: 'subspace-identification', title: 'Subspace Identification', description: 'System identification methods', complexity: 'advanced', hasExternalDocs: false },
    ],
  },
  {
    name: 'PLC Integration',
    description: 'Programmable Logic Controller interfaces and communication',
    nodes: [
      { nodeType: 'plc-input', title: 'PLC Input', description: 'Read sensor data from PLC', complexity: 'basic', hasExternalDocs: false },
      { nodeType: 'plc-output', title: 'PLC Output', description: 'Control actuators via PLC', complexity: 'basic', hasExternalDocs: false },
      { nodeType: 'modbus-client', title: 'Modbus Client', description: 'Modbus communication protocol', complexity: 'intermediate', hasExternalDocs: true },
      { nodeType: 'opc-server', title: 'OPC Server', description: 'OPC data server', complexity: 'intermediate', hasExternalDocs: true },
      { nodeType: 'opc-client', title: 'OPC Client', description: 'OPC client connection', complexity: 'intermediate', hasExternalDocs: true },
      { nodeType: 'hmi-display', title: 'HMI Display', description: 'Human Machine Interface', complexity: 'intermediate', hasExternalDocs: false },
    ],
  },
  {
    name: 'Data Integration',
    description: 'Database connectors and data storage solutions',
    nodes: [
      { nodeType: 'postgresql-connector', title: 'PostgreSQL Connector', description: 'PostgreSQL database integration', complexity: 'intermediate', hasExternalDocs: true },
      { nodeType: 'redis-connector', title: 'Redis Connector', description: 'Redis cache and data store', complexity: 'intermediate', hasExternalDocs: true },
      { nodeType: 'neo4j-connector', title: 'Neo4j Connector', description: 'Graph database connector', complexity: 'intermediate', hasExternalDocs: true },
      { nodeType: 'qdrant-connector', title: 'Qdrant Connector', description: 'Vector database for AI', complexity: 'intermediate', hasExternalDocs: true },
      { nodeType: 'historian-connector', title: 'Historian Connector', description: 'Process historian integration', complexity: 'intermediate', hasExternalDocs: false },
    ],
  },
  {
    name: 'Machine Learning',
    description: 'AI and machine learning algorithms for process optimization',
    nodes: [
      { nodeType: 'narx-neural-network', title: 'NARX Neural Network', description: 'Nonlinear system identification', complexity: 'advanced', hasExternalDocs: false },
      { nodeType: 'gaussian-process-regression', title: 'Gaussian Process Regression', description: 'Probabilistic ML model', complexity: 'advanced', hasExternalDocs: false },
      { nodeType: 'lstm-model', title: 'LSTM Model', description: 'Long Short-Term Memory network', complexity: 'advanced', hasExternalDocs: false },
      { nodeType: 'sindy-identifier', title: 'SINDy Identifier', description: 'Sparse nonlinear dynamics identification', complexity: 'advanced', hasExternalDocs: false },
      { nodeType: 'reinforcement-learning', title: 'Reinforcement Learning', description: 'RL agent for optimal control', complexity: 'advanced', hasExternalDocs: false },
    ],
  },
  {
    name: 'System Components',
    description: 'Core system components for data logging and monitoring',
    nodes: [
      { nodeType: 'data-logger', title: 'Data Logger', description: 'Historical data logging', complexity: 'basic', hasExternalDocs: false },
      { nodeType: 'alarm-handler', title: 'Alarm Handler', description: 'Process alarm management', complexity: 'intermediate', hasExternalDocs: false },
      { nodeType: 'custom-logic', title: 'Custom Logic', description: 'User-defined logic blocks', complexity: 'intermediate', hasExternalDocs: false },
      { nodeType: 'url-display', title: 'URL Display', description: 'Web content embedding', complexity: 'basic', hasExternalDocs: false },
    ],
  },
  {
    name: 'Workflow Management',
    description: 'Workflow orchestration and execution control',
    nodes: [
      { nodeType: 'n8n-workflow', title: 'N8N Workflow', description: 'N8N automation platform integration', complexity: 'intermediate', hasExternalDocs: true },
      { nodeType: 'workflow-reference', title: 'Workflow Reference', description: 'External workflow references', complexity: 'basic', hasExternalDocs: false },
      { nodeType: 'workflow-subset', title: 'Workflow Subset', description: 'Selective workflow execution', complexity: 'intermediate', hasExternalDocs: false },
      { nodeType: 'workflow-conditional', title: 'Workflow Conditional', description: 'Conditional execution logic', complexity: 'intermediate', hasExternalDocs: false },
      { nodeType: 'workflow-parallel', title: 'Workflow Parallel', description: 'Parallel execution branches', complexity: 'intermediate', hasExternalDocs: false },
      { nodeType: 'workflow-loop', title: 'Workflow Loop', description: 'Iterative execution control', complexity: 'intermediate', hasExternalDocs: false },
    ],
  },
  {
    name: 'Analysis & Reporting',
    description: 'Data analysis, visualization, and reporting tools',
    nodes: [
      { nodeType: 'math-function-creator', title: 'Math Function Creator', description: 'Mathematical function builder', complexity: 'advanced', hasExternalDocs: false },
      { nodeType: 'data-distribution-analyzer', title: 'Data Distribution Analyzer', description: 'Statistical analysis tool', complexity: 'intermediate', hasExternalDocs: false },
      { nodeType: 'dashboard-generator', title: 'Dashboard Generator', description: 'Automated dashboard creation', complexity: 'intermediate', hasExternalDocs: false },
      { nodeType: 'pdf-report-generator', title: 'PDF Report Generator', description: 'PDF report automation', complexity: 'intermediate', hasExternalDocs: false },
      { nodeType: 'email-notifier', title: 'Email Notifier', description: 'Email notification system', complexity: 'basic', hasExternalDocs: false },
      { nodeType: 'chart-generator', title: 'Chart Generator', description: 'Dynamic chart creation', complexity: 'intermediate', hasExternalDocs: false },
      { nodeType: 'kpi-calculator', title: 'KPI Calculator', description: 'Key Performance Indicators', complexity: 'intermediate', hasExternalDocs: false },
    ],
  },
];

export default function NodeDocumentationIndex(): React.JSX.Element {
  const [searchQuery, setSearchQuery] = useState('');
  
  // Filter categories and nodes based on search
  const filteredCategories = useMemo(() => {
    if (!searchQuery) return DOCUMENTATION_CATEGORIES;
    
    return DOCUMENTATION_CATEGORIES.map(category => ({
      ...category,
      nodes: category.nodes.filter(node =>
        node.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.nodeType.toLowerCase().includes(searchQuery.toLowerCase())
      ),
    })).filter(category => category.nodes.length > 0);
  }, [searchQuery]);
  
  const totalNodes = DOCUMENTATION_CATEGORIES.reduce((sum, cat) => sum + cat.nodes.length, 0);
  const filteredNodes = filteredCategories.reduce((sum, cat) => sum + cat.nodes.length, 0);
  
  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'basic':
        return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
      case 'intermediate':
        return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200';
      case 'advanced':
        return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200';
      default:
        return 'bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <BookOpen className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                Industrial Node Documentation
              </h1>
            </div>
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-6">
              Comprehensive documentation for all industrial automation nodes in the PLC-GBT system
            </p>
            
            {/* Search */}
            <div className="max-w-md mx-auto relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search nodes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className={cn(
                  'w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600',
                  'rounded-lg bg-white dark:bg-gray-700',
                  'text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400',
                  'focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                  'transition-all duration-200'
                )}
              />
            </div>
            
            {/* Stats */}
            <div className="mt-6 flex items-center justify-center space-x-6 text-sm text-gray-600 dark:text-gray-400">
              <span>{filteredNodes} of {totalNodes} nodes</span>
              <span>•</span>
              <span>{filteredCategories.length} categories</span>
              <span>•</span>
              <span>Phase 1.5 Implementation</span>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Categories */}
        <div className="space-y-8">
          {filteredCategories.map((category) => (
            <section key={category.name} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  {category.name}
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  {category.description}
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {category.nodes.map((node) => (
                  <Link
                    key={node.nodeType}
                    href={`/docs/nodes/${node.nodeType}`}
                    className="group block p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-md transition-all duration-200"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <Settings className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                          {node.title}
                        </h3>
                      </div>
                      <div className="flex items-center space-x-2">
                        {node.hasExternalDocs && (
                          <ExternalLink className="w-4 h-4 text-gray-400" />
                        )}
                        <span className={cn(
                          'px-2 py-1 text-xs rounded-full',
                          getComplexityColor(node.complexity)
                        )}>
                          {node.complexity}
                        </span>
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      {node.description}
                    </p>
                    
                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                      <span>Node Type: {node.nodeType}</span>
                      <span className="text-blue-600 dark:text-blue-400 group-hover:text-blue-700 dark:group-hover:text-blue-300">
                        View Documentation →
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          ))}
        </div>
        
        {/* No Results */}
        {filteredCategories.length === 0 && (
          <div className="text-center py-12">
            <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              No nodes found
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Try adjusting your search query or browse all categories above.
            </p>
          </div>
        )}
        
        {/* Development Status */}
        <div className="mt-12 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <BookOpen className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            <h2 className="text-xl font-bold text-blue-900 dark:text-blue-100">
              Documentation Development Status
            </h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Phase 1.5: Complete ✅
              </h3>
              <ul className="text-gray-600 dark:text-gray-400 space-y-1">
                <li>• CircleHelp icon system</li>
                <li>• Tooltip infrastructure</li>
                <li>• 36 placeholder pages created</li>
                <li>• Documentation routing</li>
              </ul>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Phase 2: Planned 📋
              </h3>
              <ul className="text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Detailed content creation</li>
                <li>• Interactive examples</li>
                <li>• Video tutorials</li>
                <li>• Advanced troubleshooting</li>
              </ul>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Phase 3: Future 🚀
              </h3>
              <ul className="text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Community features</li>
                <li>• Version comparisons</li>
                <li>• API auto-generation</li>
                <li>• Advanced search</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
