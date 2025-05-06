
'use client';

import React, { useState, useEffect } from 'react';

// Define types based on backend models
interface MaterialLog {
  id: number;
  employee_id: number;
  employee_name: string; // Assuming backend provides this
  material_type_id: number;
  material_type_name: string; // Assuming backend provides this
  quantity: number;
  delivery_date: string;
  expected_replacement_date: string | null;
}

interface Employee {
  id: number;
  name: string;
}

interface MaterialType {
  id: number;
  name: string;
}

const MaterialLogList: React.FC = () => {
  const [logs, setLogs] = useState<MaterialLog[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [materialTypes, setMaterialTypes] = useState<MaterialType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // State for filters
  const [filterEmployeeId, setFilterEmployeeId] = useState<string>('');
  const [filterMaterialTypeId, setFilterMaterialTypeId] = useState<string>('');
  const [filterStartDate, setFilterStartDate] = useState<string>('');
  const [filterEndDate, setFilterEndDate] = useState<string>('');

  // State for adding new log
  const [isAddFormVisible, setIsAddFormVisible] = useState(false);
  const [newLogData, setNewLogData] = useState({
    employee_id: '',
    material_type_id: '',
    quantity: 1,
    delivery_date: new Date().toISOString().split('T')[0], // Default to today
  });

  // Fetch logs based on filters
  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const queryParams = new URLSearchParams();
      if (filterEmployeeId) queryParams.append('employee_id', filterEmployeeId);
      if (filterMaterialTypeId) queryParams.append('material_type_id', filterMaterialTypeId);
      if (filterStartDate) queryParams.append('start_date', filterStartDate);
      if (filterEndDate) queryParams.append('end_date', filterEndDate);

      const response = await fetch(`http://localhost:5004/admin/materials/logs?${queryParams.toString()}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Falha ao buscar registros de materiais');
      const data = await response.json();
      setLogs(data);
    } catch (err: any) {
      setError(err.message || 'Erro ao buscar registros.');
      console.error('Fetch logs error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch employees and material types for dropdowns
  const fetchDropdownData = async () => {
    try {
      const token = localStorage.getItem('token');
      const [empRes, typeRes] = await Promise.all([
        fetch('http://localhost:5004/admin/employees', { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch('http://localhost:5004/admin/materials/types', { headers: { 'Authorization': `Bearer ${token}` } })
      ]);
      if (empRes.ok) setEmployees(await empRes.json());
      if (typeRes.ok) setMaterialTypes(await typeRes.json());
    } catch (err) {
      console.error('Failed to fetch dropdown data:', err);
      // Handle error appropriately, maybe show a message
    }
  };

  useEffect(() => {
    fetchLogs();
    fetchDropdownData();
  }, [filterEmployeeId, filterMaterialTypeId, filterStartDate, filterEndDate]);

  const handleAddInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setNewLogData(prev => ({ ...prev, [name]: value }));
  };

  const handleAddLogSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const payload = {
        ...newLogData,
        employee_id: parseInt(newLogData.employee_id),
        material_type_id: parseInt(newLogData.material_type_id),
        quantity: parseInt(newLogData.quantity as any),
      };

      const response = await fetch('http://localhost:5004/admin/materials/logs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Falha ao registrar entrega');
      }

      alert('Entrega registrada com sucesso!');
      setIsAddFormVisible(false);
      resetAddForm();
      fetchLogs(); // Refresh the list

    } catch (err: any) {
      setError(err.message || 'Ocorreu um erro ao registrar.');
      console.error('Add log error:', err);
    } finally {
      setLoading(false);
    }
  };

  const resetAddForm = () => {
    setNewLogData({
      employee_id: '',
      material_type_id: '',
      quantity: 1,
      delivery_date: new Date().toISOString().split('T')[0],
    });
  };

  // Function to format date strings
  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    try {
      const [year, month, day] = dateString.split('T')[0].split('-').map(Number);
      return new Date(year, month - 1, day).toLocaleDateString('pt-BR');
    } catch (e) {
      return dateString;
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-semibold mb-4">Registros de Entrega de Material</h2>

      {/* Filter Section */}
      <div className="mb-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-gray-50 rounded shadow">
        <div>
          <label htmlFor="filterEmployeeId" className="block text-sm font-medium text-gray-700 mb-1">Funcionário:</label>
          <select id="filterEmployeeId" value={filterEmployeeId} onChange={(e) => setFilterEmployeeId(e.target.value)} className="input-field">
            <option value="">Todos</option>
            {employees.map(emp => <option key={emp.id} value={emp.id}>{emp.name}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="filterMaterialTypeId" className="block text-sm font-medium text-gray-700 mb-1">Tipo Material:</label>
          <select id="filterMaterialTypeId" value={filterMaterialTypeId} onChange={(e) => setFilterMaterialTypeId(e.target.value)} className="input-field">
            <option value="">Todos</option>
            {materialTypes.map(type => <option key={type.id} value={type.id}>{type.name}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="filterStartDate" className="block text-sm font-medium text-gray-700 mb-1">Data Entrega (Início):</label>
          <input type="date" id="filterStartDate" value={filterStartDate} onChange={(e) => setFilterStartDate(e.target.value)} className="input-field" />
        </div>
        <div>
          <label htmlFor="filterEndDate" className="block text-sm font-medium text-gray-700 mb-1">Data Entrega (Fim):</label>
          <input type="date" id="filterEndDate" value={filterEndDate} onChange={(e) => setFilterEndDate(e.target.value)} className="input-field" />
        </div>
      </div>

      <button
        onClick={() => setIsAddFormVisible(true)}
        className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded mb-4 focus:outline-none focus:shadow-outline"
      >
        Registrar Nova Entrega
      </button>

      {/* Add New Log Form (Modal or Inline) */}
      {isAddFormVisible && (
        <div className="mb-6 p-4 bg-white rounded shadow-md">
          <h3 className="text-xl font-semibold mb-3">Registrar Nova Entrega</h3>
          <form onSubmit={handleAddLogSubmit}>
            {error && <p className="text-red-500 text-sm mb-3">Erro: {error}</p>}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
              <div>
                <label htmlFor="employee_id" className="block text-sm font-medium text-gray-700 mb-1">Funcionário*</label>
                <select name="employee_id" id="employee_id" value={newLogData.employee_id} onChange={handleAddInputChange} required className="input-field">
                  <option value="" disabled>Selecione...</option>
                  {employees.map(emp => <option key={emp.id} value={emp.id}>{emp.name}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="material_type_id" className="block text-sm font-medium text-gray-700 mb-1">Tipo Material*</label>
                <select name="material_type_id" id="material_type_id" value={newLogData.material_type_id} onChange={handleAddInputChange} required className="input-field">
                  <option value="" disabled>Selecione...</option>
                  {materialTypes.map(type => <option key={type.id} value={type.id}>{type.name}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">Quantidade*</label>
                <input type="number" name="quantity" id="quantity" value={newLogData.quantity} onChange={handleAddInputChange} required min="1" className="input-field" />
              </div>
              <div>
                <label htmlFor="delivery_date" className="block text-sm font-medium text-gray-700 mb-1">Data Entrega*</label>
                <input type="date" name="delivery_date" id="delivery_date" value={newLogData.delivery_date} onChange={handleAddInputChange} required className="input-field" />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => { setIsAddFormVisible(false); resetAddForm(); setError(null); }}
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
                {loading ? 'Registrando...' : 'Registrar Entrega'}
              </button>
            </div>
          </form>
        </div>
      )}

      {loading && !isAddFormVisible && <p className="text-center mt-4">Carregando registros...</p>}
      {error && !isAddFormVisible && <p className="text-center text-red-500 mt-4">Erro: {error}</p>}

      {!loading && !error && (
        <div className="overflow-x-auto bg-white rounded shadow">
          <table className="min-w-full table-auto">
            <thead className="bg-gray-200">
              <tr>
                <th className="px-4 py-2 text-left">Funcionário</th>
                <th className="px-4 py-2 text-left">Material</th>
                <th className="px-4 py-2 text-left">Quantidade</th>
                <th className="px-4 py-2 text-left">Data Entrega</th>
                <th className="px-4 py-2 text-left">Próxima Troca Esperada</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-4">Nenhum registro encontrado para os filtros selecionados.</td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">{log.employee_name}</td>
                    <td className="px-4 py-2">{log.material_type_name}</td>
                    <td className="px-4 py-2">{log.quantity}</td>
                    <td className="px-4 py-2">{formatDate(log.delivery_date)}</td>
                    <td className="px-4 py-2">{formatDate(log.expected_replacement_date)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Re-use input style */}
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
        select.input-field {
          padding-right: 2.5rem; /* Add space for arrow */
        }
      `}</style>
    </div>
  );
};

export default MaterialLogList;

