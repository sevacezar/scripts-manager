import { useState, useEffect } from 'react';
import { X, Sun, Moon, Copy, Check, Loader2 } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { apiClient } from '../../api/client';

interface CodeExampleModalProps {
  onClose: () => void;
}

type Theme = 'light' | 'dark';

const CodeExampleModal = ({ onClose }: CodeExampleModalProps) => {
  const [theme, setTheme] = useState<Theme>(() => {
    const savedTheme = localStorage.getItem('code-viewer-theme');
    return (savedTheme === 'dark' || savedTheme === 'light') ? savedTheme : 'light';
  });
  const [copied, setCopied] = useState(false);
  const [code, setCode] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadCode = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const codeContent = await apiClient.getCodeExample();
        console.log('Loaded code content:', codeContent?.substring(0, 100));
        if (!codeContent || codeContent === 'null' || codeContent.trim() === '') {
          throw new Error('Получен пустой ответ от сервера');
        }
        setCode(codeContent);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Не удалось загрузить пример кода';
        setError(errorMessage);
        console.error('Failed to load code example:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadCode();
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('code-viewer-theme', newTheme);
  };

  const handleCopy = async () => {
    if (!code) return;
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full mx-4 max-h-[90vh] flex flex-col shadow-xl">
        {/* Header */}
        <div className="flex-shrink-0 p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
              Пример вызова скрипта из тНавигатора
            </h3>
            <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
              Python
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
              tabIndex={0}
              aria-label="Копировать код"
              title="Копировать код"
            >
              {copied ? (
                <Check className="w-5 h-5 text-green-600" />
              ) : (
                <Copy className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              )}
            </button>
            <button
              onClick={toggleTheme}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
              tabIndex={0}
              aria-label="Переключить тему"
              title="Переключить тему"
            >
              {theme === 'light' ? (
                <Moon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              ) : (
                <Sun className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              )}
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
              tabIndex={0}
              aria-label="Закрыть"
            >
              <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
        </div>

        {/* Code Content */}
        <div className="flex-1 overflow-auto">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-red-600">{error}</p>
            </div>
          ) : (
            <SyntaxHighlighter
              language="python"
              style={theme === 'dark' ? vscDarkPlus : oneLight}
              customStyle={{
                margin: 0,
                padding: '1.5rem',
                fontSize: '0.875rem',
                lineHeight: '1.6',
              }}
              showLineNumbers
            >
              {code}
            </SyntaxHighlighter>
          )}
        </div>

        {/* Footer */}
        <div className="flex-shrink-0 p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
          <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
            Этот пример показывает, как вызвать скрипт на сервере из тНавигатора через HTTP API
          </p>
        </div>
      </div>
    </div>
  );
};

export default CodeExampleModal;

