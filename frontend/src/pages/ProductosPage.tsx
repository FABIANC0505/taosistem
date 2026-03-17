import React, { useEffect, useState } from 'react';
import { Plus, Edit2, Trash2, Package } from 'lucide-react';
import { AdminLayout } from '../components/AdminLayout';
import { Product } from '../types';
import { productService } from '../services/productService';

export const ProductosPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [formData, setFormData] = useState({
    nombre: '',
    precio: '',
    descripcion: '',
    categoria: '',
    imagen: null as File | null,
  });

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await productService.getAll();
      setProducts(data);
    } catch (err) {
      setError('Error al cargar productos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({ nombre: '', precio: '', descripcion: '', categoria: '', imagen: null });
    setEditingProduct(null);
    setShowForm(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const form = new FormData();
      form.append('nombre', formData.nombre);
      form.append('precio', formData.precio);
      form.append('descripcion', formData.descripcion);
      form.append('categoria', formData.categoria);
      if (formData.imagen) {
        form.append('imagen', formData.imagen);
      }

      if (editingProduct) {
        await productService.update(editingProduct.id, form);
      } else {
        await productService.create(form);
      }

      resetForm();
      await loadProducts();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al guardar producto');
    }
  };

  const handleEdit = (product: Product) => {
    setEditingProduct(product);
    setFormData({
      nombre: product.nombre,
      precio: product.precio.toString(),
      descripcion: product.descripcion || '',
      categoria: product.categoria,
      imagen: null,
    });
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar este producto?')) {
      try {
        await productService.delete(id);
        await loadProducts();
      } catch (err) {
        setError('Error al eliminar producto');
      }
    }
  };

  const handleMarkOutOfStock = async (id: string) => {
    try {
      await productService.markAsOutOfStock(id);
      await loadProducts();
    } catch (err) {
      setError('Error al marcar como agotado');
    }
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gestión de Productos</h1>
            <p className="text-gray-600 mt-2">Administra el menú del restaurante</p>
          </div>
          <button
            onClick={() => {
              if (showForm && editingProduct) {
                resetForm();
              } else {
                setShowForm(!showForm);
              }
            }}
            className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition"
          >
            <Plus size={20} />
            {showForm ? 'Cerrar Formulario' : 'Nuevo Producto'}
          </button>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Formulario */}
        {showForm && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">{editingProduct ? 'Editar Producto' : 'Crear Nuevo Producto'}</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Nombre del producto"
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  required
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                />
                <input
                  type="number"
                  placeholder="Precio"
                  step="0.01"
                  value={formData.precio}
                  onChange={(e) => setFormData({ ...formData, precio: e.target.value })}
                  required
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                />
                <input
                  type="text"
                  placeholder="Categoría"
                  value={formData.categoria}
                  onChange={(e) => setFormData({ ...formData, categoria: e.target.value })}
                  required
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                />
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setFormData({ ...formData, imagen: e.target.files?.[0] || null })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                />
              </div>
              <textarea
                placeholder="Descripción"
                value={formData.descripcion}
                onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                rows={3}
              ></textarea>
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition"
                >
                  {editingProduct ? 'Guardar Cambios' : 'Crear'}
                </button>
                <button
                  type="button"
                  onClick={resetForm}
                  className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-lg transition"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Grid de productos */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            <div className="col-span-full flex items-center justify-center p-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
          ) : products.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <Package size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600">No hay productos registrados</p>
            </div>
          ) : (
            products.map((product) => (
              <div key={product.id} className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition">
                {product.imagen_url && (
                  <img
                    src={product.imagen_url}
                    alt={product.nombre}
                    className="w-full h-48 object-cover"
                  />
                )}
                <div className="p-6">
                  <h3 className="font-semibold text-lg text-gray-900">{product.nombre}</h3>
                  <p className="text-gray-600 text-sm mt-1">{product.descripcion}</p>
                  <div className="flex items-center justify-between mt-4">
                    <span className="text-2xl font-bold text-primary-600">${product.precio.toFixed(2)}</span>
                    <span className={`text-xs px-3 py-1 rounded-full font-medium ${product.disponible ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                      {product.disponible ? 'Disponible' : 'Agotado'}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">Categoría: {product.categoria}</p>
                  <div className="flex gap-2 mt-4">
                    <button
                      onClick={() => handleEdit(product)}
                      className="flex-1 p-2 border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50 transition flex items-center justify-center gap-2"
                    >
                      <Edit2 size={16} />
                      Editar
                    </button>
                    <button
                      onClick={() => handleDelete(product.id)}
                      className="flex-1 p-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition flex items-center justify-center gap-2"
                    >
                      <Trash2 size={16} />
                      Eliminar
                    </button>
                  </div>
                  {product.disponible && (
                    <button
                      onClick={() => handleMarkOutOfStock(product.id)}
                      className="w-full mt-2 p-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition text-sm font-medium"
                    >
                      Marcar como Agotado
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </AdminLayout>
  );
};
