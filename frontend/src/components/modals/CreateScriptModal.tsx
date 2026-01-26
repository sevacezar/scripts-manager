import { useState, FormEvent, ChangeEvent } from 'react';
import { X } from 'lucide-react';
import { apiClient } from '../../api/client';
import type { ApiError } from '../../types/api';

interface CreateScriptModalProps {
  folderId: number | null;
  onClose: () => void;
  onSuccess: () => void;
}

type CreationMode = 'file' | 'text';

const CreateScriptModal = ({ folderId, onClose, onSuccess }: CreateScriptModalProps) => {
  const [mode, setMode] = useState<CreationMode>('file');
  const [file, setFile] = useState<File | null>(null);
  const [filename, setFilename] = useState('');
  const [content, setContent] = useState('');
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

  const handleModeChange = (newMode: CreationMode) => {
    setMode(newMode);
    setError(null);
    setReplaceRequired(false);
    // Clear fields when switching modes
    if (newMode === 'text') {
      setFile(null);
      if (!filename && !displayName) {
        setFilename('script.py');
        setDisplayName('script');
      }
    } else {
      setFilename('');
      setContent('');
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (mode === 'file') {
      if (!file) {
        setError('Please select a file');
        return;
      }
    } else {
      if (!filename.trim()) {
        setError('Please enter a filename');
        return;
      }
      if (!filename.endsWith('.py')) {
        setError('Filename must end with .py');
        return;
      }
      if (!content.trim()) {
        setError('Please enter script content');
        return;
      }
      if (!displayName.trim()) {
        setError('Please enter a display name');
        return;
      }
    }

    setIsLoading(true);

    try {
      if (mode === 'file') {
        if (!file) {
          setError('Please select a file');
          setIsLoading(false);
          return;
        }
        await apiClient.createScript({
          file,
          display_name: displayName,
          description: description || undefined,
          folder_id: folderId,
          replace: replaceRequired,
        });
      } else {
        await apiClient.createScriptFromText({
          filename: filename.trim(),
          display_name: displayName.trim(),
          content: content.trim(),
          description: description || undefined,
          folder_id: folderId,
          replace: replaceRequired,
        });
      }
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
      <div className="bg-white rounded-lg max-w-2xl w-full mx-4 max-h-[90vh] flex flex-col">
        {/* Fixed header */}
        <div className="flex-shrink-0 p-6 pb-4 border-b border-gray-200">
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

          {/* Mode selector */}
          <div className="flex gap-2 border-b border-gray-200">
          <button
            type="button"
            onClick={() => handleModeChange('file')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              mode === 'file'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
            tabIndex={0}
          >
            Upload File
          </button>
          <button
            type="button"
            onClick={() => handleModeChange('text')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              mode === 'text'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
            tabIndex={0}
          >
            Write Code
          </button>
          </div>
        </div>

        {/* Scrollable content */}
        <div className="flex-1 overflow-y-auto p-6 pt-4">
          {error && (
            <div className={`mb-4 px-4 py-3 rounded ${
              replaceRequired
                ? 'bg-yellow-50 border border-yellow-200 text-yellow-700'
                : 'bg-red-50 border border-red-200 text-red-700'
            }`}>
              {error}
            </div>
          )}
          
          <form id="create-script-form" onSubmit={handleSubmit} className="flex flex-col">

          {mode === 'file' ? (
            <div className="mb-4">
              <label htmlFor="scriptFile" className="block text-sm font-medium text-gray-700 mb-2">
                Python File (.py)
              </label>
              <input
                id="scriptFile"
                type="file"
                accept=".py"
                required={mode === 'file'}
                onChange={handleFileChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                aria-label="Script file input"
              />
            </div>
          ) : (
            <>
              <div className="mb-4">
                <label htmlFor="filename" className="block text-sm font-medium text-gray-700 mb-2">
                  Filename <span className="text-red-500">*</span>
                </label>
                <input
                  id="filename"
                  type="text"
                  required={mode === 'text'}
                  value={filename}
                  onChange={(e) => setFilename(e.target.value)}
                  placeholder="script.py"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                  aria-label="Filename input"
                />
                <p className="mt-1 text-xs text-gray-500">Must end with .py</p>
              </div>
              <div className="mb-4">
                <label htmlFor="scriptContent" className="block text-sm font-medium text-gray-700 mb-2">
                  Script Content <span className="text-red-500">*</span>
                </label>
              <textarea
                id="scriptContent"
                required={mode === 'text'}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Tab') {
                    e.preventDefault();
                    const textarea = e.currentTarget;
                    const start = textarea.selectionStart;
                    const end = textarea.selectionEnd;
                    const tab = '    '; // 4 spaces
                    const newValue = content.substring(0, start) + tab + content.substring(end);
                    setContent(newValue);
                    // Set cursor position after the inserted tab
                    setTimeout(() => {
                      textarea.selectionStart = textarea.selectionEnd = start + tab.length;
                    }, 0);
                  }
                }}
                rows={12}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary font-mono text-sm"
                placeholder="def main(data: dict) -> dict:&#10;    # Your code here&#10;    return {}"
                aria-label="Script content input"
              />
                <p className="mt-1 text-xs text-gray-500">
                  Script must contain a function <code className="bg-gray-100 px-1 rounded">main(data: dict) -&gt; dict</code>
                </p>
              </div>
            </>
          )}

          <div className="mb-4">
            <label htmlFor="displayName" className="block text-sm font-medium text-gray-700 mb-2">
              Display Name <span className="text-red-500">*</span>
            </label>
            <input
              id="displayName"
              type="text"
              required
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
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
              aria-label="Description input"
            />
          </div>
          </form>
        </div>

        {/* Fixed footer */}
        <div className="flex-shrink-0 p-6 pt-4 border-t border-gray-200">
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
              form="create-script-form"
              disabled={isLoading}
              className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark disabled:opacity-50"
              tabIndex={0}
            >
              {isLoading ? 'Creating...' : replaceRequired ? 'Replace' : 'Create'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateScriptModal;


