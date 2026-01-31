import { ReactNode, useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { LogOut, HelpCircle, Code } from 'lucide-react';
import Onboarding from './Onboarding';
import CodeExampleModal from './modals/CodeExampleModal';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const { logout, needsOnboarding, isLoading } = useAuth();
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showCodeExample, setShowCodeExample] = useState(false);

  useEffect(() => {
    // Show onboarding if user needs it and we're not loading
    if (!isLoading && needsOnboarding) {
      setShowOnboarding(true);
    }
  }, [needsOnboarding, isLoading]);

  const handleOnboardingComplete = () => {
    setShowOnboarding(false);
  };

  const handleOnboardingSkip = () => {
    setShowOnboarding(false);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Onboarding
        run={showOnboarding}
        onComplete={handleOnboardingComplete}
        onSkip={handleOnboardingSkip}
      />
      <header className="bg-primary text-white shadow-md">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <h1 className="text-xl font-bold">Менеджер скриптов</h1>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowCodeExample(true)}
              className="flex items-center gap-2 px-3 py-2 bg-primary-dark hover:bg-primary-light rounded transition-colors text-sm"
              tabIndex={0}
              aria-label="Показать пример кода"
              title="Показать пример вызова скрипта из тНавигатора"
              data-onboarding="code-example-button"
            >
              <Code className="w-4 h-4" />
              <span className="hidden sm:inline">Пример кода</span>
            </button>
            <button
              onClick={() => setShowOnboarding(true)}
              className="flex items-center gap-2 px-3 py-2 bg-primary-dark hover:bg-primary-light rounded transition-colors text-sm"
              tabIndex={0}
              aria-label="Показать онбординг"
              title="Показать онбординг"
            >
              <HelpCircle className="w-4 h-4" />
              <span className="hidden sm:inline">Помощь</span>
            </button>
            <button
              onClick={logout}
              className="flex items-center gap-2 px-4 py-2 bg-primary-dark hover:bg-primary-light rounded transition-colors"
              tabIndex={0}
              aria-label="Кнопка выхода"
            >
              <LogOut className="w-4 h-4" />
              <span>Выход</span>
            </button>
          </div>
        </div>
      </header>
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
      {showCodeExample && (
        <CodeExampleModal onClose={() => setShowCodeExample(false)} />
      )}
    </div>
  );
};

export default Layout;


