import { useState, FormEvent, ChangeEvent } from 'react';
import { X } from 'lucide-react';
import { apiClient } from '../../api/client';
import type { ApiError } from '../../types/api';

interface CreateScriptModalProps {
  folderId: number | null;
  onClose: () => void;
  onSuccess: () => void;
}

const CreateScriptModal = ({ folderId, onClose, onSuccess }: CreateScriptModalProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [displayName, setDisplayName] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [replaceRequired, setReplaceRequired] = useState(false);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      if (!displayName) {
        setDisplayName(selectedFile.name.replace('.py', ''));
      }
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!file) {
      setError('Please select a file');
      return;
    }

    setIsLoading(true);

    try {
      await apiClient.createScript({
        file,
        display_name: displayName,
        description: description || undefined,
        folder_id: folderId,
        replace: replaceRequired,
      });
      onSuccess();
    } catch (err) {
      const apiError = err as ApiError;
      if (apiError.error_code === 'SCRIPT_EXISTS_REPLACE_REQUIRED') {
        setReplaceRequired(true);
        setError('Script already exists. Click Create again to replace it.');
      } else {
        setError(apiError.message || 'Failed to create script');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Create Script</h3>
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
            <div className={`mb-4 px-4 py-3 rounded ${
              replaceRequired
                ? 'bg-yellow-50 border border-yellow-200 text-yellow-700'
                : 'bg-red-50 border border-red-200 text-red-700'
            }`}>
              {error}
            </div>
          )}

          <div className="mb-4">
            <label htmlFor="scriptFile" className="block text-sm font-medium text-gray-700 mb-2">
              Python File (.py)
            </label>
            <input
              id="scriptFile"
              type="file"
              accept=".py"
              required
              onChange={handleFileChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              tabIndex={0}
              aria-label="Script file input"
            />
          </div>

          <div className="mb-4">
            <label htmlFor="displayName" className="block text-sm font-medium text-gray-700 mb-2">
              Display Name
            </label>
            <input
              id="displayName"
              type="text"
              required
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              tabIndex={0}
              aria-label="Display name input"
            />
          </div>

          <div className="mb-4">
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Description (optional)
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              tabIndex={0}
              aria-label="Description input"
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
              {isLoading ? 'Creating...' : replaceRequired ? 'Replace' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateScriptModal;

