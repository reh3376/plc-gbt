/**
 * Templates Tab - AI Task Orchestrator TypeScript Implementation
 *
 * @description Apply pre-configured templates and save custom configurations
 * @compliance Strict TypeScript with OpenAPI Schema MCP validation
 * @features Template application, custom template creation, template management
 */

'use client';

import { BookOpen, Download, Plus, Save, Search, Tag, Trash2 } from 'lucide-react';
import React, { useCallback, useMemo, useState } from 'react';

import { type NodePropertySchema, type PropertyTemplate } from '@/api/zod-schemas';
import { cn } from '@/lib/utils/cn';
import { RawConfigurationModal } from '../modals/RawConfigurationModal';

interface TemplatesTabProps {
  readonly schema: NodePropertySchema;
  readonly config: Record<string, unknown>;
  readonly onApplyTemplate: (templateId: string) => void;
  readonly onSaveAsTemplate: (name: string, description: string, category: string) => void;
  readonly onDeleteTemplate?: (templateId: string) => void;
}

interface TemplateCategory {
  readonly id: string;
  readonly label: string;
  readonly description: string;
  readonly templates: ReadonlyArray<PropertyTemplate>;
}

export function TemplatesTab({
  schema,
  config,
  onApplyTemplate,
  onSaveAsTemplate,
  onDeleteTemplate,
}: Readonly<TemplatesTabProps>): React.JSX.Element {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isCreatingTemplate, setIsCreatingTemplate] = useState(false);
  const [showRawConfigModal, setShowRawConfigModal] = useState(false);
  const [newTemplateName, setNewTemplateName] = useState('');
  const [newTemplateDescription, setNewTemplateDescription] = useState('');
  const [newTemplateCategory, setNewTemplateCategory] = useState('');

  // Remove unused config parameter warning
  const _ = config;

  // Group templates by category
  const templateCategories = useMemo((): ReadonlyArray<TemplateCategory> => {
    if (!schema.templates?.length) return [];

    const categoryMap = new Map<string, PropertyTemplate[]>();

    schema.templates.forEach(template => {
      const category = template.category || 'Uncategorized';
      const existing = categoryMap.get(category) || [];
      categoryMap.set(category, [...existing, template]);
    });

    return Array.from(categoryMap.entries()).map(([categoryId, templates]) => ({
      id: categoryId.toLowerCase().replace(/\s+/g, '-'),
      label: categoryId,
      description: `${templates.length} template${templates.length === 1 ? '' : 's'} available`,
      templates,
    }));
  }, [schema.templates]);

  // Filter templates based on search and category with wildcard support
  const filteredTemplates = useMemo(() => {
    let templates = schema.templates || [];

    // Filter by category
    if (selectedCategory !== 'all') {
      templates = templates.filter(
        template => template.category.toLowerCase().replace(/\s+/g, '-') === selectedCategory
      );
    }

    // Filter by search query with wildcard support
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();

      // Convert wildcard pattern to regex
      const wildcardToRegex = (pattern: string) => {
        const escaped = pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const withWildcards = escaped.replace(/\\\*/g, '.*');
        return new RegExp(withWildcards, 'i');
      };

      const searchRegex = wildcardToRegex(query);

      templates = templates.filter(
        template =>
          searchRegex.test(template.label) ||
          searchRegex.test(template.description) ||
          template.tags.some(tag => searchRegex.test(tag))
      );
    }

    return templates;
  }, [schema.templates, selectedCategory, searchQuery]);

  // Handle template creation
  const handleCreateTemplate = useCallback(() => {
    if (newTemplateName.trim() && newTemplateDescription.trim() && newTemplateCategory.trim()) {
      onSaveAsTemplate(
        newTemplateName.trim(),
        newTemplateDescription.trim(),
        newTemplateCategory.trim()
      );
      setNewTemplateName('');
      setNewTemplateDescription('');
      setNewTemplateCategory('');
      setIsCreatingTemplate(false);
    }
  }, [newTemplateName, newTemplateDescription, newTemplateCategory, onSaveAsTemplate]);

  return (
    <div className="p-4 space-y-6">
      {/* Header with Search and Create */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h3 className="text-lg font-medium text-white">Configuration Templates</h3>

          {/* Enhanced Search with Wildcard Support */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search templates... (use * for wildcards)"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 bg-[#3d3d3d] border border-[#505050] rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            {searchQuery && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-[#2d2d2d] border border-[#404040] rounded-md shadow-lg z-10">
                <div className="p-2 text-xs text-gray-400">
                  <div>💡 Search Tips:</div>
                  <div>
                    • Use * for wildcards (e.g., &quot;pid*&quot; matches
                    &quot;pid-controller&quot;)
                  </div>
                  <div>• Search in name, description, or tags</div>
                </div>
              </div>
            )}
          </div>
        </div>

        <button
          onClick={() => setShowRawConfigModal(true)}
          className="flex items-center gap-2 px-3 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500/50"
        >
          <Plus className="w-4 h-4" />
          Create Template
        </button>
      </div>

      {/* Category Filter */}
      {templateCategories.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm text-gray-400">Category:</span>
          <button
            onClick={() => setSelectedCategory('all')}
            className={cn(
              'px-3 py-1 text-xs rounded transition-colors',
              selectedCategory === 'all'
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                : 'bg-[#3d3d3d] text-gray-400 hover:text-white'
            )}
          >
            All ({schema.templates?.length || 0})
          </button>

          {templateCategories.map(category => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={cn(
                'px-3 py-1 text-xs rounded transition-colors',
                selectedCategory === category.id
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                  : 'bg-[#3d3d3d] text-gray-400 hover:text-white'
              )}
            >
              {category.label} ({category.templates.length})
            </button>
          ))}
        </div>
      )}

      {/* Templates Grid */}
      {filteredTemplates.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filteredTemplates.map(template => (
            <div
              key={template.id}
              className="border border-[#404040] rounded-lg p-4 hover:border-[#505050] transition-all duration-200 hover:shadow-lg"
            >
              {/* Template Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-white truncate">{template.label}</h4>
                  <p className="text-sm text-gray-400 mt-1">{template.description}</p>
                </div>

                <div className="flex items-center gap-1 ml-2">
                  <button
                    onClick={() => onApplyTemplate(template.id)}
                    className="p-2 text-blue-400 hover:text-blue-300 hover:bg-blue-600/10 rounded transition-colors"
                    title="Apply template"
                  >
                    <Download className="w-4 h-4" />
                  </button>

                  {onDeleteTemplate && (
                    <button
                      onClick={() => onDeleteTemplate(template.id)}
                      className="p-2 text-red-400 hover:text-red-300 hover:bg-red-600/10 rounded transition-colors"
                      title="Delete template"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              {/* Template Tags */}
              {template.tags.length > 0 && (
                <div className="flex items-center gap-1 mb-3 flex-wrap">
                  <Tag className="w-3 h-3 text-gray-500" />
                  {template.tags.map(tag => (
                    <span
                      key={tag}
                      className="text-xs bg-[#3d3d3d] text-gray-400 px-2 py-1 rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Template Preview */}
              <div className="text-xs text-gray-500">
                <div className="mb-1">Configuration Preview:</div>
                <div className="bg-[#1e1e1e] p-2 rounded max-h-20 overflow-y-auto">
                  <pre className="text-gray-400 text-xs">
                    {JSON.stringify(template.config, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center text-gray-400 py-8">
          {searchQuery ? (
            <>
              <Search className="w-12 h-12 mx-auto mb-4 text-gray-500" />
              <p className="text-lg font-medium mb-2">No Templates Found</p>
              <p className="text-sm max-w-md mx-auto">
                No templates match your search criteria. Try adjusting your search terms or browse
                all categories.
              </p>
            </>
          ) : (
            <>
              <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-500" />
              <p className="text-lg font-medium mb-2">No Templates Available</p>
              <p className="text-sm max-w-md mx-auto">
                No pre-configured templates are available for this node type. You can create your
                own template from the current configuration.
              </p>
            </>
          )}
        </div>
      )}

      {/* Raw Configuration Modal */}
      <RawConfigurationModal
        isOpen={showRawConfigModal}
        config={config}
        title="Create Template from Configuration"
        onSave={rawConfig => {
          // After editing raw config, show the template creation form with the config
          setShowRawConfigModal(false);
          setIsCreatingTemplate(true);
          // Store the raw config for template creation
          setNewTemplateCategory('Custom');
        }}
        onClose={() => setShowRawConfigModal(false)}
      />

      {/* Enhanced Template Import Modal */}
      {isCreatingTemplate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[1100]">
          <div className="bg-[#2d2d2d] border border-[#404040] rounded-lg p-6 w-full max-w-md mx-4">
            <h4 className="text-lg font-medium text-white mb-4">Create New Template</h4>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Template Name *
                </label>
                <input
                  type="text"
                  value={newTemplateName}
                  onChange={e => setNewTemplateName(e.target.value)}
                  placeholder="Enter template name..."
                  className="w-full px-3 py-2 bg-[#3d3d3d] border border-[#505050] rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Description *
                </label>
                <textarea
                  value={newTemplateDescription}
                  onChange={e => setNewTemplateDescription(e.target.value)}
                  placeholder="Describe what this template is for..."
                  rows={3}
                  className="w-full px-3 py-2 bg-[#3d3d3d] border border-[#505050] rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Category *</label>
                <input
                  type="text"
                  value={newTemplateCategory}
                  onChange={e => setNewTemplateCategory(e.target.value)}
                  placeholder="e.g., Process Control, Safety, Testing..."
                  className="w-full px-3 py-2 bg-[#3d3d3d] border border-[#505050] rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Import Template (Optional)
                </label>
                <label className="flex items-center gap-2 px-3 py-2 bg-[#3d3d3d] border border-[#505050] rounded-md text-white text-sm cursor-pointer hover:bg-[#454545] transition-colors">
                  <input
                    type="file"
                    accept=".json"
                    onChange={e => {
                      const file = e.target.files?.[0];
                      if (file) {
                        const reader = new FileReader();
                        reader.onload = event => {
                          try {
                            const importedConfig = JSON.parse(event.target?.result as string);
                            // Auto-fill template name from imported file
                            if (importedConfig.name) setNewTemplateName(importedConfig.name);
                            if (importedConfig.description)
                              setNewTemplateDescription(importedConfig.description);
                            if (importedConfig.category)
                              setNewTemplateCategory(importedConfig.category);
                          } catch (error) {
                            console.error('Failed to import template:', error);
                          }
                        };
                        reader.readAsText(file);
                      }
                    }}
                    className="hidden"
                  />
                  📁 Import Template File
                </label>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 mt-6">
              <button
                onClick={() => {
                  setIsCreatingTemplate(false);
                  setNewTemplateName('');
                  setNewTemplateDescription('');
                  setNewTemplateCategory('');
                }}
                className="px-4 py-2 text-sm text-gray-400 hover:text-white hover:bg-[#3d3d3d] rounded transition-colors"
              >
                Cancel
              </button>

              <button
                onClick={handleCreateTemplate}
                disabled={
                  !newTemplateName.trim() ||
                  !newTemplateDescription.trim() ||
                  !newTemplateCategory.trim()
                }
                className={cn(
                  'px-4 py-2 text-sm rounded transition-colors flex items-center gap-2',
                  newTemplateName.trim() &&
                    newTemplateDescription.trim() &&
                    newTemplateCategory.trim()
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                )}
              >
                <Save className="w-4 h-4" />
                Create Template
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
