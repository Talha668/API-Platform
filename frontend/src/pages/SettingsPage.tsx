import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { User, Mail, Building, Key, Bell, Shield, Moon, Sun, LogOut } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { useAuthContext } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { authAPI } from '../api/auth';


const profileSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  company: z.string().optional(),
  bio: z.string().optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

export const SettingsPage: React.FC = () => {
  const { user, logout } = useAuthContext();
  const { theme, toggleTheme } = useTheme();
  const [isUpdating, setIsUpdating] = React.useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      company: user?.company || '',
      bio: user?.bio || '',
    },
  });

  const onSubmit = async (data: ProfileFormData) => {
    setIsUpdating(true);
    try {
      await authAPI.updateProfile(data);
      // Refresh user data
      window.location.reload();
    } catch (error: any) {
      setError('root', {
        message: error.response?.data?.detail || 'Failed to update profile',
      });
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Manage your account settings and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Settings */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Profile</CardTitle>
            <CardDescription>
              Update your personal information
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="first_name">First name</Label>
                  <Input
                    id="first_name"
                    {...register('first_name')}
                  />
                  {errors.first_name && (
                    <p className="text-sm text-red-500">{errors.first_name.message}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="last_name">Last name</Label>
                  <Input
                    id="last_name"
                    {...register('last_name')}
                  />
                  {errors.last_name && (
                    <p className="text-sm text-red-500">{errors.last_name.message}</p>
                  )}
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="company">Company</Label>
                <Input
                  id="company"
                  placeholder="Your company name"
                  {...register('company')}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="bio">Bio</Label>
                <Input
                  id="bio"
                  placeholder="Tell us about yourself"
                  {...register('bio')}
                />
              </div>
              {errors.root && (
                <p className="text-sm text-red-500">{errors.root.message}</p>
              )}
              <Button type="submit" disabled={isUpdating}>
                {isUpdating ? 'Saving...' : 'Save Changes'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Account Info */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Account</CardTitle>
              <CardDescription>Your account information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-3">
                <Mail className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Email</p>
                  <p className="font-medium text-gray-900 dark:text-white">{user?.email}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Building className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Plan</p>
                  <p className="font-medium text-gray-900 dark:text-white capitalize">
                    {user?.subscription_tier || 'Free'}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Key className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Member since</p>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {new Date(user?.date_joined || '').toLocaleDateString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Preferences</CardTitle>
              <CardDescription>Customize your experience</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {theme === 'dark' ? (
                    <Moon className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                  ) : (
                    <Sun className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                  )}
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {theme === 'dark' ? 'Dark Mode' : 'Light Mode'}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {theme === 'dark' ? 'Currently using dark theme' : 'Currently using light theme'}
                    </p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={toggleTheme}
                >
                  Switch to {theme === 'dark' ? 'Light' : 'Dark'}
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <Button
                variant="destructive"
                className="w-full"
                onClick={logout}
              >
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};