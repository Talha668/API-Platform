import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, User, LogOut, Settings } from 'lucide-react';
import { Button } from '../ui/button';
import { useAuthContext } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';


export const Header: React.FC = () => {
  const { user, logout } = useAuthContext();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);

  return (
    <header className="sticky top-0 z-40 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="flex h-16 items-center justify-between px-4 md:px-8">
        <div className="flex items-center lg:hidden">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsMenuOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </Button>
        </div>

        <div className="flex-1" />

        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate('/settings')}
          >
            <Settings className="h-5 w-5" />
          </Button>

          <div className="relative">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              <User className="h-5 w-5" />
            </Button>

            {isMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-700 py-1">
                <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {user?.first_name} {user?.last_name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {user?.email}
                  </p>
                </div>
                <button
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                  onClick={() => {
                    setIsMenuOpen(false);
                    navigate('/settings');
                  }}
                >
                  <User className="h-4 w-4 mr-2" />
                  Profile
                </button>
                <button
                  className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                  onClick={() => {
                    setIsMenuOpen(false);
                    logout();
                  }}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};