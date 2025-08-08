/**
 * Select Component
 * Dropdown select component with search and async loading support
 */

import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check, Search, Loader } from 'lucide-react';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

interface SelectProps {
  label?: string;
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  options: SelectOption[];
  loading?: boolean;
  searchable?: boolean;
  disabled?: boolean;
  error?: string;
  helperText?: string;
  required?: boolean;
  className?: string;
  onSearch?: (searchTerm: string) => void;
}

const Select: React.FC<SelectProps> = ({
  label,
  placeholder = 'Select an option...',
  value,
  onChange,
  options,
  loading = false,
  searchable = false,
  disabled = false,
  error,
  helperText,
  required = false,
  className = '',
  onSearch,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredOptions, setFilteredOptions] = useState(options);
  const selectRef = useRef<HTMLDivElement>(null);

  // Filter options based on search term
  useEffect(() => {
    if (searchable && searchTerm) {
      const filtered = options.filter(option =>
        option.label.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredOptions(filtered);
      onSearch?.(searchTerm);
    } else {
      setFilteredOptions(options);
    }
  }, [searchTerm, options, searchable, onSearch]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectedOption = options.find(option => option.value === value);

  const handleOptionClick = (optionValue: string) => {
    onChange?.(optionValue);
    setIsOpen(false);
    setSearchTerm('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (disabled) return;

    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        setIsOpen(!isOpen);
        break;
      case 'Escape':
        setIsOpen(false);
        setSearchTerm('');
        break;
      case 'ArrowDown':
        e.preventDefault();
        setIsOpen(true);
        break;
    }
  };

  return (
    <div className={`relative ${className}`} ref={selectRef}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          className={`
            relative w-full bg-white border rounded-lg px-3 py-2 text-left cursor-default
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            transition-colors duration-200
            ${error 
              ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
              : 'border-gray-300'
            }
            ${disabled 
              ? 'bg-gray-50 text-gray-500 cursor-not-allowed' 
              : 'hover:border-gray-400'
            }
          `}
        >
          <span className={`block truncate ${!selectedOption ? 'text-gray-500' : 'text-gray-900'}`}>
            {selectedOption ? selectedOption.label : placeholder}
          </span>
          
          <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
            {loading ? (
              <Loader className="w-4 h-4 text-gray-400 animate-spin" />
            ) : (
              <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${
                isOpen ? 'transform rotate-180' : ''
              }`} />
            )}
          </span>
        </button>

        {/* Dropdown */}
        {isOpen && (
          <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-lg border border-gray-200 overflow-hidden">
            {searchable && (
              <div className="p-2 border-b border-gray-200">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search options..."
                    className="w-full pl-9 pr-3 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                    autoFocus
                  />
                </div>
              </div>
            )}
            
            <div className="py-1 max-h-48 overflow-auto">
              {loading ? (
                <div className="px-3 py-2 text-center text-gray-500">
                  <Loader className="w-4 h-4 animate-spin mx-auto mb-1" />
                  <span className="text-sm">Loading options...</span>
                </div>
              ) : filteredOptions.length === 0 ? (
                <div className="px-3 py-2 text-sm text-gray-500 text-center">
                  {searchTerm ? 'No options found' : 'No options available'}
                </div>
              ) : (
                filteredOptions.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => !option.disabled && handleOptionClick(option.value)}
                    disabled={option.disabled}
                    className={`
                      relative w-full text-left px-3 py-2 text-sm cursor-default select-none
                      transition-colors duration-150
                      ${option.disabled
                        ? 'text-gray-400 cursor-not-allowed'
                        : 'hover:bg-blue-50 hover:text-blue-900 cursor-pointer'
                      }
                      ${value === option.value 
                        ? 'bg-blue-100 text-blue-900' 
                        : 'text-gray-900'
                      }
                    `}
                  >
                    <span className="block truncate">{option.label}</span>
                    
                    {value === option.value && (
                      <span className="absolute inset-y-0 right-0 flex items-center pr-3">
                        <Check className="w-4 h-4 text-blue-600" />
                      </span>
                    )}
                  </button>
                ))
              )}
            </div>
          </div>
        )}
      </div>

      {/* Helper text or error */}
      {(helperText || error) && (
        <p className={`mt-1 text-xs ${error ? 'text-red-600' : 'text-gray-500'}`}>
          {error || helperText}
        </p>
      )}
    </div>
  );
};

export default Select;