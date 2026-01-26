import { useState, useEffect, useRef } from 'react';
import { X, Sun, Moon, Edit2, Save, XCircle } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
import { keymap } from '@codemirror/view';
import { EditorView } from '@codemirror/view';
import { Transaction } from '@codemirror/state';
import { apiClient } from '../api/client';
import type { Script, ApiError } from '../types/api';

interface ScriptViewerProps {
  script: Script;
  onClose: () => void;
  onScriptUpdated?: (updatedScript: Script) => void;
}

type Theme = 'light' | 'dark';

const ScriptViewer = ({ script, onClose, onScriptUpdated }: ScriptViewerProps) => {
  const [content, setContent] = useState<string | null>(null);
  const [originalContent, setOriginalContent] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [theme, setTheme] = useState<Theme>(() => {
    const savedTheme = localStorage.getItem('code-viewer-theme');
    return (savedTheme === 'dark' || savedTheme === 'light') ? savedTheme : 'light';
  });
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);
  const [showExpandButton, setShowExpandButton] = useState(false);
  const [isDescriptionLong, setIsDescriptionLong] = useState(false);
  const descriptionRef = useRef<HTMLParagraphElement>(null);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('code-viewer-theme', newTheme);
  };

  useEffect(() => {
    const loadContent = async () => {
      setIsLoading(true);
      setError(null);
      setIsEditing(false);
      setSaveError(null);
      try {
        const response = await apiClient.getScriptContent(script.id);
        setContent(response.content);
        setOriginalContent(response.content);
      } catch (err) {
        setError('Ошибка загрузки содержимого скрипта');
      } finally {
        setIsLoading(false);
      }
    };

    loadContent();
  }, [script.id]);


  useEffect(() => {
    // Check if description is longer than 3 lines
    // Use setTimeout to ensure element is rendered
    const timer = setTimeout(() => {
      if (descriptionRef.current && script.description) {
        const element = descriptionRef.current;
        
        // Create a temporary clone to measure full height without line-clamp
        const clone = element.cloneNode(true) as HTMLElement;
        clone.className = clone.className.replace('line-clamp-3', '');
        clone.style.position = 'absolute';
        clone.style.visibility = 'hidden';
        clone.style.width = `${element.offsetWidth}px`;
        clone.style.whiteSpace = 'pre-line';
        document.body.appendChild(clone);
        
        const fullHeight = clone.scrollHeight;
        const clampedHeight = element.clientHeight;
        
        document.body.removeChild(clone);
        
        // Check if description is longer than 3 lines
        const isLong = fullHeight > clampedHeight;
        setIsDescriptionLong(isLong);
        
        // Show button if description is long (either to expand or collapse)
        setShowExpandButton(isLong);
      } else {
        setIsDescriptionLong(false);
        setShowExpandButton(false);
      }
    }, 0);

    return () => clearTimeout(timer);
  }, [script.description]);

  const handleToggleDescription = () => {
    setIsDescriptionExpanded(!isDescriptionExpanded);
  };

  const handleStartEdit = () => {
    setIsEditing(true);
    setSaveError(null);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setContent(originalContent);
    setSaveError(null);
  };

  const handleContentChange = (value: string) => {
    setContent(value);
    setSaveError(null);
  };

  const hasChanges = content !== originalContent;

  const handleSave = async () => {
    if (content === null || !hasChanges) return;

    setIsSaving(true);
    setSaveError(null);

    try {
      const updatedScript = await apiClient.updateScript(script.id, {
        content: content,
      });
      
      setOriginalContent(content);
      setIsEditing(false);
      
      if (onScriptUpdated) {
        onScriptUpdated(updatedScript);
      }
    } catch (err) {
      const apiError = err as ApiError;
      // Extract detailed error message from backend
      let errorMessage = 'Ошибка сохранения содержимого скрипта';
      
      if (apiError.message) {
        errorMessage = apiError.message;
      } else if (apiError.error_code) {
        // If we have error code but no message, create a user-friendly message
        if (apiError.error_code === 'SCRIPT_MISSING_MAIN') {
          errorMessage = "Скрипт должен содержать функцию 'main(data: dict) -> dict'";
        } else if (apiError.error_code === 'INVALID_SCRIPT_CONTENT') {
          errorMessage = 'Ошибка валидации скрипта. Проверьте содержимое скрипта.';
        } else {
          errorMessage = `Ошибка: ${apiError.error_code}`;
        }
      }
      
      setSaveError(errorMessage);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="h-full border-l border-gray-200 bg-white flex flex-col">
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold text-gray-800">{script.filename}</h3>
            {script.display_name !== script.filename && (
              <span className="text-sm text-gray-500 italic">({script.display_name})</span>
            )}
          </div>
          <p className="text-sm text-gray-500 mt-1">{script.logical_path}</p>
          {script.description && (
            <div className="mt-1">
              <p
                ref={descriptionRef}
                className={`text-sm text-gray-600 whitespace-pre-line ${
                  !isDescriptionExpanded ? 'line-clamp-3' : ''
                }`}
              >
                {script.description}
              </p>
              {showExpandButton && (
                <button
                  onClick={handleToggleDescription}
                  className="text-xs text-primary hover:text-primary-dark mt-1 font-medium"
                  tabIndex={0}
                  aria-label={isDescriptionExpanded ? 'Hide full description' : 'Show full description'}
                >
                  {isDescriptionExpanded ? 'Скрыть' : 'Показать все'}
                </button>
              )}
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          {!isEditing && script.can_edit && (
            <button
              onClick={handleStartEdit}
              className="px-3 py-1.5 text-sm bg-primary text-white rounded hover:bg-primary-dark flex items-center gap-1.5"
              tabIndex={0}
              aria-label="Редактировать скрипт"
            >
              <Edit2 className="w-4 h-4" />
              Редактировать
            </button>
          )}
          {!isEditing && (
            <button
              onClick={toggleTheme}
              className="p-2 hover:bg-gray-100 rounded transition-colors"
              tabIndex={0}
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
              title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
            >
              {theme === 'light' ? (
                <Moon className="w-5 h-5 text-gray-600" />
              ) : (
                <Sun className="w-5 h-5 text-gray-600" />
              )}
            </button>
          )}
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded"
            tabIndex={0}
            aria-label="Close viewer"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4 flex flex-col">
        {isLoading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-600">Загрузка...</div>
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center h-full">
            <div className="text-red-600">{error}</div>
          </div>
        )}

        {content !== null && !isLoading && !error && (
          <>
            {isEditing ? (
              <div className="flex-1 flex flex-col min-h-0">
                <div className="flex-1 min-h-0 border border-gray-300 rounded overflow-hidden">
                  <CodeMirror
                    value={content || ''}
                    height="100%"
                    extensions={[
                      python(),
                      keymap.of([
                        {
                          key: 'Tab',
                          preventDefault: true,
                          run: (view: EditorView) => {
                            const { state } = view;
                            const transaction = state.changeByRange((range) => {
                              return {
                                changes: { from: range.from, insert: '    ' },
                                range: { from: range.from + 4, to: range.from + 4 },
                              };
                            });
                            view.dispatch(transaction);
                            return true;
                          },
                        },
                      ]),
                    ]}
                    theme={theme === 'dark' ? oneDark : undefined}
                    onChange={(value) => {
                      setContent(value);
                      setSaveError(null);
                    }}
                    basicSetup={{
                      lineNumbers: true,
                      foldGutter: true,
                      dropCursor: false,
                      allowMultipleSelections: false,
                      indentOnInput: false,
                      tabSize: 4,
                      indentUnit: 4,
                    }}
                    style={{
                      fontSize: '0.875rem',
                      height: '100%',
                    }}
                  />
                </div>
                <div className="flex-shrink-0 mt-4">
                  {saveError && (
                    <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-600">
                      {saveError}
                    </div>
                  )}
                  <div className="flex gap-2 justify-end">
                    <button
                      onClick={handleCancelEdit}
                      disabled={isSaving}
                      className="px-4 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
                      tabIndex={0}
                      aria-label="Отменить редактирование"
                    >
                      <XCircle className="w-4 h-4" />
                      Отмена
                    </button>
                    <button
                      onClick={handleSave}
                      disabled={!hasChanges || isSaving}
                      className="px-4 py-2 text-sm bg-primary text-white rounded hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
                      tabIndex={0}
                      aria-label="Сохранить изменения"
                    >
                      <Save className="w-4 h-4" />
                      {isSaving ? 'Сохранение...' : 'Сохранить'}
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div 
                className="rounded border border-gray-200 overflow-auto cursor-text"
                onDoubleClick={() => {
                  if (script.can_edit && !isEditing) {
                    handleStartEdit();
                  }
                }}
                title={script.can_edit ? 'Двойной клик для редактирования' : undefined}
              >
                <SyntaxHighlighter
                  language="python"
                  style={theme === 'light' ? oneLight : vscDarkPlus}
                  customStyle={{
                    margin: 0,
                    padding: '1rem',
                    fontSize: '0.875rem',
                    lineHeight: '1.5',
                    backgroundColor: theme === 'light' ? '#fafafa' : '#1e1e1e',
                  }}
                  showLineNumbers
                  lineNumberStyle={{
                    minWidth: '3em',
                    paddingRight: '1em',
                    color: theme === 'light' ? '#999' : '#858585',
                    userSelect: 'none',
                  }}
                >
                  {content}
                </SyntaxHighlighter>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ScriptViewer;

