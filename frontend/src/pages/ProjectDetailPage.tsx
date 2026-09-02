import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ArrowLeft, 
  Key, 
  Activity, 
  BarChart3, 
  FileText, 
  Settings,
  Link2,
  Copy,
  Check,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { projectsAPI } from '../api/projects';
import { formatNumber, formatRelativeTime } from '../lib/utils';


export const ProjectDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');

  const { data: project, isLoading, error } = useQuery({
    queryKey: ['projects', Number(id)],
    queryFn: () => projectsAPI.get(Number(id)),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Failed to load project details</p>
          <Button onClick={() => navigate('/projects')} className="mt-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Projects
          </Button>
        </div>
      </div>
    );
  }

  const navigationItems = [
    { name: 'Overview', path: '', icon: Activity },
    { name: 'API Keys', path: 'keys', icon: Key },
    { name: 'Logs', path: 'logs', icon: FileText },
    { name: 'Analytics', path: 'analytics', icon: BarChart3 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/projects')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {project.name}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {project.description || 'No description'}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
          <Button size="sm">
            <Link2 className="h-4 w-4 mr-2" />
            Copy Endpoint
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">Total Requests</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {formatNumber(project.total_requests)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">Success Rate</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">
              {project.total_requests > 0 
                ? `${((project.successful_requests / project.total_requests) * 100).toFixed(1)}%`
                : '0%'}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">Avg Response</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {project.avg_response_time.toFixed(0)}ms
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">Active Keys</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {project.api_keys_count}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Navigation Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <TabsTrigger key={item.path} value={item.name.toLowerCase()}>
                <Icon className="h-4 w-4 mr-2" />
                {item.name}
              </TabsTrigger>
            );
          })}
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Quick Stats Card */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Stats</CardTitle>
              <CardDescription>Last 7 days of activity</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Today</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatNumber(project.total_requests_today)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">This Week</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatNumber(project.total_requests_this_week)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Rate Limit</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {formatNumber(project.rate_limit)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Remaining</p>
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {formatNumber(project.rate_limit_remaining)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="cursor-pointer hover:border-blue-500 transition-colors" onClick={() => navigate(`/projects/${id}/keys`)}>
              <CardContent className="p-6">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                    <Key className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Manage API Keys</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Create and manage keys</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="cursor-pointer hover:border-green-500 transition-colors" onClick={() => navigate(`/projects/${id}/logs`)}>
              <CardContent className="p-6">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                    <FileText className="h-5 w-5 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">View Logs</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Inspect request history</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="cursor-pointer hover:border-purple-500 transition-colors" onClick={() => navigate(`/projects/${id}/analytics`)}>
              <CardContent className="p-6">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                    <BarChart3 className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">View Analytics</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Monitor performance</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Other tabs will be rendered by their respective components */}
        <TabsContent value="keys">
          <APIKeysPage projectId={Number(id)} />
        </TabsContent>
        <TabsContent value="logs">
          <LogsPage projectId={Number(id)} />
        </TabsContent>
        <TabsContent value="analytics">
          <AnalyticsPage projectId={Number(id)} />
        </TabsContent>
      </Tabs>
    </div>
  );
};