/**
 * Sidebar Navigation Component
 * Modern sidebar with collapsible sections based on the OLIVER design pattern
 */

'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/hooks';
import {
  User,
  Settings,
  ChevronDown,
  ChevronRight,
  Package,
  Building2
} from 'lucide-react';

interface SidebarItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  href?: string;
  children?: SidebarItem[];
  allowedRoles?: string[];
}

const sidebarItems: SidebarItem[] = [
  {
    id: 'inventory',
    label: 'Inventory',
    icon: Package,
    children: [
      { id: 'products', label: 'Products', icon: Package, href: '/products', allowedRoles: ['Owner', 'Admin', 'Manager', 'Stocker'] },
    ]
  }
];

const Sidebar: React.FC = () => {
  const [expandedSections, setExpandedSections] = useState<string[]>(['inventory']);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const pathname = usePathname();
  const { authState, isUserType } = useAuth();

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev =>
      prev.includes(sectionId)
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    );
  };

  const hasAccess = (item: SidebarItem): boolean => {
    if (!item.allowedRoles) return true;
    if (!authState.user) return false;
    return isUserType(item.allowedRoles as any);
  };

  const renderSidebarItem = (item: SidebarItem, depth = 0) => {
    const isExpanded = expandedSections.includes(item.id);
    const isActive = pathname === item.href;
    const hasChildren = item.children && item.children.length > 0;
    const Icon = item.icon;

    if (!hasAccess(item)) return null;

    if (hasChildren) {
      return (
        <div key={item.id} className="mb-1">
          <button
            onClick={() => toggleSection(item.id)}
            className={`w-full flex items-center justify-between px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 ${
              depth === 0 
                ? 'text-gray-700 hover:bg-gray-100' 
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center">
              {depth === 0 ? (
                <Icon className="w-4 h-4 mr-3 text-gray-500" />
              ) : (
                <div className="w-4 h-4 mr-3" />
              )}
              <span className={depth === 0 ? 'font-semibold' : ''}>{item.label}</span>
            </div>
            {hasChildren && (
              isExpanded ? (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-400" />
              )
            )}
          </button>
          
          {isExpanded && (
            <div className="ml-4 mt-1 space-y-1">
              {item.children?.map(child => renderSidebarItem(child, depth + 1))}
            </div>
          )}
        </div>
      );
    }

    return (
      <Link
        key={item.id}
        href={item.href || '#'}
        className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 ${
          isActive
            ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
        }`}
      >
        {depth === 0 ? (
          <Icon className={`w-4 h-4 mr-3 ${isActive ? 'text-blue-700' : 'text-gray-500'}`} />
        ) : (
          <div className="w-4 h-4 mr-3" />
        )}
        <span>{item.label}</span>
      </Link>
    );
  };

  return (
    <div className={`bg-white border-r border-gray-200 h-screen flex flex-col transition-all duration-300 ${
      isCollapsed ? 'w-16' : 'w-64'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Building2 className="w-4 h-4 text-white" />
          </div>
          {!isCollapsed && (
            <span className="ml-3 text-lg font-semibold text-gray-900">DryWall ERP</span>
          )}
        </div>
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <Settings className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      {/* Menu Label */}
      {!isCollapsed && (
        <div className="px-4 py-2 border-b border-gray-200">
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            MENU
          </span>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 overflow-y-auto">
        <div className="space-y-2">
          {sidebarItems.map(item => renderSidebarItem(item))}
        </div>
      </nav>

      {/* User Profile */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center">
          <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-gray-600" />
          </div>
          {!isCollapsed && (
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">
                {authState.user?.first_name} {authState.user?.last_name}
              </p>
              <p className="text-xs text-gray-500">{authState.user?.email}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;