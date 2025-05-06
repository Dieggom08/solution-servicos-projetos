
'use client';

import React, { useState, useEffect } from 'react';

interface LatenessRecord {
  employee_id: number;
  employee_name: string;
  date: string;
  check_in_time: string;
  expected_check_in: string; // Assuming backend provides this
  lateness_duration: string; // e.g., "00:15:30"
}

const LatenessReport: React.FC = () => {
  const [reportData, setReportData] = useState<LatenessRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStartDate, setFilterStartDate] = useState<string>('');
  const [filterEndDate, setFilterEndDate] = useState<string>('');

  const fetchReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const queryParams = new URLSearchParams();
      if (filterStartDate) queryParams.append('start_date', filterStartDate);
      if (filterEndDate) queryParams.append('end_date', filterEndDate);

      const response = await fetch(`http://localhost:5004/admin/reports/lateness?${queryParams.toString()}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error('Falha ao buscar relatório de atrasos');
      }
      const data = await response.json();
      setReportData(data);
    } catch (err: any) {
      setError(err.message || 'Ocorreu um erro ao buscar o relatório.');
      console.error('Fetch lateness report error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Fetch report initially and whenever filters change
    fetchReport();
  }, [filterStartDate, filterEndDate]);

  const handleDownloadPdf = async () => {
    try {
      const token = localStorage.getItem('token');
      const queryParams = new URLSearchParams();
      if (filterStartDate) queryParams.append('start_date', filterStartDate);
      if (filterEndDate) queryParams.append('end_date', filterEndDate);

      const response = await fetch(`http://localhost:5004/admin/reports/lateness/pdf?${queryParams.toString()}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Falha ao gerar PDF do relatório');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `relatorio_atrasos_${filterStartDate}_a_${filterEndDate}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

    } catch (err: any) {
      setError(err.message || 'Ocorreu um erro ao gerar o PDF.');
      console.error('Download PDF error:', err);
    }
  };

  // Function to format date/time strings (optional, adjust as needed)
  const formatDateTime = (dateTimeString: string | null) => {
    if (!dateTimeString) return '-';
    try {
      return new Date(dateTimeString).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch (e) {
      return dateTimeString;
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    try {
      const [year, month, day] = dateString.split('-').map(Number);
      return new Date(year, month - 1, day).toLocaleDateString('pt-BR');
    } catch (e) {
      return dateString;
    }
  };


  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-semibold mb-4">Relatório de Atrasos</h2>

      {/* Filter Section */}
      <div className="mb-4 flex flex-wrap gap-4 p-4 bg-gray-50 rounded shadow">
        <div>
          <label htmlFor="filterStartDate" className="block text-sm font-medium text-gray-700 mb-1">Data Início:</label>
          <input
            type="date"
            id="filterStartDate"
            value={filterStartDate}
            onChange={(e) => setFilterStartDate(e.target.value)}
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2"
          />
        </div>
        <div>
          <label htmlFor="filterEndDate" className="block text-sm font-medium text-gray-700 mb-1">Data Fim:</label>
          <input
            type="date"
            id="filterEndDate"
            value={filterEndDate}
            onChange={(e) => setFilterEndDate(e.target.value)}
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2"
          />
        </div>
        <div className="self-end">
          <button
            onClick={handleDownloadPdf}
            className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            disabled={loading}
          >
            {loading ? 'Gerando...' : 'Baixar PDF'}
          </button>
        </div>
      </div>

      {loading && <p className="text-center mt-4">Carregando relatório...</p>}
      {error && <p className="text-center text-red-500 mt-4">Erro: {error}</p>}

      {!loading && !error && (
        <div className="overflow-x-auto bg-white rounded shadow">
          <table className="min-w-full table-auto">
            <thead className="bg-gray-200">
              <tr>
                <th className="px-4 py-2 text-left">Funcionário</th>
                <th className="px-4 py-2 text-left">Data</th>
                <th className="px-4 py-2 text-left">Hora Entrada</th>
                <th className="px-4 py-2 text-left">Entrada Esperada</th>
                <th className="px-4 py-2 text-left">Duração Atraso</th>
              </tr>
            </thead>
            <tbody>
              {reportData.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-4">Nenhum atraso encontrado para o período selecionado.</td>
                </tr>
              ) : (
                reportData.map((record, index) => (
                  <tr key={`${record.employee_id}-${record.date}-${index}`} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">{record.employee_name}</td>
                    <td className="px-4 py-2">{formatDate(record.date)}</td>
                    <td className="px-4 py-2">{formatDateTime(record.check_in_time)}</td>
                    <td className="px-4 py-2">{record.expected_check_in}</td>
                    <td className="px-4 py-2">{record.lateness_duration}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default LatenessReport;

