import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  BarChart3,
  History,
  Users,
  UtensilsCrossed,
  Tag,
  Settings,
  X,
} from 'lucide-react';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
  badge?: string;
}

const navItems: NavItem[] = [
  { label: 'Dashboard', href: '/admin', icon: <BarChart3 size={20} /> },
  { label: 'Usuarios', href: '/admin/usuarios', icon: <Users size={20} /> },
  { label: 'Productos', href: '/admin/productos', icon: <UtensilsCrossed size={20} /> },
  { label: 'Descuentos', href: '/admin/descuentos', icon: <Tag size={20} /> },
  { label: 'Configuración', href: '/admin/configuracion', icon: <Settings size={20} /> },
  { label: 'Historial', href: '/admin/historial', icon: <History size={20} /> },
];

export const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const location = useLocation();
  const isActive = (href: string) => location.pathname === href;

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 lg:hidden z-30"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed top-0 left-0 h-full w-64 bg-white border-r border-gray-200 z-40 transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ marginTop: '60px' }}
      >
        <div className="p-6 flex flex-col gap-6">
          <button
            onClick={onClose}
            className="lg:hidden absolute top-4 right-4 p-2 hover:bg-gray-100 rounded-lg"
          >
            <X size={20} />
          </button>

          <nav className="space-y-2 mt-8 lg:mt-0">
            {navItems.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                onClick={onClose}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                  isActive(item.href)
                    ? 'bg-primary-100 text-primary-700 font-medium'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
                {item.badge && (
                  <span className="ml-auto bg-primary-600 text-white text-xs px-2 py-1 rounded-full">
                    {item.badge}
                  </span>
                )}
              </Link>
            ))}
          </nav>
        </div>
      </aside>
    </>
  );
};
