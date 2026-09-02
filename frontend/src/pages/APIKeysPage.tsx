import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Copy, Check, Trash2, RefreshCw, AlertCircle, Key, Loader2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useAPIKeys } from '../hooks/useAPIKeys';
import { formatRelativeTime } from '../lib/utils';


const keySchema = z.object({
  name: z.string().min(1, 'Key name is required'),
  scope: z.enum(['read', 'write', 'admin']).default('read'),
});

type KeyFormData = z.infer<typeof keySchema>;

interface APIKeysPageProps {
  projectId?: number;
}

export const APIKeysPage: React.FC<APIKeysPageProps> = ({ projectId: propProjectId }) => {
  const { id } = useParams<{ id: string }>();
  const projectId = propProjectId || Number(id);
  const { keys, isLoading, createKey, deleteKey, regenerateKey } = useAPIKeys(projectId);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [showSecret, setShowSecret] = useState<string | null>(null);
  const [selectedKey, setSelectedKey] = useState<number | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<KeyFormData>({
    resolver: zodResolver(keySchema),
    defaultValues: {
      scope: 'read',
    },
  });

  const onSubmit = async (data: KeyFormData) => {
    try {
      const result = await createKey.mutateAsync(data);
      if (result.key) {
        setShowSecret(result.key);
      }
      setIsCreateModalOpen(false);
      reset();
    } catch (error) {
      console.error('Failed to create API key:', error);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(text);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleRegenerate = async (keyId: number) => {
    if (window.confirm('This will generate a new secret. The old secret will be invalidated. Continue?')) {
      const result = await regenerateKey.mutateAsync(keyId);
      if (result.key) {
        setShowSecret(result.key);
      }
    }
  };

  const handleDelete = async (keyId: number) => {
    if (window.confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      await deleteKey.mutateAsync(keyId);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">API Keys</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Manage API keys for your project
          </p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create API Key
        </Button>
      </div>

      {/* API Keys List */}
      {keys && keys.length > 0 ? (
        <div className="space-y-4">
          {keys.map((key) => (
            <Card key={key.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                        {key.name}
                      </h3>
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                        key.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                      }`}>
                        {key.is_active ? 'Active' : 'Inactive'}
                      </span>
                      {key.is_expired && (
                        <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300">
                          Expired
                        </span>
                      )}
                    </div>
                    <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                      <span>Scope: <span className="font-medium">{key.scope_display}</span></span>
                      <span>Prefix: <code className="px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs">{key.key_prefix}</code></span>
                      {key.last_used_at && (
                        <span>Last used: {formatRelativeTime(key.last_used_at)}</span>
                      )}
                      <span>Created: {formatRelativeTime(key.created_at)}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRegenerate(key.id)}
                      disabled={regenerateKey.isPending}
                    >
                      <RefreshCw className={`h-4 w-4 ${regenerateKey.isPending ? 'animate-spin' : ''}`} />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(key.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                {/* Show secret if recently created/regenerated */}
                {showSecret === key.key && (
                  <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                          ⚠️ This secret will only be shown once!
                        </p>
                        <code className="mt-1 block text-sm font-mono bg-white dark:bg-gray-900 p-2 rounded border border-yellow-200 dark:border-yellow-800 break-all">
                          {showSecret}
                        </code>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleCopy(showSecret)}
                        className="ml-4"
                      >
                        {copiedKey === showSecret ? (
                          <Check className="h-4 w-4 text-green-600" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="flex flex-col items-center">
            <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-full mb-4">
              <Key className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">No API keys</h3>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              Create your first API key to start making requests
            </p>
            <Button onClick={() => setIsCreateModalOpen(true)} className="mt-4">
              <Plus className="h-4 w-4 mr-2" />
              Create API Key
            </Button>
          </div>
        </div>
      )}

      {/* Create API Key Modal */}
      <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create API Key</DialogTitle>
            <DialogDescription>
              Generate a new API key for your project.
              The secret will only be shown once.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="name">Key Name</Label>
                <Input
                  id="name"
                  placeholder="Production Key"
                  {...register('name')}
                />
                {errors.name && (
                  <p className="text-sm text-red-500">{errors.name.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="scope">Scope</Label>
                <Select {...register('scope')}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a scope" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="read">Read Only</SelectItem>
                    <SelectItem value="write">Read and Write</SelectItem>
                    <SelectItem value="admin">Full Access</SelectItem>
                  </SelectContent>
                </Select>
                {errors.scope && (
                  <p className="text-sm text-red-500">{errors.scope.message}</p>
                )}
              </div>
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsCreateModalOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={createKey.isPending}>
                {createKey.isPending ? 'Creating...' : 'Create Key'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};