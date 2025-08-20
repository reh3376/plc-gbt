/**
 * Node Documentation Template - AI Task Orchestrator TypeScript Implementation
 *
 * @description Reusable template component for node documentation pages
 * @compliance Strict TypeScript - zero `any` types policy
 * @features Structured layout, code examples, interactive elements
 */

'use client';

import { AlertTriangle, CheckCircle, Copy, ExternalLink, Info, Lightbulb, Settings, Zap } from 'lucide-react';
import Link from 'next/link';
import React, { useCallback, useState } from 'react';

import { type IndustrialNodeType } from '@/api/zod-schemas';
import { cn } from '@/lib/utils/cn';

interface ParameterReference {
  readonly name: string;
  readonly type: string;
  readonly defaultValue: string;
  readonly range?: string;
  readonly description: string;
  readonly required: boolean;
}

interface CodeExample {
  readonly title: string;
  readonly description: string;
  readonly code: string;
  readonly language: 'json' | 'typescript' | 'javascript';
}

interface TroubleshootingItem {
  readonly issue: string;
  readonly symptoms: string;
  readonly cause: string;
  readonly solution: string;
  readonly severity: 'low' | 'medium' | 'high';
}

interface NodeDocumentationData {
  readonly nodeType: IndustrialNodeType;
  readonly title: string;
  readonly description: string;
  readonly overview: string;
  readonly features: ReadonlyArray<string>;
  readonly useCases: ReadonlyArray<string>;
  readonly parameters: ReadonlyArray<ParameterReference>;
  readonly examples: ReadonlyArray<CodeExample>;
  readonly troubleshooting: ReadonlyArray<TroubleshootingItem>;
  readonly bestPractices: {
    readonly dos: ReadonlyArray<string>;
    readonly donts: ReadonlyArray<string>;
    readonly performanceTips: ReadonlyArray<string>;
  };
  readonly relatedNodes: ReadonlyArray<string>;
  readonly externalLinks: ReadonlyArray<{
    readonly title: string;
    readonly url: string;
    readonly description: string;
  }>;
}

interface NodeDocumentationTemplateProps {
  readonly data: NodeDocumentationData;
}

export function NodeDocumentationTemplate({
  data,
}: Readonly<NodeDocumentationTemplateProps>): React.JSX.Element {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const handleCopyCode = useCallback(async (code: string, exampleTitle: string) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedCode(exampleTitle);
      setTimeout(() => setCopiedCode(null), 2000);
    } catch (error) {
      console.error('Failed to copy code:', error);
    }
  }, []);

  const getSeverityIcon = (severity: TroubleshootingItem['severity']) => {
    switch (severity) {
      case 'high':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'medium':
        return <Info className="w-4 h-4 text-yellow-500" />;
      case 'low':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-8">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <Settings className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            {data.title}
          </h1>
        </div>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-6">
          {data.description}
        </p>
        
        {/* Quick Actions */}
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Zap className="w-4 h-4 mr-2" />
            Quick Start Guide
          </button>
          <button
            type="button"
            className="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            <Copy className="w-4 h-4 mr-2" />
            Copy Example
          </button>
        </div>
      </header>

      {/* Table of Contents */}
      <nav className="mb-8 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
          Table of Contents
        </h2>
        <ul className="grid grid-cols-2 gap-2 text-sm">
          <li><a href="#overview" className="text-blue-600 dark:text-blue-400 hover:underline">Overview</a></li>
          <li><a href="#configuration" className="text-blue-600 dark:text-blue-400 hover:underline">Configuration Guide</a></li>
          <li><a href="#parameters" className="text-blue-600 dark:text-blue-400 hover:underline">Parameters Reference</a></li>
          <li><a href="#examples" className="text-blue-600 dark:text-blue-400 hover:underline">Examples</a></li>
          <li><a href="#troubleshooting" className="text-blue-600 dark:text-blue-400 hover:underline">Troubleshooting</a></li>
          <li><a href="#best-practices" className="text-blue-600 dark:text-blue-400 hover:underline">Best Practices</a></li>
        </ul>
      </nav>

      {/* Overview Section */}
      <section id="overview" className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          📋 Overview
        </h2>
        <p className="text-gray-700 dark:text-gray-300 mb-6">
          {data.overview}
        </p>

        {/* Features */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
            Key Features
          </h3>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {data.features.map((feature, index) => (
              <li key={index} className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span className="text-gray-700 dark:text-gray-300">{feature}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Use Cases */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
            When to Use This Node
          </h3>
          <ul className="space-y-2">
            {data.useCases.map((useCase, index) => (
              <li key={index} className="flex items-start space-x-2">
                <Lightbulb className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
                <span className="text-gray-700 dark:text-gray-300">{useCase}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Configuration Guide */}
      <section id="configuration" className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          ⚙️ Configuration Guide
        </h2>
        
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">
            Quick Start
          </h3>
          <ol className="list-decimal list-inside space-y-1 text-blue-800 dark:text-blue-200">
            <li>Drag the {data.title} from the node palette</li>
            <li>Connect input/output handles as required</li>
            <li>Double-click to open properties</li>
            <li>Configure essential parameters</li>
            <li>Test connection (if applicable)</li>
          </ol>
        </div>

        <div className="prose dark:prose-invert max-w-none">
          <h3>Detailed Setup</h3>
          <p>
            This section provides step-by-step instructions for configuring the {data.title} node.
            Follow these steps to ensure proper setup and optimal performance.
          </p>
          
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
            <p className="text-yellow-800 dark:text-yellow-200 mb-0">
              <strong>Note:</strong> This is a placeholder documentation page. 
              Detailed configuration instructions will be added in Phase 2 of the development process.
            </p>
          </div>
        </div>
      </section>

      {/* Parameters Reference */}
      <section id="parameters" className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          📊 Parameters Reference
        </h2>
        
        <div className="overflow-x-auto">
          <table className="w-full border border-gray-200 dark:border-gray-700 rounded-lg">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-900 dark:text-gray-100">
                  Parameter
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-900 dark:text-gray-100">
                  Type
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-900 dark:text-gray-100">
                  Default
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-900 dark:text-gray-100">
                  Range
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-900 dark:text-gray-100">
                  Description
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {data.parameters.map((param, index) => (
                <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td className="px-4 py-3">
                    <div className="flex items-center space-x-2">
                      <code className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-sm">
                        {param.name}
                      </code>
                      {param.required && (
                        <span className="text-red-500 text-xs">*</span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    {param.type}
                  </td>
                  <td className="px-4 py-3">
                    <code className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-sm">
                      {param.defaultValue}
                    </code>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    {param.range || '-'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
                    {param.description}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Examples */}
      <section id="examples" className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          💡 Examples
        </h2>
        
        <div className="space-y-6">
          {data.examples.map((example, index) => (
            <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg">
              <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {example.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {example.description}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => handleCopyCode(example.code, example.title)}
                  className={cn(
                    'inline-flex items-center px-3 py-2 text-sm rounded-md transition-colors',
                    copiedCode === example.title
                      ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  )}
                >
                  <Copy className="w-4 h-4 mr-2" />
                  {copiedCode === example.title ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <div className="p-4">
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                  <code className={`language-${example.language}`}>
                    {example.code}
                  </code>
                </pre>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Troubleshooting */}
      <section id="troubleshooting" className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          🔧 Troubleshooting
        </h2>
        
        <div className="space-y-4">
          {data.troubleshooting.map((item, index) => (
            <div
              key={index}
              className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
            >
              <div className="flex items-start space-x-3">
                {getSeverityIcon(item.severity)}
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                    {item.issue}
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Symptoms:
                      </h4>
                      <p className="text-gray-600 dark:text-gray-400">
                        {item.symptoms}
                      </p>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Cause:
                      </h4>
                      <p className="text-gray-600 dark:text-gray-400">
                        {item.cause}
                      </p>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Solution:
                      </h4>
                      <p className="text-gray-600 dark:text-gray-400">
                        {item.solution}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Best Practices */}
      <section id="best-practices" className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          ✅ Best Practices
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Do's */}
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-green-900 dark:text-green-100 mb-3">
              ✅ Do&apos;s
            </h3>
            <ul className="space-y-2">
              {data.bestPractices.dos.map((item, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                  <span className="text-green-800 dark:text-green-200 text-sm">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Don&apos;ts */}
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-red-900 dark:text-red-100 mb-3">
              ❌ Don&apos;ts
            </h3>
            <ul className="space-y-2">
              {data.bestPractices.donts.map((item, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <AlertTriangle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
                  <span className="text-red-800 dark:text-red-200 text-sm">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Performance Tips */}
        <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">
            ⚡ Performance Tips
          </h3>
          <ul className="space-y-2">
            {data.bestPractices.performanceTips.map((tip, index) => (
              <li key={index} className="flex items-start space-x-2">
                <Zap className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
                <span className="text-blue-800 dark:text-blue-200 text-sm">{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Related Nodes */}
      {data.relatedNodes.length > 0 && (
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            🔗 Related Nodes
          </h2>
          <div className="flex flex-wrap gap-2">
            {data.relatedNodes.map((nodeType, index) => (
              <Link
                key={index}
                href={`/docs/nodes/${nodeType}`}
                className="inline-flex items-center px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                {nodeType}
                <ExternalLink className="w-3 h-3 ml-2" />
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* External Links */}
      {data.externalLinks.length > 0 && (
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            📚 External Resources
          </h2>
          <div className="space-y-3">
            {data.externalLinks.map((link, index) => (
              <a
                key={index}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                      {link.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {link.description}
                    </p>
                  </div>
                  <ExternalLink className="w-5 h-5 text-gray-400" />
                </div>
              </a>
            ))}
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="pt-8 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
          <p>
            Last updated: {new Date().toLocaleDateString()}
          </p>
          <div className="flex items-center space-x-4">
            <button
              type="button"
              className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            >
              Report Issue
            </button>
            <button
              type="button"
              className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            >
              Suggest Edit
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}

export type { NodeDocumentationData, ParameterReference, CodeExample, TroubleshootingItem };
