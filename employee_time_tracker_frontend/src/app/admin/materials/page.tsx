
'use client';

import React, { useState } from 'react';
import MaterialTypeList from '@/components/admin/materials/MaterialTypeList';
import MaterialLogList from '@/components/admin/materials/MaterialLogList';
// Import form components when created
// import MaterialTypeForm from '@/components/admin/materials/MaterialTypeForm';
// import MaterialLogForm from '@/components/admin/materials/MaterialLogForm';
import { Button } from '@/components/ui/button'; // Assuming shadcn/ui

const AdminMaterialsPage: React.FC = () => {
  const [view, setView] = useState<'types' | 'logs'>('types'); // Control view
  // State for forms (add later)
  // const [showTypeForm, setShowTypeForm] = useState(false);
  // const [showLogForm, setShowLogForm] = useState(false);
  // const [editingType, setEditingType] = useState<any>(null);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Controle de Materiais</h1>

      <div className="mb-4 space-x-2">
        <Button variant={view === 'types' ? 'default' : 'outline'} onClick={() => setView('types')}>Gerenciar Tipos</Button>
        <Button variant={view === 'logs' ? 'default' : 'outline'} onClick={() => setView('logs')}>Ver Entregas</Button>
      </div>

      {view === 'types' && (
        <section>
          <h2 className="text-xl font-semibold mb-2">Tipos de Material</h2>
          {/* Add Button for new type form later */}
          {/* <Button onClick={() => { setEditingType(null); setShowTypeForm(true); }} className="mb-4">Adicionar Novo Tipo</Button> */}
          {/* {showTypeForm ? <MaterialTypeForm typeData={editingType} onClose={() => setShowTypeForm(false)} /> : <MaterialTypeList onEdit={(type) => { setEditingType(type); setShowTypeForm(true); }} />} */}
          <MaterialTypeList onEdit={() => {}} /> {/* Placeholder onEdit */}
        </section>
      )}

      {view === 'logs' && (
        <section>
          <h2 className="text-xl font-semibold mb-2">Registros de Entrega</h2>
           {/* Add Button for new log form later */}
          {/* <Button onClick={() => setShowLogForm(true)} className="mb-4">Registrar Nova Entrega</Button> */}
          {/* {showLogForm ? <MaterialLogForm onClose={() => setShowLogForm(false)} /> : <MaterialLogList />} */}
          <MaterialLogList />
        </section>
      )}

    </div>
  );
};

export default AdminMaterialsPage;

