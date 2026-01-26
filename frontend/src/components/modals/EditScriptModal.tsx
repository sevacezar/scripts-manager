import { useState, FormEvent, useEffect } from 'react';
import { X } from 'lucide-react';
import { apiClient } from '../../api/client';
import type { Script, ApiError } from '../../types/api';

interface EditScriptModalProps {
  script: Script;
  onClose: () => void;
  onSuccess: () => void;
}

const EditScriptModal = ({ script, onClose, onSuccess }: EditScriptModalProps) => {
  const [displayName, setDisplayName] = useState(script.display_name);
  const [description, setDescription] = useState(script.description || '');
  const [filename, setFilename] = useState(script.filename);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setDisplayName(script.display_name);
    setDescription(script.description || '');
    setFilename(script.filename);
  }, [script]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await apiClient.updateScript(script.id, {
        display_name: displayName,
        description: description || undefined,
        filename: filename !== script.filename ? filename : undefined,
      });
      onSuccess();
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.message || 'Failed to update script');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Edit Script</h3>
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
            <label htmlFor="filename" className="block text-sm font-medium text-gray-700 mb-2">
              Filename
            </label>
            <input
              id="filename"
              type="text"
              required
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              tabIndex={0}
              aria-label="Filename input"
            />
            <p className="text-xs text-gray-500 mt-1">Must have .py extension</p>
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
              {isLoading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditScriptModal;


