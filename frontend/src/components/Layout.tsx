import { ReactNode } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { LogOut } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const { logout } = useAuth();

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <header className="bg-primary text-white shadow-md">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <h1 className="text-xl font-bold">Scripts Manager</h1>
          <button
            onClick={logout}
            className="flex items-center gap-2 px-4 py-2 bg-primary-dark hover:bg-primary-light rounded transition-colors"
            tabIndex={0}
            aria-label="Logout button"
          >
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </button>
        </div>
      </header>
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
    </div>
  );
};

export default Layout;


