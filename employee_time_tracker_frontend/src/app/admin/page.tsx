
'use client';

import React from 'react';
import Link from 'next/link';

const AdminDashboard: React.FC = () => {
  // Placeholder for authentication check - in a real app, protect this route

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold mb-8 text-gray-800">Painel Administrativo</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Card Funcionários */}
        <Link href="/admin/employees" legacyBehavior>
          <a className="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
            <h2 className="text-xl font-semibold mb-2 text-blue-600">Gerenciar Funcionários</h2>
            <p className="text-gray-600">Adicionar, visualizar, editar e remover funcionários.</p>
          </a>
        </Link>

        {/* Card Registros de Ponto */}
        <Link href="/admin/time-records" legacyBehavior>
          <a className="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
            <h2 className="text-xl font-semibold mb-2 text-green-600">Registros de Ponto</h2>
            <p className="text-gray-600">Visualizar e filtrar os registros de ponto dos funcionários.</p>
          </a>
        </Link>

        {/* Card Relatórios */}
        <Link href="/admin/reports" legacyBehavior>
          <a className="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
            <h2 className="text-xl font-semibold mb-2 text-purple-600">Relatórios</h2>
            <p className="text-gray-600">Gerar relatórios de atrasos, horas trabalhadas e ausências.</p>
          </a>
        </Link>

        {/* Card Materiais */}
        <Link href="/admin/materials" legacyBehavior>
          <a className="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
            <h2 className="text-xl font-semibold mb-2 text-orange-600">Controle de Materiais</h2>
            <p className="text-gray-600">Gerenciar tipos de materiais e registrar entregas.</p>
          </a>
        </Link>

        {/* Adicionar mais cards conforme necessário */}

      </div>
    </div>
  );
};

export default AdminDashboard;

