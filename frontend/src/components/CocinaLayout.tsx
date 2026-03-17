import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ChefHat, LogOut, Menu, X } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

interface CocinaLayoutProps {
  children: React.ReactNode;
}

const navItems = [
  { label: 'Pedidos cocina', href: '/cocina/pedidos', icon: <ChefHat size={20} /> },
];

export const CocinaLayout: React.FC<CocinaLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (href: string) => location.pathname === href || location.pathname.startsWith(`${href}/`);

  return (
    <div className="flex h-screen bg-gray-50">
      {sidebarOpen && (
        <button
          className="fixed inset-0 bg-black/40 lg:hidden z-30"
          onClick={() => setSidebarOpen(false)}
          aria-label="Cerrar menú"
        />
      )}

      <aside
        className={`fixed lg:static top-0 left-0 h-full w-64 bg-white border-r border-gray-200 z-40 transform transition-transform duration-200 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="p-5 border-b border-gray-100 flex items-center justify-between">
          <h1 className="text-xl font-bold text-primary-600">Panel Cocina</h1>
          <button className="lg:hidden" onClick={() => setSidebarOpen(false)}>
            <X size={20} />
          </button>
        </div>

        <nav className="p-4 space-y-2">
          {navItems.map((item) => (
            <Link
              key={item.href}
              to={item.href}
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg transition ${
                isActive(item.href) ? 'bg-primary-100 text-primary-700 font-medium' : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              {item.icon}
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white border-b border-gray-200 px-4 sm:px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button className="lg:hidden" onClick={() => setSidebarOpen(true)}>
              <Menu size={22} />
            </button>
            <div>
              <p className="font-medium text-gray-900">{user?.nombre || 'Cocina'}</p>
              <p className="text-xs text-gray-500">Seguimiento de pedidos</p>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="p-2 hover:bg-red-50 text-red-600 rounded-lg transition"
            title="Cerrar sesión"
          >
            <LogOut size={20} />
          </button>
        </header>

        <main className="flex-1 overflow-y-auto p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
};