export interface User {
  id: number;
  login: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  login: string;
  password: string;
}

export interface RegisterRequest {
  login: string;
  password: string;
}

export interface Folder {
  id: number;
  name: string;
  path: string;
  parent_id: number | null;
  created_by: User;
  created_at: string;
  updated_at: string;
  can_edit: boolean;
  can_delete: boolean;
}

export interface Script {
  id: number;
  filename: string;
  logical_path: string;
  display_name: string;
  description: string | null;
  folder_id: number | null;
  created_by: User;
  created_at: string;
  updated_at: string;
  can_edit: boolean;
  can_delete: boolean;
}

export interface FolderTreeItem {
  folder: Folder;
  scripts: Script[];
  subfolders: FolderTreeItem[];
}

export interface TreeResponse {
  root_scripts: Script[];
  root_folders: FolderTreeItem[];
}

export interface ScriptContentResponse {
  content: string;
}

export interface CreateFolderRequest {
  name: string;
  parent_id: number | null;
}

export interface UpdateFolderRequest {
  name?: string;
}

export interface CreateScriptRequest {
  file: File;
  display_name: string;
  description?: string;
  folder_id?: number | null;
  replace?: boolean;
}

export interface UpdateScriptRequest {
  display_name?: string;
  description?: string;
  filename?: string;
}

export interface ApiError {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
}

