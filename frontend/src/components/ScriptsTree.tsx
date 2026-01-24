import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { TreeResponse, FolderTreeItem, Script, Folder, ApiError } from '../types/api';
import { ChevronRight, ChevronDown, Folder as FolderIcon, FileCode, Trash2, Edit2, Eye } from 'lucide-react';
import CreateFolderModal from './modals/CreateFolderModal';
import CreateScriptModal from './modals/CreateScriptModal';
import EditFolderModal from './modals/EditFolderModal';
import EditScriptModal from './modals/EditScriptModal';
import ScriptViewer from './ScriptViewer';

interface FolderItemProps {
  folderItem: FolderTreeItem;
  level: number;
  onRefresh: () => void;
  onViewScript: (script: Script) => void;
}

const FolderItem = ({ folderItem, level, onRefresh, onViewScript }: FolderItemProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showCreateFolder, setShowCreateFolder] = useState(false);
  const [showCreateScript, setShowCreateScript] = useState(false);
  const [showEditFolder, setShowEditFolder] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await apiClient.deleteFolder(folderItem.folder.id);
      onRefresh();
    } catch (error) {
      const apiError = error as ApiError;
      // Error will be handled by API client for 401, so we only show other errors
      if (apiError.error_code !== 'NETWORK_ERROR') {
        alert(apiError.message || 'Failed to delete folder');
      }
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  return (
    <div>
      <div
        className="flex items-center gap-2 py-1 px-2 hover:bg-gray-100 rounded cursor-pointer group"
        style={{ paddingLeft: `${level * 1.5}rem` }}
      >
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1 hover:bg-gray-200 rounded"
          tabIndex={0}
          aria-label={isExpanded ? 'Collapse folder' : 'Expand folder'}
        >
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-gray-600" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-600" />
          )}
        </button>
        <FolderIcon className="w-4 h-4 text-primary" />
        <span className="flex-1 text-sm font-medium text-gray-700">{folderItem.folder.name}</span>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {folderItem.folder.can_edit && (
            <>
              <button
                onClick={() => setShowCreateFolder(true)}
                className="p-1 hover:bg-gray-200 rounded text-xs text-gray-600"
                tabIndex={0}
                aria-label="Create subfolder"
                title="Create subfolder"
              >
                + Folder
              </button>
              <button
                onClick={() => setShowCreateScript(true)}
                className="p-1 hover:bg-gray-200 rounded text-xs text-gray-600"
                tabIndex={0}
                aria-label="Create script"
                title="Create script"
              >
                + Script
              </button>
              <button
                onClick={() => setShowEditFolder(true)}
                className="p-1 hover:bg-gray-200 rounded"
                tabIndex={0}
                aria-label="Edit folder"
                title="Edit folder"
              >
                <Edit2 className="w-4 h-4 text-gray-600" />
              </button>
            </>
          )}
          {folderItem.folder.can_delete && (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="p-1 hover:bg-red-100 rounded"
              tabIndex={0}
              aria-label="Delete folder"
              title="Delete folder"
            >
              <Trash2 className="w-4 h-4 text-red-600" />
            </button>
          )}
        </div>
      </div>

      {isExpanded && (
        <div>
          {folderItem.scripts.map((script) => (
            <ScriptItem
              key={script.id}
              script={script}
              level={level + 1}
              onRefresh={onRefresh}
              onView={onViewScript}
            />
          ))}
          {folderItem.subfolders.map((subfolder) => (
            <FolderItem
              key={subfolder.folder.id}
              folderItem={subfolder}
              level={level + 1}
              onRefresh={onRefresh}
              onViewScript={onViewScript}
            />
          ))}
        </div>
      )}

      {showCreateFolder && (
        <CreateFolderModal
          parentId={folderItem.folder.id}
          onClose={() => setShowCreateFolder(false)}
          onSuccess={() => {
            setShowCreateFolder(false);
            onRefresh();
          }}
        />
      )}

      {showCreateScript && (
        <CreateScriptModal
          folderId={folderItem.folder.id}
          onClose={() => setShowCreateScript(false)}
          onSuccess={() => {
            setShowCreateScript(false);
            onRefresh();
          }}
        />
      )}

      {showEditFolder && (
        <EditFolderModal
          folder={folderItem.folder}
          onClose={() => setShowEditFolder(false)}
          onSuccess={() => {
            setShowEditFolder(false);
            onRefresh();
          }}
        />
      )}

      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Delete Folder</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete folder "{folderItem.folder.name}"? This will delete all scripts and subfolders inside.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
                tabIndex={0}
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                tabIndex={0}
              >
                {isDeleting ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

interface ScriptItemProps {
  script: Script;
  level: number;
  onRefresh: () => void;
  onView: (script: Script) => void;
}

const ScriptItem = ({ script, level, onRefresh, onView }: ScriptItemProps) => {
  const [showEdit, setShowEdit] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await apiClient.deleteScript(script.id);
      onRefresh();
    } catch (error) {
      const apiError = error as ApiError;
      // Error will be handled by API client for 401, so we only show other errors
      if (apiError.error_code !== 'NETWORK_ERROR') {
        alert(apiError.message || 'Failed to delete script');
      }
    } finally {
      setIsDeleting(false);
      setShowDelete(false);
    }
  };

  return (
    <>
      <div
        className="flex items-center gap-2 py-1 px-2 hover:bg-gray-100 rounded cursor-pointer group"
        style={{ paddingLeft: `${level * 1.5}rem` }}
      >
        <FileCode className="w-4 h-4 text-primary" />
        <span
          className="flex-1 text-sm text-gray-700 hover:text-primary cursor-pointer"
          onClick={() => onView(script)}
        >
          {script.display_name}
        </span>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onView(script)}
            className="p-1 hover:bg-gray-200 rounded"
            tabIndex={0}
            aria-label="View script"
            title="View script"
          >
            <Eye className="w-4 h-4 text-gray-600" />
          </button>
          {script.can_edit && (
            <button
              onClick={() => setShowEdit(true)}
              className="p-1 hover:bg-gray-200 rounded"
              tabIndex={0}
              aria-label="Edit script"
              title="Edit script"
            >
              <Edit2 className="w-4 h-4 text-gray-600" />
            </button>
          )}
          {script.can_delete && (
            <button
              onClick={() => setShowDelete(true)}
              className="p-1 hover:bg-red-100 rounded"
              tabIndex={0}
              aria-label="Delete script"
              title="Delete script"
            >
              <Trash2 className="w-4 h-4 text-red-600" />
            </button>
          )}
        </div>
      </div>

      {showEdit && (
        <EditScriptModal
          script={script}
          onClose={() => setShowEdit(false)}
          onSuccess={() => {
            setShowEdit(false);
            onRefresh();
          }}
        />
      )}

      {showDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Delete Script</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete script "{script.display_name}"?
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDelete(false)}
                className="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
                tabIndex={0}
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                tabIndex={0}
              >
                {isDeleting ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

const ScriptsTree = () => {
  const [tree, setTree] = useState<TreeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedScript, setSelectedScript] = useState<Script | null>(null);
  const [showCreateFolder, setShowCreateFolder] = useState(false);
  const [showCreateScript, setShowCreateScript] = useState(false);

  const loadTree = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient.getTree();
      setTree(data);
    } catch (err) {
      setError('Failed to load scripts tree');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTree();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="text-red-600 mb-4">{error}</div>
        <button
          onClick={loadTree}
          className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark"
          tabIndex={0}
        >
          Retry
        </button>
      </div>
    );
  }

  if (!tree) {
    return null;
  }

  return (
    <div className="flex h-full">
      <div className="flex-1 overflow-auto p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-800">Scripts & Folders</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setShowCreateFolder(true)}
              className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark text-sm"
              tabIndex={0}
            >
              + New Folder
            </button>
            <button
              onClick={() => setShowCreateScript(true)}
              className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark text-sm"
              tabIndex={0}
            >
              + New Script
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200">
          {tree.root_scripts.map((script) => (
            <ScriptItem
              key={script.id}
              script={script}
              level={0}
              onRefresh={loadTree}
              onView={setSelectedScript}
            />
          ))}
          {tree.root_folders.map((folderItem) => (
            <FolderItem
              key={folderItem.folder.id}
              folderItem={folderItem}
              level={0}
              onRefresh={loadTree}
              onViewScript={setSelectedScript}
            />
          ))}
          {tree.root_scripts.length === 0 && tree.root_folders.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              No scripts or folders yet. Create your first folder or script!
            </div>
          )}
        </div>
      </div>

      {selectedScript && (
        <ScriptViewer
          script={selectedScript}
          onClose={() => setSelectedScript(null)}
        />
      )}

      {showCreateFolder && (
        <CreateFolderModal
          parentId={null}
          onClose={() => setShowCreateFolder(false)}
          onSuccess={() => {
            setShowCreateFolder(false);
            loadTree();
          }}
        />
      )}

      {showCreateScript && (
        <CreateScriptModal
          folderId={null}
          onClose={() => setShowCreateScript(false)}
          onSuccess={() => {
            setShowCreateScript(false);
            loadTree();
          }}
        />
      )}
    </div>
  );
};

export default ScriptsTree;

