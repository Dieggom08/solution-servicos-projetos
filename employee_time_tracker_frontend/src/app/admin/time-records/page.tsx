
'use client';

import React from 'react';
import TimeRecordList from '@/components/admin/TimeRecordList';

const AdminTimeRecordsPage: React.FC = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Registros de Ponto</h1>
      <TimeRecordList />
    </div>
  );
};

export default AdminTimeRecordsPage;

