import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { TreeResponse, FolderTreeItem, Script, ApiError } from '../types/api';
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
  expandedFolders: Set<number>;
  onToggleFolder: (folderId: number, isExpanded: boolean) => void;
}

const FolderItem = ({ folderItem, level, onRefresh, onViewScript, expandedFolders, onToggleFolder }: FolderItemProps) => {
  const [isExpanded, setIsExpanded] = useState(expandedFolders.has(folderItem.folder.id));
  
  // Sync with parent state when folder ID changes
  useEffect(() => {
    setIsExpanded(expandedFolders.has(folderItem.folder.id));
  }, [folderItem.folder.id, expandedFolders]);

  const handleToggle = () => {
    const newExpanded = !isExpanded;
    setIsExpanded(newExpanded);
    onToggleFolder(folderItem.folder.id, newExpanded);
  };
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
        alert(apiError.message || 'Ошибка удаления папки');
      }
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  return (
    <div>
      <div
        className="flex items-center gap-2 py-1 px-2 hover:bg-gray-100 rounded cursor-pointer group min-w-0"
        style={{ paddingLeft: `${level * 1.5}rem` }}
        onDoubleClick={handleToggle}
      >
        <button
          onClick={handleToggle}
          className="p-1 hover:bg-gray-200 rounded flex-shrink-0"
          tabIndex={0}
          aria-label={isExpanded ? 'Collapse folder' : 'Expand folder'}
        >
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-gray-600" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-600" />
          )}
        </button>
        <FolderIcon className="w-4 h-4 text-primary flex-shrink-0" />
        <span className="flex-1 text-sm font-medium text-gray-700 min-w-0 truncate">{folderItem.folder.name}</span>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {/* Any user can create folders and scripts in any directory */}
          <button
            onClick={() => setShowCreateFolder(true)}
            className="p-1 hover:bg-gray-200 rounded text-xs text-gray-600"
            tabIndex={0}
            aria-label="Создать подпапку"
            title="Создать подпапку"
          >
            + Папка
          </button>
          <button
            onClick={() => setShowCreateScript(true)}
            className="p-1 hover:bg-gray-200 rounded text-xs text-gray-600"
            tabIndex={0}
            aria-label="Создать скрипт"
            title="Создать скрипт"
          >
            + Скрипт
          </button>
          {folderItem.folder.can_edit && (
            <button
              onClick={() => setShowEditFolder(true)}
              className="p-1 hover:bg-gray-200 rounded"
              tabIndex={0}
              aria-label="Редактировать папку"
              title="Редактировать папку"
            >
              <Edit2 className="w-4 h-4 text-gray-600" />
            </button>
          )}
          {folderItem.folder.can_delete && (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="p-1 hover:bg-red-100 rounded"
              tabIndex={0}
              aria-label="Удалить папку"
              title="Удалить папку"
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
              expandedFolders={expandedFolders}
              onToggleFolder={onToggleFolder}
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
            <h3 className="text-lg font-semibold mb-4">Удалить папку</h3>
            <p className="text-gray-600 mb-6">
              Вы уверены, что хотите удалить папку "{folderItem.folder.name}"? Это удалит все скрипты и подпапки внутри.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
                tabIndex={0}
              >
                Отмена
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                tabIndex={0}
              >
                {isDeleting ? 'Удаление...' : 'Удалить'}
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
        alert(apiError.message || 'Ошибка удаления скрипта');
      }
    } finally {
      setIsDeleting(false);
      setShowDelete(false);
    }
  };

  return (
    <>
      <div
        className="flex items-center gap-2 py-1 px-2 hover:bg-gray-100 rounded cursor-pointer group min-w-0"
        style={{ paddingLeft: `${level * 1.5}rem` }}
      >
        <FileCode className="w-4 h-4 text-primary flex-shrink-0" />
        <div
          className="flex-1 flex items-center gap-2 cursor-pointer min-w-0"
          onClick={() => onView(script)}
          title={script.display_name !== script.filename ? script.display_name : undefined}
        >
          <span className="text-sm text-gray-700 hover:text-primary font-medium flex-shrink-0">
            {script.filename}
          </span>
          {script.display_name !== script.filename && (
            <span 
              className="text-xs text-gray-500 italic whitespace-nowrap flex-shrink-0" 
              title={script.display_name}
            >
              ({script.display_name})
            </span>
          )}
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onView(script)}
            className="p-1 hover:bg-gray-200 rounded"
            tabIndex={0}
            aria-label="Просмотреть скрипт"
            title="Просмотреть скрипт"
          >
            <Eye className="w-4 h-4 text-gray-600" />
          </button>
          {script.can_edit && (
            <button
              onClick={() => setShowEdit(true)}
              className="p-1 hover:bg-gray-200 rounded"
              tabIndex={0}
              aria-label="Редактировать скрипт"
              title="Редактировать скрипт"
            >
              <Edit2 className="w-4 h-4 text-gray-600" />
            </button>
          )}
          {script.can_delete && (
            <button
              onClick={() => setShowDelete(true)}
              className="p-1 hover:bg-red-100 rounded"
              tabIndex={0}
              aria-label="Удалить скрипт"
              title="Удалить скрипт"
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
            <h3 className="text-lg font-semibold mb-4">Удалить скрипт</h3>
            <p className="text-gray-600 mb-6">
              Вы уверены, что хотите удалить скрипт "{script.display_name}"?
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDelete(false)}
                className="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
                tabIndex={0}
              >
                Отмена
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                tabIndex={0}
              >
                {isDeleting ? 'Удаление...' : 'Удалить'}
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
  const [expandedFolders, setExpandedFolders] = useState<Set<number>>(new Set());
  const [viewerWidth, setViewerWidth] = useState(() => {
    const savedWidth = localStorage.getItem('script-viewer-width');
    return savedWidth ? parseFloat(savedWidth) : 50; // Percentage, default 50%
  });
  const [isResizing, setIsResizing] = useState(false);

  const handleToggleFolder = (folderId: number, isExpanded: boolean) => {
    setExpandedFolders((prev) => {
      const newSet = new Set(prev);
      if (isExpanded) {
        newSet.add(folderId);
      } else {
        newSet.delete(folderId);
      }
      return newSet;
    });
  };

  const handleMouseDown = () => {
    setIsResizing(true);
  };

  const loadTree = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient.getTree();
      setTree(data);
      // Keep expanded folders state after refresh
    } catch (err) {
      setError('Ошибка загрузки дерева скриптов');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTree();
  }, []);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      
      const container = document.querySelector('.scripts-tree-container');
      if (!container) return;
      
      const containerRect = container.getBoundingClientRect();
      // Calculate viewer width based on mouse position
      // Mouse position relative to right edge of container
      const mouseX = e.clientX - containerRect.left;
      const containerWidth = containerRect.width;
      const newViewerWidth = ((containerWidth - mouseX) / containerWidth) * 100;
      
      // Limit width between 20% and 80%
      const clampedWidth = Math.max(20, Math.min(80, newViewerWidth));
      setViewerWidth(clampedWidth);
      localStorage.setItem('script-viewer-width', clampedWidth.toString());
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Загрузка...</div>
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
    <div className="flex h-full scripts-tree-container">
      <div 
        className="overflow-auto p-4 flex-shrink-0" 
        style={{ 
          width: selectedScript ? `${100 - viewerWidth}%` : '100%',
          minWidth: selectedScript ? '200px' : 'auto'
        }}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-800">Скрипты и папки</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setShowCreateFolder(true)}
              className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark text-sm"
              tabIndex={0}
            >
              + Новая папка
            </button>
            <button
              onClick={() => setShowCreateScript(true)}
              className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark text-sm"
              tabIndex={0}
            >
              + Новый скрипт
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
              expandedFolders={expandedFolders}
              onToggleFolder={handleToggleFolder}
            />
          ))}
          {tree.root_scripts.length === 0 && tree.root_folders.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              Пока нет скриптов или папок. Создайте первую папку или скрипт!
            </div>
          )}
        </div>
      </div>

      {selectedScript && (
        <>
          <div
            onMouseDown={handleMouseDown}
            className="w-1 bg-gray-300 hover:bg-primary cursor-col-resize transition-colors flex-shrink-0"
            style={{ cursor: isResizing ? 'col-resize' : 'col-resize' }}
            role="separator"
            aria-label="Resize viewer"
            aria-orientation="vertical"
          />
          <div style={{ width: `${viewerWidth}%` }} className="flex-shrink-0">
            <ScriptViewer
              script={selectedScript}
              onClose={() => setSelectedScript(null)}
              onScriptUpdated={(updatedScript) => {
                setSelectedScript(updatedScript);
                loadTree();
              }}
            />
          </div>
        </>
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

