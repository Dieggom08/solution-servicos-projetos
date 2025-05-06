
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation'; // Use useParams for edit mode

// Define the Employee type (can be shared)
interface Employee {
  id?: number; // Optional for new employees
  name: string;
  email: string;
  cpf: string;
  rg?: string; // Optional fields based on previous discussions
  pis?: string;
  phone?: string;
  address?: string;
  role: 'employee' | 'supervisor' | 'admin'; // Define roles
  admission_date?: string;
  salary?: number;
  // Add other fields as needed
}

const EmployeeForm: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const employeeId = params?.id; // Get ID from URL for edit mode
  const isEditMode = !!employeeId;

  const [employee, setEmployee] = useState<Employee>({
    name: '',
    email: '',
    cpf: '',
    role: 'employee', // Default role
    // Initialize other fields as needed
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isEditMode) {
      setLoading(true);
      const fetchEmployee = async () => {
        try {
          const token = localStorage.getItem('token');
          const response = await fetch(`http://localhost:5004/admin/employees/${employeeId}`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          if (!response.ok) {
            throw new Error('Falha ao buscar dados do funcionário');
          }
          const data = await response.json();
          // Format date if necessary before setting state
          if (data.admission_date) {
            data.admission_date = data.admission_date.split('T')[0]; // Get YYYY-MM-DD
          }
          setEmployee(data);
        } catch (err: any) {
          setError(err.message || 'Erro ao carregar funcionário.');
          console.error('Fetch employee error:', err);
        } finally {
          setLoading(false);
        }
      };
      fetchEmployee();
    }
  }, [isEditMode, employeeId]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setEmployee(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const url = isEditMode
        ? `http://localhost:5004/admin/employees/${employeeId}`
        : 'http://localhost:5004/admin/employees';
      const method = isEditMode ? 'PUT' : 'POST';

      // Prepare payload, ensure salary is number, handle optional fields
      const payload = {
        ...employee,
        salary: employee.salary ? parseFloat(employee.salary as any) : undefined,
        // Ensure empty optional fields are sent as null or omitted if backend expects that
        rg: employee.rg || undefined,
        pis: employee.pis || undefined,
        phone: employee.phone || undefined,
        address: employee.address || undefined,
        admission_date: employee.admission_date || undefined,
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
        throw new Error(errorData.message || `Falha ao ${isEditMode ? 'atualizar' : 'criar'} funcionário`);
      }

      alert(`Funcionário ${isEditMode ? 'atualizado' : 'criado'} com sucesso!`);
      router.push('/admin/employees'); // Redirect back to the list after success

    } catch (err: any) {
      setError(err.message || 'Ocorreu um erro.');
      console.error('Submit employee error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (isEditMode && loading) return <p className="text-center mt-4">Carregando dados do funcionário...</p>;

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-semibold mb-6">{isEditMode ? 'Editar Funcionário' : 'Adicionar Novo Funcionário'}</h2>
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow-md">
        {error && <p className="text-red-500 text-sm mb-4">Erro: {error}</p>}

        {/* Basic Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">Nome Completo*</label>
            <input type="text" name="name" id="name" value={employee.name} onChange={handleChange} required className="input-field" />
          </div>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email*</label>
            <input type="email" name="email" id="email" value={employee.email} onChange={handleChange} required className="input-field" />
          </div>
          <div>
            <label htmlFor="cpf" className="block text-sm font-medium text-gray-700 mb-1">CPF*</label>
            <input type="text" name="cpf" id="cpf" value={employee.cpf} onChange={handleChange} required className="input-field" placeholder="000.000.000-00" />
          </div>
          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
            <input type="tel" name="phone" id="phone" value={employee.phone || ''} onChange={handleChange} className="input-field" placeholder="(00) 90000-0000" />
          </div>
        </div>

        {/* Documents */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label htmlFor="rg" className="block text-sm font-medium text-gray-700 mb-1">RG</label>
            <input type="text" name="rg" id="rg" value={employee.rg || ''} onChange={handleChange} className="input-field" />
          </div>
          <div>
            <label htmlFor="pis" className="block text-sm font-medium text-gray-700 mb-1">PIS</label>
            <input type="text" name="pis" id="pis" value={employee.pis || ''} onChange={handleChange} className="input-field" />
          </div>
        </div>

        {/* Address */}
        <div className="mb-4">
          <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">Endereço</label>
          <textarea name="address" id="address" value={employee.address || ''} onChange={handleChange} rows={3} className="input-field"></textarea>
        </div>

        {/* Employment Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-1">Cargo*</label>
            <select name="role" id="role" value={employee.role} onChange={handleChange} required className="input-field">
              <option value="employee">Funcionário</option>
              <option value="supervisor">Supervisor</option>
              <option value="admin">Administrador</option>
            </select>
          </div>
          <div>
            <label htmlFor="admission_date" className="block text-sm font-medium text-gray-700 mb-1">Data de Admissão</label>
            <input type="date" name="admission_date" id="admission_date" value={employee.admission_date || ''} onChange={handleChange} className="input-field" />
          </div>
          <div>
            <label htmlFor="salary" className="block text-sm font-medium text-gray-700 mb-1">Salário (R$)</label>
            <input type="number" step="0.01" name="salary" id="salary" value={employee.salary || ''} onChange={handleChange} className="input-field" placeholder="1500.00" />
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end mt-6">
          <button
            type="button" // Go back button
            onClick={() => router.back()} // Or router.push('/admin/employees')
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded mr-2 focus:outline-none focus:shadow-outline"
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            disabled={loading}
          >
            {loading ? 'Salvando...' : (isEditMode ? 'Atualizar Funcionário' : 'Adicionar Funcionário')}
          </button>
        </div>
      </form>

      {/* Simple CSS for input fields - can be moved to globals.css */}
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

export default EmployeeForm;


