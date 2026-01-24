import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  TreeResponse,
  Script,
  Folder,
  ScriptContentResponse,
  CreateFolderRequest,
  UpdateFolderRequest,
  CreateScriptRequest,
  UpdateScriptRequest,
  ApiError,
} from '../types/api';

const API_BASE_URL = '/api/v1';

class ApiClient {
  private getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: HeadersInit = {
      ...options.headers,
    };

    // Only set Content-Type for JSON requests (not FormData)
    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });

      // Handle 401 Unauthorized - token expired or invalid
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        throw new Error('Session expired. Please login again.');
      }

      if (!response.ok) {
        const error: ApiError = await response.json().catch(() => ({
          error_code: 'UNKNOWN_ERROR',
          message: 'An unknown error occurred',
        }));
        throw error;
      }

      if (response.status === 204) {
        return null as T;
      }

      return response.json();
    } catch (error) {
      // Handle network errors
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        throw {
          error_code: 'NETWORK_ERROR',
          message: 'Network error. Please check your connection.',
        } as ApiError;
      }
      throw error;
    }
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(data: LoginRequest): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getTree(): Promise<TreeResponse> {
    return this.request<TreeResponse>('/scripts-manager/tree');
  }

  async getFolder(folderId: number): Promise<Folder> {
    return this.request<Folder>(`/scripts-manager/folders/${folderId}`);
  }

  async createFolder(data: CreateFolderRequest): Promise<Folder> {
    return this.request<Folder>('/scripts-manager/folders', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateFolder(folderId: number, data: UpdateFolderRequest): Promise<Folder> {
    return this.request<Folder>(`/scripts-manager/folders/${folderId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteFolder(folderId: number): Promise<void> {
    return this.request<void>(`/scripts-manager/folders/${folderId}`, {
      method: 'DELETE',
    });
  }

  async getScript(scriptId: number): Promise<Script> {
    return this.request<Script>(`/scripts-manager/scripts/${scriptId}`);
  }

  async getScriptContent(scriptId: number): Promise<ScriptContentResponse> {
    return this.request<ScriptContentResponse>(`/scripts-manager/scripts/${scriptId}/content`);
  }

  async createScript(data: CreateScriptRequest): Promise<Script> {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('display_name', data.display_name);
    if (data.description) {
      formData.append('description', data.description);
    }
    if (data.folder_id !== undefined && data.folder_id !== null) {
      formData.append('folder_id', data.folder_id.toString());
    }
    if (data.replace !== undefined) {
      formData.append('replace', data.replace.toString());
    }

    const token = this.getToken();
    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/scripts-manager/scripts`, {
        method: 'POST',
        headers,
        body: formData,
      });

      // Handle 401 Unauthorized - token expired or invalid
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        throw new Error('Session expired. Please login again.');
      }

      if (!response.ok) {
        const error: ApiError = await response.json().catch(() => ({
          error_code: 'UNKNOWN_ERROR',
          message: 'An unknown error occurred',
        }));
        throw error;
      }

      return response.json();
    } catch (error) {
      // Handle network errors
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        throw {
          error_code: 'NETWORK_ERROR',
          message: 'Network error. Please check your connection.',
        } as ApiError;
      }
      throw error;
    }
  }

  async updateScript(scriptId: number, data: UpdateScriptRequest): Promise<Script> {
    return this.request<Script>(`/scripts-manager/scripts/${scriptId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteScript(scriptId: number): Promise<void> {
    return this.request<void>(`/scripts-manager/scripts/${scriptId}`, {
      method: 'DELETE',
    });
  }
}

export const apiClient = new ApiClient();

