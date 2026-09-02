import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Activity, 
  Database, 
  TrendingUp, 
  Clock, 
  ArrowUpRight,
  ChevronRight,
  AlertCircle,
  CheckCircle,
  XCircle,
  Loader2
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { useAuthContext } from '../context/AuthContext';
import { projectsAPI } from '../api/projects';
import { formatNumber, formatRelativeTime } from '../lib/utils';


export const DashboardPage: React.FC = () => {
  const { user } = useAuthContext();
  const navigate = useNavigate();
  
  const { data: projects, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: projectsAPI.list,
  });

  // Calculate totals
  const totalRequests = projects?.reduce((sum, p) => sum + p.total_requests, 0) || 0;
  const totalSuccess = projects?.reduce((sum, p) => sum + p.successful_requests, 0) || 0;
  const totalFailed = projects?.reduce((sum, p) => sum + p.failed_requests, 0) || 0;
  const avgResponseTime = projects?.reduce((sum, p) => sum + p.avg_response_time, 0) / (projects?.length || 1) || 0;

  const stats = [
    {
      title: 'Total Requests',
      value: formatNumber(totalRequests),
      icon: Activity,
      color: 'text-blue-600 dark:text-blue-400',
      bg: 'bg-blue-100 dark:bg-blue-900/20',
    },
    {
      title: 'Success Rate',
      value: totalRequests > 0 ? `${((totalSuccess / totalRequests) * 100).toFixed(1)}%` : '0%',
      icon: CheckCircle,
      color: 'text-green-600 dark:text-green-400',
      bg: 'bg-green-100 dark:bg-green-900/20',
    },
    {
      title: 'Failed Requests',
      value: formatNumber(totalFailed),
      icon: XCircle,
      color: 'text-red-600 dark:text-red-400',
      bg: 'bg-red-100 dark:bg-red-900/20',
    },
    {
      title: 'Avg Response Time',
      value: `${avgResponseTime.toFixed(0)}ms`,
      icon: Clock,
      color: 'text-purple-600 dark:text-purple-400',
      bg: 'bg-purple-100 dark:bg-purple-900/20',
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Failed to load dashboard data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Welcome back, {user?.first_name || 'Developer'}! 👋
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Here's what's happening with your API projects
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                      {stat.title}
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                      {stat.value}
                    </p>
                  </div>
                  <div className={`p-3 rounded-lg ${stat.bg}`}>
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Projects Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Your Projects</CardTitle>
              <CardDescription>
                Manage your API projects and monitor their performance
              </CardDescription>
            </div>
            <Button onClick={() => navigate('/projects')}>
              View All
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {projects && projects.length > 0 ? (
            <div className="space-y-4">
              {projects.slice(0, 3).map((project) => (
                <div
                  key={project.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors cursor-pointer"
                  onClick={() => navigate(`/projects/${project.id}`)}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {project.name}
                      </h3>
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                        project.tier === 'enterprise' 
                          ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300'
                          : project.tier === 'pro'
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                      }`}>
                        {project.tier}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                      {project.description || 'No description'}
                    </p>
                  </div>
                  <div className="flex items-center space-x-6 ml-4">
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {formatNumber(project.total_requests)}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Requests</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {project.error_rate.toFixed(1)}%
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Error Rate</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {project.avg_response_time.toFixed(0)}ms
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Avg Response</p>
                    </div>
                    <ArrowUpRight className="h-5 w-5 text-gray-400" />
                  </div>
                </div>
              ))}
              {projects.length > 3 && (
                <div className="text-center">
                  <Button
                    variant="ghost"
                    onClick={() => navigate('/projects')}
                    className="text-blue-600 dark:text-blue-400"
                  >
                    View all {projects.length} projects
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                No projects yet
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mt-1">
                Create your first project to start building your API
              </p>
              <Button
                onClick={() => navigate('/projects')}
                className="mt-4"
              >
                Create Project
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="cursor-pointer hover:border-blue-500 transition-colors" onClick={() => navigate('/projects')}>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <Database className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Create Project</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Start a new API project</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:border-green-500 transition-colors" onClick={() => navigate('/projects')}>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-white">View Analytics</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Monitor your API usage</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:border-purple-500 transition-colors" onClick={() => navigate('/settings')}>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                <Activity className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Account Settings</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Manage your profile</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};