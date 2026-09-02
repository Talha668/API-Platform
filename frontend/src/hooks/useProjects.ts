import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsAPI } from '../api/projects';
import { Project, ProjectCreate, ProjectUpdate } from '../types/project';


export const useProjects = () => {
  const queryClient = useQueryClient();

  const { data: projects, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: projectsAPI.list,
  });

  const createProject = useMutation({
    mutationFn: projectsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });

  const updateProject = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProjectUpdate }) =>
      projectsAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });

  const deleteProject = useMutation({
    mutationFn: projectsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });

  return {
    projects,
    isLoading,
    error,
    createProject,
    updateProject,
    deleteProject,
  };
};

export const useProject = (id: number) => {
  return useQuery({
    queryKey: ['projects', id],
    queryFn: () => projectsAPI.get(id),
    enabled: !!id,
  });
};

export const useProjectUsage = (id: number, days: number = 7) => {
  return useQuery({
    queryKey: ['projects', id, 'usage', days],
    queryFn: () => projectsAPI.getUsage(id, days),
    enabled: !!id,
  });
};