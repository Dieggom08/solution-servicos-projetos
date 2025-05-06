
'use client';

import React from 'react';
import LatenessReport from '@/components/admin/LatenessReport';
// Import other report components as needed
// import HoursWorkedReport from '@/components/admin/HoursWorkedReport';
// import AbsencesReport from '@/components/admin/AbsencesReport';

const AdminReportsPage: React.FC = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Relatórios</h1>
      <div className="space-y-6">
        {/* Lateness Report Section */}
        <section>
          <h2 className="text-xl font-semibold mb-2">Relatório de Atrasos</h2>
          <LatenessReport />
        </section>

        {/* Placeholder for Hours Worked Report */}
        {/* <section>
          <h2 className="text-xl font-semibold mb-2">Relatório de Horas Trabalhadas</h2>
          <HoursWorkedReport />
        </section> */}

        {/* Placeholder for Absences Report */}
        {/* <section>
          <h2 className="text-xl font-semibold mb-2">Relatório de Ausências</h2>
          <AbsencesReport />
        </section> */}
      </div>
    </div>
  );
};

export default AdminReportsPage;

