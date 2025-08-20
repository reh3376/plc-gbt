/**
 * Validation Tab - AI Task Orchestrator TypeScript Implementation
 *
 * @description View real-time validation results and error details
 * @compliance Strict TypeScript with OpenAPI Schema MCP validation
 * @features Real-time validation, severity levels, field-specific messages
 */

'use client';

import { AlertCircle, CheckCircle, Info, RefreshCw, Shield, XCircle } from 'lucide-react';
import React, { useMemo } from 'react';

import {
  type NodePropertySchema,
  type ValidationResult,
  type ValidationSeverity,
} from '@/api/zod-schemas';
import { cn } from '@/lib/utils/cn';

interface ValidationTabProps {
  readonly schema: NodePropertySchema;
  readonly config: Record<string, unknown>;
  readonly validationResults: ReadonlyArray<ValidationResult>;
  readonly isValidating: boolean;
  readonly onRevalidate: () => void;
}

interface ValidationSummary {
  readonly total: number;
  readonly errors: number;
  readonly warnings: number;
  readonly info: number;
  readonly isValid: boolean;
}

export function ValidationTab({
  schema,
  config,
  validationResults,
  isValidating,
  onRevalidate,
}: Readonly<ValidationTabProps>): React.JSX.Element {
  // Remove unused parameter warnings
  const _unusedSchema = schema;
  const _unusedConfig = config;
  // Calculate validation summary
  const validationSummary = useMemo((): ValidationSummary => {
    const errors = validationResults.filter(r => r.severity === 'error').length;
    const warnings = validationResults.filter(r => r.severity === 'warning').length;
    const info = validationResults.filter(r => r.severity === 'info').length;

    return {
      total: validationResults.length,
      errors,
      warnings,
      info,
      isValid: errors === 0,
    };
  }, [validationResults]);

  // Group validation results by field
  const resultsByField = useMemo(() => {
    const grouped = new Map<string, ValidationResult[]>();

    validationResults.forEach(result => {
      const field = result.field || 'general';
      const existing = grouped.get(field) || [];
      grouped.set(field, [...existing, result]);
    });

    return grouped;
  }, [validationResults]);

  // Get severity icon and color
  const getSeverityDisplay = (severity: ValidationSeverity) => {
    switch (severity) {
      case 'error':
        return {
          icon: XCircle,
          color: 'text-red-400',
          bgColor: 'bg-red-900/20',
          borderColor: 'border-red-500/30',
        };
      case 'warning':
        return {
          icon: AlertCircle,
          color: 'text-yellow-400',
          bgColor: 'bg-yellow-900/20',
          borderColor: 'border-yellow-500/30',
        };
      case 'info':
        return {
          icon: Info,
          color: 'text-blue-400',
          bgColor: 'bg-blue-900/20',
          borderColor: 'border-blue-500/30',
        };
    }
  };

  return (
    <div className="p-4 space-y-6">
      {/* Validation Summary */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            {validationSummary.isValid ? (
              <CheckCircle className="w-6 h-6 text-green-400" />
            ) : (
              <XCircle className="w-6 h-6 text-red-400" />
            )}
            <h3 className="text-lg font-medium text-white">
              {(() => {
                if (
                  validationResults.some(r => r.message === 'Validation: Awaiting Configuration')
                ) {
                  return 'Validation: Awaiting Configuration';
                }
                return validationSummary.isValid ? 'Validation Passed' : 'Validation Failed';
              })()}
            </h3>
          </div>

          {/* Summary Badges */}
          <div className="flex items-center gap-2">
            {validationSummary.errors > 0 && (
              <span className="flex items-center gap-1 text-xs bg-red-900/20 text-red-400 px-2 py-1 rounded border border-red-500/30">
                <XCircle className="w-3 h-3" />
                {validationSummary.errors} errors
              </span>
            )}
            {validationSummary.warnings > 0 && (
              <span className="flex items-center gap-1 text-xs bg-yellow-900/20 text-yellow-400 px-2 py-1 rounded border border-yellow-500/30">
                <AlertCircle className="w-3 h-3" />
                {validationSummary.warnings} warnings
              </span>
            )}
            {validationSummary.info > 0 && (
              <span className="flex items-center gap-1 text-xs bg-blue-900/20 text-blue-400 px-2 py-1 rounded border border-blue-500/30">
                <Info className="w-3 h-3" />
                {validationSummary.info} info
              </span>
            )}
            {validationSummary.total === 0 && (
              <span className="flex items-center gap-1 text-xs bg-green-900/20 text-green-400 px-2 py-1 rounded border border-green-500/30">
                <CheckCircle className="w-3 h-3" />
                No issues
              </span>
            )}
          </div>
        </div>

        <button
          onClick={onRevalidate}
          disabled={isValidating}
          className={cn(
            'flex items-center gap-2 px-3 py-2 text-sm rounded transition-all duration-200',
            'focus:outline-none focus:ring-2 focus:ring-blue-500/50',
            isValidating
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          )}
        >
          <RefreshCw className={cn('w-4 h-4', isValidating && 'animate-spin')} />
          {isValidating ? 'Validating...' : 'Revalidate'}
        </button>
      </div>

      {/* Validation Results */}
      {validationResults.length > 0 ? (
        <div className="space-y-4">
          {Array.from(resultsByField.entries()).map(([field, fieldResults]) => (
            <div key={field} className="space-y-2">
              <h4 className="text-sm font-medium text-gray-300 flex items-center gap-2">
                <Shield className="w-4 h-4" />
                {field === 'general' ? 'General Validation' : `Field: ${field}`}
              </h4>

              {fieldResults.map((result, index) => {
                const display = getSeverityDisplay(result.severity);
                const IconComponent = display.icon;

                return (
                  <div
                    key={`${field}-${index}`}
                    className={cn(
                      'flex items-start gap-3 p-3 rounded-lg transition-all duration-200',
                      display.bgColor,
                      display.borderColor,
                      'border animate-in slide-in-from-left-2'
                    )}
                  >
                    <IconComponent className={cn('w-4 h-4 mt-0.5 flex-shrink-0', display.color)} />

                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-white">{result.message}</p>

                      {result.code && (
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-gray-400">Error Code:</span>
                          <code className="text-xs bg-[#1e1e1e] text-gray-300 px-2 py-1 rounded">
                            {result.code}
                          </code>
                        </div>
                      )}

                      <div className="text-xs text-gray-500 mt-1">
                        Severity: {result.severity.toUpperCase()}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center text-gray-400 py-8">
          <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-400" />
          <p className="text-lg font-medium mb-2">Configuration Valid</p>
          <p className="text-sm max-w-md mx-auto">
            All configuration parameters have been validated successfully. No errors or warnings
            detected.
          </p>
        </div>
      )}

      {/* Validation Rules Info */}
      <div className="border-t border-[#404040] pt-4">
        <h4 className="text-sm font-medium text-gray-300 mb-3">Validation Rules</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <h5 className="text-xs font-medium text-gray-400">Field Validation</h5>
            <ul className="text-xs text-gray-500 space-y-1">
              <li>• Required fields must have values</li>
              <li>• Numeric fields must be within specified ranges</li>
              <li>• String fields must match patterns if specified</li>
              <li>• Select fields must use valid options</li>
            </ul>
          </div>

          <div className="space-y-2">
            <h5 className="text-xs font-medium text-gray-400">Cross-Field Validation</h5>
            <ul className="text-xs text-gray-500 space-y-1">
              <li>• Dependent fields are checked for consistency</li>
              <li>• Connection compatibility is verified</li>
              <li>• Protocol-specific rules are applied</li>
              <li>• Performance constraints are validated</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
