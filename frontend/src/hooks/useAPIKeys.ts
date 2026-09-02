import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiKeysAPI } from '../api/apiKeys';
import { APIKey, APIKeyCreate } from '../types/apiKey';


export const useAPIKeys = (projectId: number) => {
  const queryClient = useQueryClient();

  const { data: keys, isLoading } = useQuery({
    queryKey: ['apiKeys', projectId],
    queryFn: () => apiKeysAPI.list(projectId),
    enabled: !!projectId,
  });

  const createKey = useMutation({
    mutationFn: (data: APIKeyCreate) => apiKeysAPI.create(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys', projectId] });
    },
  });

  const updateKey = useMutation({
    mutationFn: ({ keyId, data }: { keyId: number; data: Partial<APIKey> }) =>
      apiKeysAPI.update(projectId, keyId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys', projectId] });
    },
  });

  const deleteKey = useMutation({
    mutationFn: (keyId: number) => apiKeysAPI.delete(projectId, keyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys', projectId] });
    },
  });

  const regenerateKey = useMutation({
    mutationFn: (keyId: number) => apiKeysAPI.regenerate(projectId, keyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys', projectId] });
    },
  });

  return {
    keys,
    isLoading,
    createKey,
    updateKey,
    deleteKey,
    regenerateKey,
  };
};