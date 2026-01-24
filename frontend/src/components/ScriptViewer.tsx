import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { apiClient } from '../api/client';
import type { Script } from '../types/api';

interface ScriptViewerProps {
  script: Script;
  onClose: () => void;
}

const ScriptViewer = ({ script, onClose }: ScriptViewerProps) => {
  const [content, setContent] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadContent = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await apiClient.getScriptContent(script.id);
        setContent(response.content);
      } catch (err) {
        setError('Failed to load script content');
      } finally {
        setIsLoading(false);
      }
    };

    loadContent();
  }, [script.id]);

  return (
    <div className="w-1/2 border-l border-gray-200 bg-white flex flex-col">
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">{script.display_name}</h3>
          <p className="text-sm text-gray-500">{script.logical_path}</p>
          {script.description && (
            <p className="text-sm text-gray-600 mt-1">{script.description}</p>
          )}
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded"
          tabIndex={0}
          aria-label="Close viewer"
        >
          <X className="w-5 h-5 text-gray-600" />
        </button>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {isLoading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-600">Loading...</div>
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center h-full">
            <div className="text-red-600">{error}</div>
          </div>
        )}

        {content && (
          <pre className="bg-gray-50 p-4 rounded border border-gray-200 overflow-x-auto text-sm font-mono">
            <code>{content}</code>
          </pre>
        )}
      </div>
    </div>
  );
};

export default ScriptViewer;

