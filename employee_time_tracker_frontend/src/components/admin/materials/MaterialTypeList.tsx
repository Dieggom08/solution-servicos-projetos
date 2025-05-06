
'use client';

import React, { useState, useEffect } from 'react';

// Define the MaterialType type based on your backend model
interface MaterialType {
  id: number;
  name: string;
  description: string | null;
  expected_duration_days: number | null;
}

const MaterialTypeList: React.FC = () => {
  const [materialTypes, setMaterialTypes] = useState<MaterialType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // State for the form to add/edit material types
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [editingType, setEditingType] = useState<MaterialType | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    expected_duration_days: '',
  });

  const fetchMaterialTypes = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5004/admin/materials/types', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error('Falha ao buscar tipos de material');
      }
      const data = await response.json();
      setMaterialTypes(data);
    } catch (err: any) {
      setError(err.message || 'Ocorreu um erro ao buscar tipos de material.');
      console.error('Fetch material types error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMaterialTypes();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const url = editingType
        ? `http://localhost:5004/admin/materials/types/${editingType.id}`
        : 'http://localhost:5004/admin/materials/types';
      const method = editingType ? 'PUT' : 'POST';

      const payload = {
        ...formData,
        expected_duration_days: formData.expected_duration_days ? parseInt(formData.expected_duration_days) : null,
        description: formData.description || null,
      };

      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `Falha ao ${editingType ? 'atualizar' : 'criar'} tipo de material`);
      }

      alert(`Tipo de material ${editingType ? 'atualizado' : 'criado'} com sucesso!`);
      setIsFormVisible(false);
      setEditingType(null);
      resetForm();
      fetchMaterialTypes(); // Refresh the list

    } catch (err: any) {
      setError(err.message || 'Ocorreu um erro.');
      console.error('Submit material type error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Tem certeza que deseja excluir este tipo de material? Isso pode afetar registros de log associados.')) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5004/admin/materials/types/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error('Falha ao excluir tipo de material');
      }
      alert('Tipo de material excluído com sucesso!');
      fetchMaterialTypes(); // Refresh the list
    } catch (err: any) {
      setError(err.message || 'Ocorreu um erro ao excluir.');
      console.error('Delete material type error:', err);
    } finally {
      setLoading(false);
    }
  };

  const openEditForm = (type: MaterialType) => {
    setEditingType(type);
    setFormData({
      name: type.name,
      description: type.description || '',
      expected_duration_days: type.expected_duration_days?.toString() || '',
    });
    setIsFormVisible(true);
  };

  const openAddForm = () => {
    setEditingType(null);
    resetForm();
    setIsFormVisible(true);
  };

  const resetForm = () => {
    setFormData({ name: '', description: '', expected_duration_days: '' });
  };

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-semibold mb-4">Gerenciar Tipos de Material</h2>

      <button
        onClick={openAddForm}
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4 focus:outline-none focus:shadow-outline"
      >
        Adicionar Novo Tipo
      </button>

      {isFormVisible && (
        <div className="mb-6 p-4 bg-white rounded shadow-md">
          <h3 className="text-xl font-semibold mb-3">{editingType ? 'Editar Tipo de Material' : 'Novo Tipo de Material'}</h3>
          <form onSubmit={handleFormSubmit}>
            {error && <p className="text-red-500 text-sm mb-3">Erro: {error}</p>}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">Nome*</label>
                <input type="text" name="name" id="name" value={formData.name} onChange={handleInputChange} required className="input-field" />
              </div>
              <div>
                <label htmlFor="expected_duration_days" className="block text-sm font-medium text-gray-700 mb-1">Duração Esperada (dias)</label>
                <input type="number" name="expected_duration_days" id="expected_duration_days" value={formData.expected_duration_days} onChange={handleInputChange} className="input-field" placeholder="Ex: 30" />
              </div>
            </div>
            <div className="mb-3">
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
              <textarea name="description" id="description" value={formData.description} onChange={handleInputChange} rows={2} className="input-field"></textarea>
            </div>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => { setIsFormVisible(false); setEditingType(null); resetForm(); setError(null); }}
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                disabled={loading}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                disabled={loading}
              >
                {loading ? 'Salvando...' : (editingType ? 'Atualizar' : 'Adicionar')}
              </button>
            </div>
          </form>
        </div>
      )}

      {loading && !isFormVisible && <p className="text-center mt-4">Carregando tipos...</p>}
      {error && !isFormVisible && <p className="text-center text-red-500 mt-4">Erro: {error}</p>}

      {!loading && !error && (
        <div className="overflow-x-auto bg-white rounded shadow">
          <table className="min-w-full table-auto">
            <thead className="bg-gray-200">
              <tr>
                <th className="px-4 py-2 text-left">Nome</th>
                <th className="px-4 py-2 text-left">Descrição</th>
                <th className="px-4 py-2 text-left">Duração (dias)</th>
                <th className="px-4 py-2 text-center">Ações</th>
              </tr>
            </thead>
            <tbody>
              {materialTypes.length === 0 ? (
                <tr>
                  <td colSpan={4} className="text-center py-4">Nenhum tipo de material encontrado.</td>
                </tr>
              ) : (
                materialTypes.map((type) => (
                  <tr key={type.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">{type.name}</td>
                    <td className="px-4 py-2">{type.description || '-'}</td>
                    <td className="px-4 py-2">{type.expected_duration_days || '-'}</td>
                    <td className="px-4 py-2 text-center">
                      <button
                        onClick={() => openEditForm(type)}
                        className="text-blue-500 hover:text-blue-700 mr-2"
                      >
                        Editar
                      </button>
                      <button
                        onClick={() => handleDelete(type.id)}
                        className="text-red-500 hover:text-red-700"
                      >
                        Excluir
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Re-use input style from EmployeeForm or define globally */}
      <style jsx>{`
        .input-field {
          shadow: sm;
          appearance: none;
          border-radius: md;
          position: relative;
          display: block;
          width: 100%;
          padding: 0.5rem 0.75rem; /* py-2 px-3 */
          border: 1px solid #d1d5db; /* border-gray-300 */
          color: #374151; /* text-gray-700 */
          line-height: 1.25; /* leading-tight */
          background-color: #fff;
        }
        .input-field:focus {
          outline: none;
          border-color: #4f46e5; /* focus:border-indigo-500 */
          box-shadow: 0 0 0 1px #4f46e5; /* focus:ring-indigo-500 */
        }
      `}</style>
    </div>
  );
};

export default MaterialTypeList;

