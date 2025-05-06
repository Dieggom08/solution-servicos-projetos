
'use client';

import React, { useState, useEffect } from 'react';

// Define the TimeRecord type based on your backend model
interface TimeRecord {
  id: number;
  employee_id: number;
  employee_name: string; // Assuming backend provides this for convenience
  timestamp: string; // Changed from multiple fields to single timestamp
  record_type: 'arrival' | 'departure' | 'lunch_start' | 'lunch_end'; // Added record_type
  latitude?: number | null;
  longitude?: number | null;
  photo_url?: string | null;
}

// Helper to group records by date and employee
interface DailyRecord {
  date: string;
  employee_id: number;
  employee_name: string;
  arrival: string | null;
  lunch_start: string | null;
  lunch_end: string | null;
  departure: string | null;
}

const groupRecords = (records: TimeRecord[]): DailyRecord[] => {
  const grouped: { [key: string]: DailyRecord } = {};

  records.forEach(record => {
    const recordDate = new Date(record.timestamp).toLocaleDateString('pt-BR', { timeZone: 'UTC' }); // Group by date (UTC)
    const recordTime = new Date(record.timestamp).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit', timeZone: 'UTC' });
    const key = `${record.employee_id}-${recordDate}`;

    if (!grouped[key]) {
      grouped[key] = {
        date: recordDate,
        employee_id: record.employee_id,
        employee_name: record.employee_name,
        arrival: null,
        lunch_start: null,
        lunch_end: null,
        departure: null,
      };
    }

    switch (record.record_type) {
      case 'arrival':
        grouped[key].arrival = recordTime;
        break;
      case 'lunch_start':
        grouped[key].lunch_start = recordTime;
        break;
      case 'lunch_end':
        grouped[key].lunch_end = recordTime;
        break;
      case 'departure':
        grouped[key].departure = recordTime;
        break;
    }
  });

  // Sort by date descending, then by employee name
  return Object.values(grouped).sort((a, b) => {
    const dateA = a.date.split('/').reverse().join('-');
    const dateB = b.date.split('/').reverse().join('-');
    if (dateB !== dateA) return dateB.localeCompare(dateA);
    return a.employee_name.localeCompare(b.employee_name);
  });
};


const TimeRecordList: React.FC = () => {
  const [groupedRecords, setGroupedRecords] = useState<DailyRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStartDate, setFilterStartDate] = useState<string>('');
  const [filterEndDate, setFilterEndDate] = useState<string>('');
  const [filterEmployeeId, setFilterEmployeeId] = useState<string>('');

  // Function to format date/time strings (optional, adjust as needed)
  const formatTime = (timeString: string | null) => {
    return timeString || '-';
  };

  useEffect(() => {
    const fetchTimeRecords = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem('token');
        // Construct query parameters based on filters
        const queryParams = new URLSearchParams();
        if (filterStartDate) queryParams.append('start_date', filterStartDate);
        if (filterEndDate) queryParams.append('end_date', filterEndDate);
        if (filterEmployeeId) queryParams.append('employee_id', filterEmployeeId);

        // Corrected endpoint with hyphen
        const response = await fetch(`http://localhost:5004/admin/time-records?${queryParams.toString()}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        const responseText = await response.text(); // Read response as text first
        // console.log("Raw response:", responseText);

        if (!response.ok) {
          // Try to parse error message if backend sends JSON error
          try {
            const errorData = JSON.parse(responseText);
            throw new Error(errorData.error || `Falha ao buscar registros: ${response.statusText}`);
          } catch (parseError) {
            // If parsing fails, use the raw text or status text
            throw new Error(`Falha ao buscar registros: ${response.statusText} - ${responseText.substring(0, 100)}`);
          }
        }

        // If response is OK, parse as JSON
        const data: TimeRecord[] = JSON.parse(responseText);
        setGroupedRecords(groupRecords(data)); // Group the fetched records

      } catch (err: any) {
        setError(err.message || 'Ocorreu um erro ao buscar registros.');
        console.error('Fetch time records error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTimeRecords();
  }, [filterStartDate, filterEndDate, filterEmployeeId]); // Refetch when filters change

  // TODO: Fetch employee list for the filter dropdown

  if (loading) return <p className="text-center mt-4">Carregando registros...</p>;

  return (
    <div className="container mx-auto p-4">
      {/* Filter Section */}
      <div className="mb-4 flex flex-wrap gap-4 p-4 bg-gray-100 dark:bg-gray-800 rounded shadow">
        <div>
          <label htmlFor="filterStartDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Data Início:</label>
          <input
            type="date"
            id="filterStartDate"
            value={filterStartDate}
            onChange={(e) => setFilterStartDate(e.target.value)}
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 dark:border-gray-600 rounded-md p-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
          <label htmlFor="filterEndDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Data Fim:</label>
          <input
            type="date"
            id="filterEndDate"
            value={filterEndDate}
            onChange={(e) => setFilterEndDate(e.target.value)}
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 dark:border-gray-600 rounded-md p-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
          <label htmlFor="filterEmployee" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Funcionário (ID):</label>
          {/* Replace with a Select dropdown populated with employees */}
          <input
            type="text" // Temporary, replace with Select
            id="filterEmployee"
            placeholder="ID do Funcionário"
            value={filterEmployeeId}
            onChange={(e) => setFilterEmployeeId(e.target.value)}
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 dark:border-gray-600 rounded-md p-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
      </div>

      {error && <p className="text-center text-red-500 my-4">Erro: {error}</p>}

      <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded shadow">
        <table className="min-w-full table-auto">
          <thead className="bg-gray-200 dark:bg-gray-700">
            <tr>
              <th className="px-4 py-2 text-left text-gray-600 dark:text-gray-300">Funcionário</th>
              <th className="px-4 py-2 text-left text-gray-600 dark:text-gray-300">Data</th>
              <th className="px-4 py-2 text-left text-gray-600 dark:text-gray-300">Entrada</th>
              <th className="px-4 py-2 text-left text-gray-600 dark:text-gray-300">Início Almoço</th>
              <th className="px-4 py-2 text-left text-gray-600 dark:text-gray-300">Fim Almoço</th>
              <th className="px-4 py-2 text-left text-gray-600 dark:text-gray-300">Saída</th>
            </tr>
          </thead>
          <tbody className="text-gray-700 dark:text-gray-200">
            {groupedRecords.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-4">Nenhum registro encontrado para os filtros selecionados.</td>
              </tr>
            ) : (
              groupedRecords.map((record, index) => (
                <tr key={`${record.employee_id}-${record.date}-${index}`} className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700">
                  <td className="px-4 py-2">{record.employee_name}</td>
                  <td className="px-4 py-2">{record.date}</td>
                  <td className="px-4 py-2">{formatTime(record.arrival)}</td>
                  <td className="px-4 py-2">{formatTime(record.lunch_start)}</td>
                  <td className="px-4 py-2">{formatTime(record.lunch_end)}</td>
                  <td className="px-4 py-2">{formatTime(record.departure)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TimeRecordList;

