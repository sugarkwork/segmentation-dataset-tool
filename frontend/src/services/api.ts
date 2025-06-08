import axios from 'axios';
import { Project, ProjectSummary, Image, ClassDefinition, User } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
  
  register: async (email: string, full_name: string, password: string) => {
    const response = await api.post('/auth/register', {
      email,
      full_name,
      password,
    });
    return response.data;
  },
  
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/users/me');
    return response.data;
  },
};

// Projects API
export const projectsApi = {
  getProjects: async (): Promise<ProjectSummary[]> => {
    const response = await api.get('/projects/');
    return response.data;
  },
  
  getProject: async (id: number): Promise<Project> => {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },
  
  createProject: async (name: string, description?: string): Promise<Project> => {
    const response = await api.post('/projects/', { name, description });
    return response.data;
  },
  
  updateProject: async (id: number, name: string, description?: string): Promise<Project> => {
    const response = await api.put(`/projects/${id}`, { name, description });
    return response.data;
  },
  
  deleteProject: async (id: number): Promise<void> => {
    await api.delete(`/projects/${id}`);
  },
};

// Images API
export const imagesApi = {
  getProjectImages: async (projectId: number): Promise<Image[]> => {
    const response = await api.get(`/images/project/${projectId}`);
    return response.data;
  },
  
  uploadImage: async (projectId: number, file: File, datasetType: string = 'train', notes?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('dataset_type', datasetType);
    if (notes) {
      formData.append('notes', notes);
    }
    
    const response = await api.post(`/images/project/${projectId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  
  deleteImage: async (id: number): Promise<void> => {
    await api.delete(`/images/${id}`);
  },
};

// Classes API
export const classesApi = {
  getProjectClasses: async (projectId: number): Promise<ClassDefinition[]> => {
    const response = await api.get(`/classes/project/${projectId}`);
    return response.data;
  },
  
  createClass: async (projectId: number, name: string, color: string, description?: string): Promise<ClassDefinition> => {
    const response = await api.post('/classes/', {
      project_id: projectId,
      name,
      color,
      description,
    });
    return response.data;
  },
  
  updateClass: async (id: number, name: string, color: string, description?: string): Promise<ClassDefinition> => {
    const response = await api.put(`/classes/${id}`, { name, color, description });
    return response.data;
  },
  
  deleteClass: async (id: number): Promise<void> => {
    await api.delete(`/classes/${id}`);
  },
};

export default api;