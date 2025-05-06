
'use client';

import React, { useState } from 'react';
import EmployeeList from '@/components/admin/EmployeeList';
import EmployeeForm from '@/components/admin/EmployeeForm';
import { Button } from '@/components/ui/button'; // Assuming shadcn/ui is used

const AdminEmployeesPage: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<any>(null); // Adjust type as needed
  const [refreshKey, setRefreshKey] = useState(0); // To trigger list refresh

  const handleEdit = (employee: any) => {
    setEditingEmployee(employee);
    setShowForm(true);
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingEmployee(null);
    setRefreshKey(prev => prev + 1); // Refresh list after closing form
  };

  const handleAddNew = () => {
    setEditingEmployee(null);
    setShowForm(true);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Gerenciar Funcionários</h1>

      {showForm ? (
        <EmployeeForm
          employeeData={editingEmployee}
          onClose={handleFormClose}
        />
      ) : (
        <>
          <Button onClick={handleAddNew} className="mb-4">
            Adicionar Novo Funcionário
          </Button>
          <EmployeeList key={refreshKey} onEdit={handleEdit} />
        </>
      )}
    </div>
  );
};

export default AdminEmployeesPage;

