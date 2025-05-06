
'use client';

import React, { useState, useEffect } from 'react';

// Define the Employee type based on your backend model
interface Employee {
  id: number;
  name: string;
  email: string;
  cpf: string;
  role: string;
  // Add other relevant fields
}

const EmployeeList: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEmployees = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem('token'); // Assuming token is stored in localStorage
        const response = await fetch('http://localhost:5004/admin/employees', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        if (!response.ok) {
          throw new Error('Falha ao buscar funcionários');
        }
        const data = await response.json();
        setEmployees(data);
      } catch (err: any) {
        setError(err.message || 'Ocorreu um erro ao buscar funcionários.');
        console.error('Fetch employees error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchEmployees();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Tem certeza que deseja excluir este funcionário?')) {
      return;
    }
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5004/admin/employees/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error('Falha ao excluir funcionário');
      }
      setEmployees(employees.filter(emp => emp.id !== id));
      alert('Funcionário excluído com sucesso!');
    } catch (err: any) {
      setError(err.message || 'Ocorreu um erro ao excluir funcionário.');
      console.error('Delete employee error:', err);
    }
  };

  if (loading) return <p className="text-center mt-4">Carregando funcionários...</p>;
  if (error) return <p className="text-center text-red-500 mt-4">Erro: {error}</p>;

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-semibold mb-4">Lista de Funcionários</h2>
      {/* Add button to navigate to EmployeeForm for adding new employee */}
      {/* <Link href="/admin/employees/new"> */}
      {/*   <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4"> */}
      {/*     Adicionar Funcionário */}
      {/*   </button> */}
      {/* </Link> */}
      <div className="overflow-x-auto bg-white rounded shadow">
        <table className="min-w-full table-auto">
          <thead className="bg-gray-200">
            <tr>
              <th className="px-4 py-2 text-left">Nome</th>
              <th className="px-4 py-2 text-left">Email</th>
              <th className="px-4 py-2 text-left">CPF</th>
              <th className="px-4 py-2 text-left">Cargo</th>
              <th className="px-4 py-2 text-center">Ações</th>
            </tr>
          </thead>
          <tbody>
            {employees.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-4">Nenhum funcionário encontrado.</td>
              </tr>
            ) : (
              employees.map((employee) => (
                <tr key={employee.id} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-2">{employee.name}</td>
                  <td className="px-4 py-2">{employee.email}</td>
                  <td className="px-4 py-2">{employee.cpf}</td>
                  <td className="px-4 py-2">{employee.role}</td>
                  <td className="px-4 py-2 text-center">
                    {/* Add Link to EmployeeForm for editing */}
                    {/* <Link href={`/admin/employees/edit/${employee.id}`}> */}
                    {/*   <button className="text-blue-500 hover:text-blue-700 mr-2">Editar</button> */}
                    {/* </Link> */}
                    <button
                      onClick={() => handleDelete(employee.id)}
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
    </div>
  );
};

export default EmployeeList;

