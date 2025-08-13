/**
 * Sort Dropdown Component - AI Task Orchestrator TypeScript Implementation
 *
 * @description File Explorer sorting options dropdown with accessibility support
 * @compliance Strict TypeScript - zero `any` types policy
 * @accessibility WCAG 2.1 AA compliant with keyboard navigation
 */

'use client';

import type { FileSortOption, FileSortState } from '@/lib/types/file-explorer.types';
import { cn } from '@/lib/utils/cn';
import { ArrowDownAZ, ArrowUpAZ, Calendar, ChevronDown, File, Folder } from 'lucide-react';
import React, { useCallback, useRef, useState } from 'react';

interface SortOption {
  value: FileSortOption;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

interface SortDropdownProps {
  readonly sortState: FileSortState;
  readonly onSortChange: (option: FileSortOption) => void;
  readonly className?: string;
  readonly disabled?: boolean;
}

const ORGANIZATION_OPTIONS: readonly SortOption[] = [
  {
    value: 'files-first',
    label: 'Files First',
    icon: File,
    description: 'Files before folders',
  },
  {
    value: 'folders-first',
    label: 'Folders First',
    icon: Folder,
    description: 'Folders before files',
  },
] as const;

const SORT_METHOD_OPTIONS: readonly SortOption[] = [
  {
    value: 'a-z',
    label: 'A-Z',
    icon: ArrowDownAZ,
    description: 'Alphabetical order',
  },
  {
    value: 'z-a',
    label: 'Z-A',
    icon: ArrowUpAZ,
    description: 'Reverse alphabetical',
  },
  {
    value: 'date',
    label: 'Date',
    icon: Calendar,
    description: 'By modification date',
  },
] as const;

const ALL_SORT_OPTIONS = [...ORGANIZATION_OPTIONS, ...SORT_METHOD_OPTIONS] as const;

/**
 * Sort Dropdown Component for File Explorer
 *
 * @param sortState - Current sort state
 * @param onSortChange - Callback when sort option changes
 * @param className - Additional CSS classes
 * @param disabled - Whether the dropdown is disabled
 */
export function SortDropdown({
  sortState,
  onSortChange,
  className,
  disabled = false,
}: SortDropdownProps): React.ReactElement {
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Find current options
  const currentOrganization =
    ORGANIZATION_OPTIONS.find(option => option.value === sortState.organization) ||
    ORGANIZATION_OPTIONS[0];
  const currentSortMethod =
    SORT_METHOD_OPTIONS.find(option => option.value === sortState.sortMethod) ||
    SORT_METHOD_OPTIONS[0];

  // Get the icon to display (prioritize sort method, fallback to organization)
  const DisplayIcon = currentSortMethod.icon;

  /**
   * Handle dropdown toggle
   */
  const toggleDropdown = useCallback(() => {
    if (disabled) return;
    setIsOpen(prev => !prev);
    setFocusedIndex(-1);
  }, [disabled]);

  /**
   * Handle option selection
   */
  const handleOptionSelect = useCallback(
    (option: FileSortOption) => {
      onSortChange(option);
      setIsOpen(false);
      setFocusedIndex(-1);
      buttonRef.current?.focus();
    },
    [onSortChange]
  );

  /**
   * Handle keyboard navigation
   */
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      switch (event.key) {
        case 'Escape': {
          setIsOpen(false);
          setFocusedIndex(-1);
          buttonRef.current?.focus();
          break;
        }

        case 'ArrowDown': {
          event.preventDefault();
          if (!isOpen) {
            setIsOpen(true);
            setFocusedIndex(0);
          } else {
            setFocusedIndex(prev => (prev + 1) % ALL_SORT_OPTIONS.length);
          }
          break;
        }

        case 'ArrowUp': {
          event.preventDefault();
          if (!isOpen) {
            setIsOpen(true);
            setFocusedIndex(ALL_SORT_OPTIONS.length - 1);
          } else {
            setFocusedIndex(prev => (prev - 1 + ALL_SORT_OPTIONS.length) % ALL_SORT_OPTIONS.length);
          }
          break;
        }

        case 'Enter':
        case ' ': {
          event.preventDefault();
          if (!isOpen) {
            setIsOpen(true);
            setFocusedIndex(0);
          } else if (focusedIndex >= 0) {
            handleOptionSelect(ALL_SORT_OPTIONS[focusedIndex].value);
          }
          break;
        }

        case 'Tab': {
          if (isOpen) {
            setIsOpen(false);
            setFocusedIndex(-1);
          }
          break;
        }

        default: {
          // Handle letter navigation
          const letter = event.key.toLowerCase();
          if (letter.length === 1 && /[a-z]/.test(letter)) {
            event.preventDefault();
            const matchingIndex = ALL_SORT_OPTIONS.findIndex(option =>
              option.label.toLowerCase().startsWith(letter)
            );
            if (matchingIndex >= 0) {
              if (!isOpen) {
                setIsOpen(true);
              }
              setFocusedIndex(matchingIndex);
            }
          }
          break;
        }
      }
    },
    [isOpen, focusedIndex, handleOptionSelect]
  );

  /**
   * Handle click outside to close dropdown
   */
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setFocusedIndex(-1);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  return (
    <div className={cn('relative', className)}>
      {/* Dropdown Trigger Button */}
      <button
        ref={buttonRef}
        onClick={toggleDropdown}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        className={cn(
          'p-1 rounded text-[#cccccc] transition-colors flex items-center space-x-1',
          'hover:bg-[#2a2d2e] focus:outline-none focus:ring-2 focus:ring-blue-500',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
        title={`Sort: ${currentOrganization.label} • ${currentSortMethod.label}`}
        aria-label={`Sort: ${currentOrganization.label}, ${currentSortMethod.label}. Click to change sorting options.`}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        type="button"
      >
        <DisplayIcon className="w-4 h-4" />
        <ChevronDown className={cn('w-3 h-3 transition-transform', isOpen && 'rotate-180')} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          ref={dropdownRef}
          className="absolute right-0 top-full mt-1 bg-[#2d2d30] border border-[#5a5a5a] rounded-lg shadow-lg z-50 min-w-48"
          role="listbox"
          aria-label="Sort options"
        >
          <div className="py-1">
            {/* Organization Section */}
            <div className="px-3 py-1 text-xs font-medium text-[#969696] uppercase tracking-wider border-b border-[#5a5a5a]">
              Organization
            </div>
            {ORGANIZATION_OPTIONS.map((option, index) => {
              const isSelected = option.value === sortState.organization;
              const isFocused = index === focusedIndex;

              return (
                <button
                  key={option.value}
                  onClick={() => handleOptionSelect(option.value)}
                  className={cn(
                    'w-full px-3 py-2 text-left flex items-center space-x-3 transition-colors',
                    'hover:bg-[#3c3c3c] focus:outline-none',
                    isSelected && 'bg-[#094771] text-white',
                    isFocused && 'bg-[#3c3c3c]'
                  )}
                  role="option"
                  aria-selected={isSelected}
                  tabIndex={-1}
                  type="button"
                >
                  <option.icon
                    className={cn(
                      'w-4 h-4 flex-shrink-0',
                      isSelected ? 'text-white' : 'text-[#cccccc]'
                    )}
                  />
                  <div className="flex-1 min-w-0">
                    <div
                      className={cn(
                        'text-sm font-medium',
                        isSelected ? 'text-white' : 'text-[#cccccc]'
                      )}
                    >
                      {option.label}
                    </div>
                    <div className={cn('text-xs', isSelected ? 'text-blue-200' : 'text-[#969696]')}>
                      {option.description}
                    </div>
                  </div>
                  {isSelected && <div className="w-2 h-2 bg-white rounded-full flex-shrink-0" />}
                </button>
              );
            })}

            {/* Sort Method Section */}
            <div className="px-3 py-1 text-xs font-medium text-[#969696] uppercase tracking-wider border-b border-[#5a5a5a] mt-2">
              Sort Method
            </div>
            {SORT_METHOD_OPTIONS.map((option, index) => {
              const isSelected = option.value === sortState.sortMethod;
              const isFocused = index + ORGANIZATION_OPTIONS.length === focusedIndex;

              return (
                <button
                  key={option.value}
                  onClick={() => handleOptionSelect(option.value)}
                  className={cn(
                    'w-full px-3 py-2 text-left flex items-center space-x-3 transition-colors',
                    'hover:bg-[#3c3c3c] focus:outline-none',
                    isSelected && 'bg-[#094771] text-white',
                    isFocused && 'bg-[#3c3c3c]'
                  )}
                  role="option"
                  aria-selected={isSelected}
                  tabIndex={-1}
                  type="button"
                >
                  <option.icon
                    className={cn(
                      'w-4 h-4 flex-shrink-0',
                      isSelected ? 'text-white' : 'text-[#cccccc]'
                    )}
                  />
                  <div className="flex-1 min-w-0">
                    <div
                      className={cn(
                        'text-sm font-medium',
                        isSelected ? 'text-white' : 'text-[#cccccc]'
                      )}
                    >
                      {option.label}
                    </div>
                    <div className={cn('text-xs', isSelected ? 'text-blue-200' : 'text-[#969696]')}>
                      {option.description}
                    </div>
                  </div>
                  {isSelected && <div className="w-2 h-2 bg-white rounded-full flex-shrink-0" />}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
