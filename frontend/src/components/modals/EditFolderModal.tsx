import { useState, FormEvent, useEffect } from 'react';
import { X } from 'lucide-react';
import { apiClient } from '../../api/client';
import type { Folder, ApiError } from '../../types/api';

interface EditFolderModalProps {
  folder: Folder;
  onClose: () => void;
  onSuccess: () => void;
}

const EditFolderModal = ({ folder, onClose, onSuccess }: EditFolderModalProps) => {
  const [name, setName] = useState(folder.name);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setName(folder.name);
  }, [folder]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await apiClient.updateFolder(folder.id, { name });
      onSuccess();
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.message || 'Failed to update folder');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Edit Folder</h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded"
            tabIndex={0}
            aria-label="Close modal"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <div className="mb-4">
            <label htmlFor="folderName" className="block text-sm font-medium text-gray-700 mb-2">
              Folder Name
            </label>
            <input
              id="folderName"
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              tabIndex={0}
              aria-label="Folder name input"
            />
          </div>

          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
              tabIndex={0}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark disabled:opacity-50"
              tabIndex={0}
            >
              {isLoading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditFolderModal;


