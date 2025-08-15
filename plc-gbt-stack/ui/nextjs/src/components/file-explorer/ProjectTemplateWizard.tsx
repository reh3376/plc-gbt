/**
 * Project Template Wizard Component - File Explorer Enhancement
 * AI Task Orchestrator Generated - Strict TypeScript Compliance
 *
 * @description Multi-step wizard for creating new PLC projects with schema-driven UI generation
 * @compliance Zero 'any' types, comprehensive type safety
 * @features Template selection, validation, preview, and project scaffolding
 */

'use client';

import { cn } from '@/lib/utils/cn';
import {
  AlertCircle,
  Check,
  ChevronLeft,
  ChevronRight,
  FileCode,
  FileText,
  Folder,
  Loader2,
  Package,
  Settings,
  Sparkles,
  X,
} from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { z } from 'zod';

// ===== TYPE DEFINITIONS =====

/**
 * Project template types aligned with PLC types
 */
export type ProjectTemplateType =
  | 'controllogix-standard'
  | 'compactlogix-standard'
  | 'slc500-migration'
  | 'plc5-migration'
  | 'micrologix-simple'
  | 'distillation-control'
  | 'batch-process'
  | 'motion-control'
  | 'safety-instrumented'
  | 'scada-integration'
  | 'custom';

/**
 * Template metadata with schema-driven properties
 */
export interface ProjectTemplate {
  id: ProjectTemplateType;
  name: string;
  description: string;
  category: 'standard' | 'industry' | 'migration' | 'custom';
  plcType: 'ControlLogix' | 'CompactLogix' | 'SLC500' | 'PLC5' | 'MicroLogix';
  icon: React.ComponentType<{ className?: string }>;
  features: string[];
  requiredFields: ProjectFieldDefinition[];
  optionalFields?: ProjectFieldDefinition[];
  fileStructure: TemplateFileStructure[];
  estimatedSize: string;
  complexity: 'simple' | 'moderate' | 'complex';
}

/**
 * Field definition for schema-driven form generation
 */
export interface ProjectFieldDefinition {
  id: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'multiselect' | 'boolean' | 'file';
  placeholder?: string;
  defaultValue?: string | number | boolean | string[];
  validation?: z.ZodType<unknown>;
  options?: Array<{ value: string; label: string }>;
  description?: string;
  dependsOn?: {
    field: string;
    value: unknown;
  };
}

/**
 * Template file structure definition
 */
export interface TemplateFileStructure {
  name: string;
  type: 'file' | 'folder';
  template?: string; // Template content for files
  children?: TemplateFileStructure[];
  variables?: string[]; // Variables to replace in template
}

/**
 * Wizard step definition
 */
export interface WizardStep {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

/**
 * Project creation data collected through wizard
 */
export interface ProjectCreationData {
  name: string;
  template: ProjectTemplateType;
  parentPath: string;
  fields: Record<string, unknown>;
}

// ===== TEMPLATE DEFINITIONS =====

const projectTemplates: ProjectTemplate[] = [
  {
    id: 'controllogix-standard',
    name: 'ControlLogix Standard',
    description: 'Standard template for ControlLogix controllers with basic program structure',
    category: 'standard',
    plcType: 'ControlLogix',
    icon: Package,
    features: ['Main Program', 'Standard Tags', 'Basic HMI Interface', 'Alarm Management'],
    requiredFields: [
      {
        id: 'projectName',
        label: 'Project Name',
        type: 'text',
        placeholder: 'e.g., PlantControl_Main',
        validation: z
          .string()
          .min(3)
          .max(50)
          .regex(/^[a-zA-Z][a-zA-Z0-9_]*$/),
        description: 'Project name (alphanumeric and underscore only)',
      },
      {
        id: 'controllerName',
        label: 'Controller Name',
        type: 'text',
        placeholder: 'e.g., CTRL_01',
        validation: z.string().min(3).max(40),
      },
      {
        id: 'processorType',
        label: 'Processor Type',
        type: 'select',
        options: [
          { value: '1756-L71', label: '1756-L71' },
          { value: '1756-L72', label: '1756-L72' },
          { value: '1756-L73', label: '1756-L73' },
          { value: '1756-L74', label: '1756-L74' },
          { value: '1756-L75', label: '1756-L75' },
        ],
        defaultValue: '1756-L73',
      },
    ],
    optionalFields: [
      {
        id: 'enableRedundancy',
        label: 'Enable Redundancy',
        type: 'boolean',
        defaultValue: false,
        description: 'Configure controller redundancy',
      },
      {
        id: 'ioModules',
        label: 'I/O Modules',
        type: 'multiselect',
        options: [
          { value: '1756-IB16', label: 'Digital Input (1756-IB16)' },
          { value: '1756-OB16E', label: 'Digital Output (1756-OB16E)' },
          { value: '1756-IF8', label: 'Analog Input (1756-IF8)' },
          { value: '1756-OF8', label: 'Analog Output (1756-OF8)' },
        ],
      },
    ],
    fileStructure: [
      {
        name: '{{projectName}}',
        type: 'folder',
        children: [
          {
            name: 'acd-current',
            type: 'folder',
            children: [
              {
                name: 'main',
                type: 'folder',
                children: [
                  {
                    name: '{{projectName}}_Main.acd',
                    type: 'file',
                    template: 'controllogix-main-template',
                  },
                ],
              },
            ],
          },
          {
            name: 'documentation',
            type: 'folder',
            children: [
              {
                name: 'README.md',
                type: 'file',
                template:
                  '# {{projectName}}\n\nControlLogix project created on {{date}}\n\nController: {{controllerName}}\nProcessor: {{processorType}}',
              },
            ],
          },
          {
            name: 'plc',
            type: 'folder',
            children: [
              { name: 'routines', type: 'folder' },
              { name: 'tags', type: 'folder' },
              { name: 'dataTypes', type: 'folder' },
              { name: 'alarms', type: 'folder' },
            ],
          },
        ],
      },
    ],
    estimatedSize: '~5 MB',
    complexity: 'simple',
  },
  {
    id: 'distillation-control',
    name: 'Distillation Control',
    description:
      'Advanced template for distillation column control with PID loops and cascade control',
    category: 'industry',
    plcType: 'ControlLogix',
    icon: Sparkles,
    features: [
      'Multi-loop PID Control',
      'Cascade Control Strategy',
      'Feed-forward Control',
      'Alarm Management',
      'HMI Templates',
      'Trending Configuration',
    ],
    requiredFields: [
      {
        id: 'projectName',
        label: 'Project Name',
        type: 'text',
        placeholder: 'e.g., Distillation_Column_01',
        validation: z
          .string()
          .min(3)
          .max(50)
          .regex(/^[a-zA-Z][a-zA-Z0-9_]*$/),
      },
      {
        id: 'columnType',
        label: 'Column Type',
        type: 'select',
        options: [
          { value: 'binary', label: 'Binary Distillation' },
          { value: 'multicomponent', label: 'Multi-component' },
          { value: 'extractive', label: 'Extractive Distillation' },
          { value: 'azeotropic', label: 'Azeotropic Distillation' },
        ],
        defaultValue: 'binary',
      },
      {
        id: 'numberOfTrays',
        label: 'Number of Trays',
        type: 'number',
        defaultValue: 30,
        validation: z.number().min(10).max(100),
      },
    ],
    optionalFields: [
      {
        id: 'temperatureLoops',
        label: 'Temperature Control Loops',
        type: 'number',
        defaultValue: 3,
        validation: z.number().min(1).max(10),
      },
      {
        id: 'pressureControl',
        label: 'Pressure Control Type',
        type: 'select',
        options: [
          { value: 'condenser', label: 'Condenser Control' },
          { value: 'reboiler', label: 'Reboiler Control' },
          { value: 'split-range', label: 'Split Range Control' },
        ],
      },
    ],
    fileStructure: [
      {
        name: '{{projectName}}',
        type: 'folder',
        children: [
          {
            name: 'acd-current',
            type: 'folder',
            children: [
              {
                name: 'main',
                type: 'folder',
                children: [
                  {
                    name: '{{projectName}}_Control.acd',
                    type: 'file',
                    template: 'distillation-control-template',
                  },
                ],
              },
            ],
          },
          {
            name: 'plc',
            type: 'folder',
            children: [
              {
                name: 'routines',
                type: 'folder',
                children: [
                  { name: 'PID_Control', type: 'folder' },
                  { name: 'Cascade_Control', type: 'folder' },
                  { name: 'Sequencing', type: 'folder' },
                  { name: 'Alarms', type: 'folder' },
                ],
              },
            ],
          },
        ],
      },
    ],
    estimatedSize: '~15 MB',
    complexity: 'complex',
  },
];

// ===== WIZARD STEPS =====

const wizardSteps: WizardStep[] = [
  {
    id: 'template',
    title: 'Select Template',
    description: 'Choose a project template that matches your requirements',
    icon: FileCode,
  },
  {
    id: 'configuration',
    title: 'Configure Project',
    description: 'Set up project-specific parameters and options',
    icon: Settings,
  },
  {
    id: 'review',
    title: 'Review & Create',
    description: 'Review your configuration and create the project',
    icon: Check,
  },
];

// ===== COMPONENT PROPS =====

interface ProjectTemplateWizardProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateProject: (data: ProjectCreationData) => Promise<void>;
  parentPath: string;
}

// ===== MAIN COMPONENT =====

export function ProjectTemplateWizard({
  isOpen,
  onClose,
  onCreateProject,
  parentPath,
}: ProjectTemplateWizardProps) {
  // State management
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedTemplate, setSelectedTemplate] = useState<ProjectTemplateType | null>(null);
  const [formData, setFormData] = useState<Record<string, unknown>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isCreating, setIsCreating] = useState(false);
  const [announcement, setAnnouncement] = useState('');

  // Refs for focus management
  const wizardRef = useRef<HTMLDivElement>(null);
  const headingRef = useRef<HTMLHeadingElement>(null);

  // Get current template details
  const currentTemplate = selectedTemplate
    ? projectTemplates.find(t => t.id === selectedTemplate)
    : null;

  // Reset wizard when closed
  useEffect(() => {
    if (!isOpen) {
      setCurrentStep(0);
      setSelectedTemplate(null);
      setFormData({});
      setErrors({});
      setIsCreating(false);
    }
  }, [isOpen]);

  // Focus management for accessibility
  useEffect(() => {
    if (isOpen && headingRef.current) {
      headingRef.current.focus();
    }
  }, [isOpen, currentStep]);

  // Announce step changes for screen readers
  useEffect(() => {
    if (isOpen && currentStep >= 0) {
      const step = wizardSteps[currentStep];
      setAnnouncement(`Step ${currentStep + 1} of ${wizardSteps.length}: ${step.title}`);
    }
  }, [currentStep, isOpen]);

  // Validate field based on schema
  const validateField = useCallback(
    (field: ProjectFieldDefinition, value: unknown): string | null => {
      if (!field.validation) return null;

      try {
        field.validation.parse(value);
        return null;
      } catch (error) {
        if (error instanceof z.ZodError) {
          return error.issues[0]?.message || 'Invalid value';
        }
        return 'Validation error';
      }
    },
    []
  );

  // Handle field change with validation
  const handleFieldChange = useCallback(
    (fieldId: string, value: unknown) => {
      setFormData(prev => ({ ...prev, [fieldId]: value }));

      // Find field definition
      const field =
        currentTemplate?.requiredFields.find(f => f.id === fieldId) ||
        currentTemplate?.optionalFields?.find(f => f.id === fieldId);

      if (field) {
        const error = validateField(field, value);
        setErrors(prev => {
          if (error) {
            return { ...prev, [fieldId]: error };
          }
          // Remove the error for this field if validation passes
          const updated = { ...prev };
          delete updated[fieldId];
          return updated;
        });
      }
    },
    [currentTemplate, validateField]
  );

  // Validate all fields
  const validateAllFields = useCallback((): boolean => {
    if (!currentTemplate) return false;

    const newErrors: Record<string, string> = {};
    let isValid = true;

    // Validate required fields
    currentTemplate.requiredFields.forEach(field => {
      const value = formData[field.id];
      const error = validateField(field, value);

      if (!value && field.type !== 'boolean') {
        newErrors[field.id] = 'This field is required';
        isValid = false;
      } else if (error) {
        newErrors[field.id] = error;
        isValid = false;
      }
    });

    // Validate optional fields if provided
    currentTemplate.optionalFields?.forEach(field => {
      const value = formData[field.id];
      if (value !== undefined && value !== '') {
        const error = validateField(field, value);
        if (error) {
          newErrors[field.id] = error;
          isValid = false;
        }
      }
    });

    setErrors(newErrors);
    return isValid;
  }, [currentTemplate, formData, validateField]);

  // Navigate between steps
  const goToNextStep = useCallback(() => {
    if (currentStep === 0 && !selectedTemplate) {
      setErrors({ template: 'Please select a template' });
      return;
    }

    if (currentStep === 1 && !validateAllFields()) {
      return;
    }

    if (currentStep < wizardSteps.length - 1) {
      setCurrentStep(prev => prev + 1);
    }
  }, [currentStep, selectedTemplate, validateAllFields]);

  const goToPreviousStep = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  }, [currentStep]);

  // Create project
  const handleCreateProject = useCallback(async () => {
    if (!selectedTemplate || !validateAllFields()) return;

    setIsCreating(true);
    try {
      const projectData: ProjectCreationData = {
        name: formData.projectName as string,
        template: selectedTemplate,
        parentPath,
        fields: formData,
      };

      await onCreateProject(projectData);
      setAnnouncement('Project created successfully');
      onClose();
    } catch (error) {
      setErrors({
        create: error instanceof Error ? error.message : 'Failed to create project',
      });
      setAnnouncement('Failed to create project');
    } finally {
      setIsCreating(false);
    }
  }, [selectedTemplate, formData, parentPath, onCreateProject, onClose, validateAllFields]);

  // Render field based on type
  const renderField = (field: ProjectFieldDefinition) => {
    const value = formData[field.id];
    const error = errors[field.id];

    // Check dependencies
    if (field.dependsOn) {
      const dependentValue = formData[field.dependsOn.field];
      if (dependentValue !== field.dependsOn.value) {
        return null;
      }
    }

    switch (field.type) {
      case 'text':
        return (
          <div key={field.id} className="space-y-2">
            <label htmlFor={field.id} className="block text-sm font-medium text-[#cccccc]">
              {field.label}
            </label>
            <input
              id={field.id}
              type="text"
              value={(value as string) || ''}
              onChange={e => handleFieldChange(field.id, e.target.value)}
              placeholder={field.placeholder}
              className={cn(
                'w-full px-3 py-2 bg-[#3c3c3c] text-[#cccccc] rounded',
                'border focus:outline-none focus:ring-2 focus:ring-blue-500',
                error ? 'border-red-500' : 'border-[#555555]'
              )}
              aria-invalid={!!error}
              aria-describedby={error ? `${field.id}-error` : undefined}
              data-testid={`field-${field.id}`}
            />
            {field.description && !error && (
              <p className="text-xs text-[#969696]">{field.description}</p>
            )}
            {error && (
              <p id={`${field.id}-error`} className="text-xs text-red-500">
                {error}
              </p>
            )}
          </div>
        );

      case 'number':
        return (
          <div key={field.id} className="space-y-2">
            <label htmlFor={field.id} className="block text-sm font-medium text-[#cccccc]">
              {field.label}
            </label>
            <input
              id={field.id}
              type="number"
              value={((value as number) || field.defaultValue || '') as string | number}
              onChange={e => handleFieldChange(field.id, parseInt(e.target.value))}
              placeholder={field.placeholder}
              className={cn(
                'w-full px-3 py-2 bg-[#3c3c3c] text-[#cccccc] rounded',
                'border focus:outline-none focus:ring-2 focus:ring-blue-500',
                error ? 'border-red-500' : 'border-[#555555]'
              )}
              aria-invalid={!!error}
              aria-describedby={error ? `${field.id}-error` : undefined}
            />
            {error && (
              <p id={`${field.id}-error`} className="text-xs text-red-500">
                {error}
              </p>
            )}
          </div>
        );

      case 'select':
        return (
          <div key={field.id} className="space-y-2">
            <label htmlFor={field.id} className="block text-sm font-medium text-[#cccccc]">
              {field.label}
            </label>
            <select
              id={field.id}
              value={((value as string) || field.defaultValue || '') as string}
              onChange={e => handleFieldChange(field.id, e.target.value)}
              className={cn(
                'w-full px-3 py-2 bg-[#3c3c3c] text-[#cccccc] rounded',
                'border focus:outline-none focus:ring-2 focus:ring-blue-500',
                error ? 'border-red-500' : 'border-[#555555]'
              )}
              aria-invalid={!!error}
              aria-describedby={error ? `${field.id}-error` : undefined}
              data-testid={`field-${field.id}`}
            >
              <option value="">Select {field.label}</option>
              {field.options?.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {error && (
              <p id={`${field.id}-error`} className="text-xs text-red-500">
                {error}
              </p>
            )}
          </div>
        );

      case 'multiselect':
        return (
          <div key={field.id} className="space-y-2">
            <label className="block text-sm font-medium text-[#cccccc]">{field.label}</label>
            <div className="space-y-2 max-h-32 overflow-y-auto border border-[#555555] rounded p-2">
              {field.options?.map(option => (
                <label
                  key={option.value}
                  className="flex items-center space-x-2 cursor-pointer hover:bg-[#3c3c3c] p-1 rounded"
                >
                  <input
                    type="checkbox"
                    value={option.value}
                    checked={((value as string[]) || []).includes(option.value)}
                    onChange={e => {
                      const currentValues = (value as string[]) || [];
                      const newValues = e.target.checked
                        ? [...currentValues, option.value]
                        : currentValues.filter(v => v !== option.value);
                      handleFieldChange(field.id, newValues);
                    }}
                    className="rounded border-[#555555] bg-[#3c3c3c] text-blue-500 focus:ring-blue-500"
                  />
                  <span className="text-sm text-[#cccccc]">{option.label}</span>
                </label>
              ))}
            </div>
          </div>
        );

      case 'boolean':
        return (
          <div key={field.id} className="space-y-2">
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={(value as boolean) || false}
                onChange={e => handleFieldChange(field.id, e.target.checked)}
                className="rounded border-[#555555] bg-[#3c3c3c] text-blue-500 focus:ring-blue-500"
              />
              <span className="text-sm text-[#cccccc]">{field.label}</span>
            </label>
            {field.description && (
              <p className="text-xs text-[#969696] ml-6">{field.description}</p>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  // Render step content
  const renderStepContent = () => {
    switch (currentStep) {
      case 0: // Template selection
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-1 gap-4">
              {['standard', 'industry', 'migration'].map(category => {
                const categoryTemplates = projectTemplates.filter(t => t.category === category);
                if (categoryTemplates.length === 0) return null;

                return (
                  <div key={category}>
                    <h3 className="text-sm font-medium text-[#969696] mb-2 capitalize">
                      {category} Templates
                    </h3>
                    <div className="space-y-2">
                      {categoryTemplates.map(template => {
                        const Icon = template.icon;
                        const isSelected = selectedTemplate === template.id;

                        return (
                          <button
                            key={template.id}
                            onClick={() => {
                              setSelectedTemplate(template.id);
                              setErrors({});
                            }}
                            className={cn(
                              'w-full p-4 rounded-lg border text-left transition-all',
                              'hover:bg-[#3c3c3c] focus:outline-none focus:ring-2 focus:ring-blue-500',
                              isSelected
                                ? 'border-blue-500 bg-[#094771]'
                                : 'border-[#555555] bg-[#2d2d30]'
                            )}
                            aria-pressed={isSelected}
                            data-testid={`template-${template.id}`}
                          >
                            <div className="flex items-start space-x-3">
                              <Icon
                                className={cn(
                                  'w-5 h-5 mt-0.5 flex-shrink-0',
                                  isSelected ? 'text-white' : 'text-[#519aba]'
                                )}
                              />
                              <div className="flex-1 min-w-0">
                                <h4
                                  className={cn(
                                    'font-medium',
                                    isSelected ? 'text-white' : 'text-[#cccccc]'
                                  )}
                                >
                                  {template.name}
                                </h4>
                                <p
                                  className={cn(
                                    'text-sm mt-1',
                                    isSelected ? 'text-white/80' : 'text-[#969696]'
                                  )}
                                >
                                  {template.description}
                                </p>
                                <div className="flex items-center gap-4 mt-2 text-xs">
                                  <span
                                    className={cn(isSelected ? 'text-white/60' : 'text-[#969696]')}
                                  >
                                    {template.plcType}
                                  </span>
                                  <span
                                    className={cn(isSelected ? 'text-white/60' : 'text-[#969696]')}
                                  >
                                    {template.estimatedSize}
                                  </span>
                                  <span
                                    className={cn(
                                      'capitalize',
                                      isSelected ? 'text-white/60' : 'text-[#969696]'
                                    )}
                                  >
                                    {template.complexity}
                                  </span>
                                </div>
                                {isSelected && (
                                  <div className="mt-3 pt-3 border-t border-white/20">
                                    <p className="text-xs text-white/80 mb-2">Features:</p>
                                    <ul className="text-xs text-white/60 space-y-1">
                                      {template.features.map((feature, idx) => (
                                        <li key={idx} className="flex items-center gap-1">
                                          <Check className="w-3 h-3" />
                                          {feature}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
            {errors.template && (
              <p className="text-sm text-red-500 text-center">{errors.template}</p>
            )}
          </div>
        );

      case 1: // Configuration
        if (!currentTemplate) return null;

        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-medium text-[#cccccc] mb-4">Required Information</h3>
              <div className="space-y-4">
                {currentTemplate.requiredFields.map(field => renderField(field))}
              </div>
            </div>

            {currentTemplate.optionalFields && currentTemplate.optionalFields.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-[#cccccc] mb-4">Optional Configuration</h3>
                <div className="space-y-4">
                  {currentTemplate.optionalFields.map(field => renderField(field))}
                </div>
              </div>
            )}
          </div>
        );

      case 2: // Review
        if (!currentTemplate) return null;

        const projectName = (formData.projectName as string) || 'Unnamed Project';

        return (
          <div className="space-y-6">
            {/* Template Summary */}
            <div className="bg-[#2d2d30] rounded-lg p-4">
              <h3 className="text-sm font-medium text-[#cccccc] mb-3">Template</h3>
              <div className="flex items-start space-x-3">
                <currentTemplate.icon className="w-5 h-5 text-[#519aba] mt-0.5" />
                <div>
                  <p className="text-[#cccccc]">{currentTemplate.name}</p>
                  <p className="text-xs text-[#969696] mt-1">{currentTemplate.description}</p>
                </div>
              </div>
            </div>

            {/* Configuration Summary */}
            <div className="bg-[#2d2d30] rounded-lg p-4">
              <h3 className="text-sm font-medium text-[#cccccc] mb-3">Configuration</h3>
              <dl className="space-y-2">
                {currentTemplate.requiredFields.map(field => {
                  const value = formData[field.id];
                  if (!value) return null;

                  return (
                    <div key={field.id} className="flex justify-between text-sm">
                      <dt className="text-[#969696]">{field.label}:</dt>
                      <dd className="text-[#cccccc]">
                        {Array.isArray(value) ? value.join(', ') : String(value)}
                      </dd>
                    </div>
                  );
                })}
                {currentTemplate.optionalFields?.map(field => {
                  const value = formData[field.id];
                  if (
                    value === undefined ||
                    value === '' ||
                    (Array.isArray(value) && value.length === 0)
                  )
                    return null;

                  return (
                    <div key={field.id} className="flex justify-between text-sm">
                      <dt className="text-[#969696]">{field.label}:</dt>
                      <dd className="text-[#cccccc]">
                        {Array.isArray(value) ? value.join(', ') : String(value)}
                      </dd>
                    </div>
                  );
                })}
              </dl>
            </div>

            {/* File Structure Preview */}
            <div className="bg-[#2d2d30] rounded-lg p-4">
              <h3 className="text-sm font-medium text-[#cccccc] mb-3">File Structure Preview</h3>
              <div className="font-mono text-xs text-[#969696]">
                {renderFileStructurePreview(currentTemplate.fileStructure, formData)}
              </div>
            </div>

            {/* Location */}
            <div className="bg-[#2d2d30] rounded-lg p-4">
              <h3 className="text-sm font-medium text-[#cccccc] mb-1">Location</h3>
              <p className="text-sm text-[#969696]">
                {parentPath}/{projectName}
              </p>
            </div>

            {errors.create && (
              <div className="flex items-center gap-2 text-sm text-red-500">
                <AlertCircle className="w-4 h-4" />
                {errors.create}
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  // Render file structure preview
  const renderFileStructurePreview = (
    structure: TemplateFileStructure[],
    data: Record<string, unknown>,
    depth = 0
  ): React.ReactNode => {
    return structure.map((item, index) => {
      const name = item.name.replace(/{{(\w+)}}/g, (_, key) => String(data[key] || key));

      return (
        <div key={index} style={{ paddingLeft: depth * 16 }}>
          <span className="inline-flex items-center gap-1">
            {item.type === 'folder' ? (
              <>
                <Folder className="w-3 h-3 text-[#dcb67a]" />
                {name}/
              </>
            ) : (
              <>
                <FileText className="w-3 h-3 text-[#519aba]" />
                {name}
              </>
            )}
          </span>
          {item.children && renderFileStructurePreview(item.children, data, depth + 1)}
        </div>
      );
    });
  };

  if (!isOpen) return null;

  return (
    <>
      {/* ARIA live region for announcements */}
      <div aria-live="polite" aria-atomic="true" className="sr-only" role="status">
        {announcement}
      </div>

      {/* Modal Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <div
          ref={wizardRef}
          className="bg-[#1e1e1e] rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] flex flex-col"
          onClick={e => e.stopPropagation()}
          role="dialog"
          aria-modal="true"
          aria-labelledby="wizard-title"
          aria-describedby="wizard-description"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-[#3c3c3c]">
            <div>
              <h2
                ref={headingRef}
                id="wizard-title"
                className="text-lg font-semibold text-[#cccccc]"
                tabIndex={-1}
              >
                New Project from Template
              </h2>
              <p id="wizard-description" className="text-sm text-[#969696] mt-1">
                Create a new PLC project using pre-configured templates
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-1 hover:bg-[#3c3c3c] rounded transition-colors"
              aria-label="Close wizard"
              data-testid="wizard-close-btn"
            >
              <X className="w-5 h-5 text-[#cccccc]" />
            </button>
          </div>

          {/* Progress Steps */}
          <div className="px-6 py-4 border-b border-[#3c3c3c]">
            <div className="flex items-center justify-between">
              {wizardSteps.map((step, index) => {
                const Icon = step.icon;
                const isActive = index === currentStep;
                const isCompleted = index < currentStep;

                return (
                  <div
                    key={step.id}
                    className="flex items-center"
                    aria-current={isActive ? 'step' : undefined}
                  >
                    <div className="flex items-center">
                      <div
                        className={cn(
                          'w-8 h-8 rounded-full flex items-center justify-center transition-colors',
                          isActive
                            ? 'bg-blue-500 text-white'
                            : isCompleted
                              ? 'bg-green-500 text-white'
                              : 'bg-[#3c3c3c] text-[#969696]'
                        )}
                      >
                        {isCompleted ? <Check className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
                      </div>
                      <div className="ml-3">
                        <p
                          className={cn(
                            'text-sm font-medium',
                            isActive ? 'text-[#cccccc]' : 'text-[#969696]'
                          )}
                        >
                          {step.title}
                        </p>
                        <p className="text-xs text-[#969696]">{step.description}</p>
                      </div>
                    </div>
                    {index < wizardSteps.length - 1 && (
                      <ChevronRight className="w-4 h-4 text-[#555555] mx-4" />
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">{renderStepContent()}</div>

          {/* Footer */}
          <div className="flex items-center justify-between p-6 border-t border-[#3c3c3c]">
            <button
              onClick={goToPreviousStep}
              disabled={currentStep === 0}
              className={cn(
                'px-4 py-2 rounded font-medium transition-colors',
                'focus:outline-none focus:ring-2 focus:ring-blue-500',
                currentStep === 0
                  ? 'bg-[#3c3c3c] text-[#555555] cursor-not-allowed'
                  : 'bg-[#3c3c3c] text-[#cccccc] hover:bg-[#4c4c4c]'
              )}
              data-testid="wizard-prev-btn"
            >
              <span className="flex items-center gap-2">
                <ChevronLeft className="w-4 h-4" />
                Previous
              </span>
            </button>

            <div className="flex items-center gap-3">
              <button
                onClick={onClose}
                className="px-4 py-2 rounded font-medium bg-[#3c3c3c] text-[#cccccc] hover:bg-[#4c4c4c] transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Cancel
              </button>

              {currentStep < wizardSteps.length - 1 ? (
                <button
                  onClick={goToNextStep}
                  className="px-4 py-2 rounded font-medium bg-blue-500 text-white hover:bg-blue-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                  data-testid="wizard-next-btn"
                >
                  <span className="flex items-center gap-2">
                    Next
                    <ChevronRight className="w-4 h-4" />
                  </span>
                </button>
              ) : (
                <button
                  onClick={handleCreateProject}
                  disabled={isCreating || !selectedTemplate}
                  className={cn(
                    'px-4 py-2 rounded font-medium transition-colors',
                    'focus:outline-none focus:ring-2 focus:ring-blue-500',
                    isCreating || !selectedTemplate
                      ? 'bg-[#3c3c3c] text-[#555555] cursor-not-allowed'
                      : 'bg-green-500 text-white hover:bg-green-600'
                  )}
                  data-testid="wizard-create-btn"
                >
                  {isCreating ? (
                    <span className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Creating...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <Check className="w-4 h-4" />
                      Create Project
                    </span>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

/**
 * ProjectTemplateWizard Component
 *
 * @description Multi-step wizard for creating new PLC projects with schema-driven UI
 * @specification Implements File Explorer enhancement for project template creation
 *
 * @features
 * - Template selection with categories
 * - Schema-driven form generation
 * - Multi-step navigation
 * - Field validation with Zod
 * - File structure preview
 * - Accessibility compliant
 *
 * @accessibility
 * - Full keyboard navigation
 * - ARIA labels and descriptions
 * - Focus management
 * - Screen reader announcements
 *
 * @validation
 * - Strict TypeScript compliance
 * - Zero 'any' types
 * - Comprehensive error handling
 * - Runtime validation with Zod
 */
