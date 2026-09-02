import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FolderOpen, 
  Key, 
  FileText, 
  BarChart3, 
  Settings,
  Zap
} from 'lucide-react';
import { cn } from '../../lib/utils';


const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Projects', href: '/projects', icon: FolderOpen },
  { name: 'API Keys', href: '/projects', icon: Key },
  { name: 'Logs', href: '/projects', icon: FileText },
  { name: 'Analytics', href: '/projects', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="fixed inset-y-0 left-0 z-50 hidden w-64 lg:block bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center px-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <Zap className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            <span className="text-xl font-bold text-gray-900 dark:text-white">
              API<span className="text-blue-600 dark:text-blue-400">Hub</span>
            </span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  cn(
                    "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                    isActive
                      ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                      : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  )
                }
              >
                <Icon className="h-5 w-5 mr-3 flex-shrink-0" />
                {item.name}
              </NavLink>
            );
          })}
        </nav>
      </div>
    </aside>
  );
};