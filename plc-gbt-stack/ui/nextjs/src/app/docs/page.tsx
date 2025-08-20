/**
 * Documentation Home Page - AI Task Orchestrator TypeScript Implementation
 *
 * @description Main documentation landing page with navigation to all sections
 * @compliance Strict TypeScript - zero `any` types policy
 * @features Overview, quick navigation, search functionality
 */

'use client';

import { ArrowRight, BookOpen, Cog, Database, Zap } from 'lucide-react';
import Link from 'next/link';
import React from 'react';

import { cn } from '@/lib/utils/cn';

interface DocSection {
  readonly title: string;
  readonly description: string;
  readonly href: string;
  readonly icon: React.ComponentType<{ className?: string }>;
  readonly nodeCount: number;
  readonly status: 'complete' | 'in-progress' | 'planned';
}

const DOCUMENTATION_SECTIONS: ReadonlyArray<DocSection> = [
  {
    title: 'Industrial Nodes',
    description: 'Comprehensive documentation for all industrial automation nodes',
    href: '/docs/nodes',
    icon: Cog,
    nodeCount: 36,
    status: 'in-progress',
  },
  {
    title: 'API Reference',
    description: 'OpenAPI schema documentation and endpoint reference',
    href: '/docs/api',
    icon: Database,
    nodeCount: 12,
    status: 'planned',
  },
  {
    title: 'Getting Started',
    description: 'Quick start guides and tutorials for new users',
    href: '/docs/getting-started',
    icon: Zap,
    nodeCount: 5,
    status: 'planned',
  },
  {
    title: 'User Guides',
    description: 'Step-by-step guides for common workflows and use cases',
    href: '/docs/guides',
    icon: BookOpen,
    nodeCount: 8,
    status: 'planned',
  },
];

export default function DocumentationHome(): React.JSX.Element {
  const getStatusBadge = (status: DocSection['status']) => {
    switch (status) {
      case 'complete':
        return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
      case 'in-progress':
        return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200';
      case 'planned':
        return 'bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200';
    }
  };

  const getStatusText = (status: DocSection['status']) => {
    switch (status) {
      case 'complete':
        return 'Complete';
      case 'in-progress':
        return 'In Progress';
      case 'planned':
        return 'Planned';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Hero Section */}
      <section className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <BookOpen className="w-16 h-16 text-blue-600 dark:text-blue-400 mx-auto mb-6" />
            <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              PLC-GBT Documentation
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-3xl mx-auto">
              Complete documentation for industrial automation, process control, and workflow management 
              in the PLC-GBT system. Built with AI Task Orchestrator methodology.
            </p>
            
            <div className="flex items-center justify-center space-x-4">
              <Link
                href="/docs/nodes"
                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Cog className="w-5 h-5 mr-2" />
                Browse Nodes
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
              
              <Link
                href="/workflow"
                className="inline-flex items-center px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Back to Workflow
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Documentation Sections */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {DOCUMENTATION_SECTIONS.map((section) => (
            <Link
              key={section.href}
              href={section.href}
              className="group block bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-lg transition-all duration-200"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <section.icon className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                    {section.title}
                  </h3>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className={cn(
                    'px-2 py-1 text-xs rounded-full',
                    getStatusBadge(section.status)
                  )}>
                    {getStatusText(section.status)}
                  </span>
                  <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" />
                </div>
              </div>
              
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {section.description}
              </p>
              
              <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                <span>{section.nodeCount} items</span>
                <span className="text-blue-600 dark:text-blue-400 group-hover:text-blue-700 dark:group-hover:text-blue-300">
                  Explore Section →
                </span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Development Status */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-blue-900 dark:text-blue-100 mb-4">
            📋 Development Status - Sub-Phase 1.5
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <h3 className="font-semibold text-green-700 dark:text-green-300 mb-2">
                ✅ Completed
              </h3>
              <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• CircleHelp icon system</li>
                <li>• Tooltip infrastructure</li>
                <li>• 36 placeholder pages</li>
                <li>• Documentation routing</li>
              </ul>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <h3 className="font-semibold text-blue-700 dark:text-blue-300 mb-2">
                🔄 Next: Phase 1.6
              </h3>
              <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Template-driven node creation</li>
                <li>• Automated property generation</li>
                <li>• Validation templates</li>
                <li>• Connection test framework</li>
              </ul>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <h3 className="font-semibold text-yellow-700 dark:text-yellow-300 mb-2">
                📋 Phase 2: Planned
              </h3>
              <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Detailed content creation</li>
                <li>• Interactive examples</li>
                <li>• Advanced tutorials</li>
                <li>• Search functionality</li>
              </ul>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <h3 className="font-semibold text-purple-700 dark:text-purple-300 mb-2">
                🚀 Phase 3: Future
              </h3>
              <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Scientific calculator</li>
                <li>• Advanced features</li>
                <li>• Community integration</li>
                <li>• Production optimization</li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
