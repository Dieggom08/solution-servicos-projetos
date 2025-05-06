
'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

// Mock function to get geolocation - replace with actual implementation
const getGeoLocation = (): Promise<{ latitude: number; longitude: number } | null> => {
  return new Promise((resolve) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        (error) => {
          console.error("Error getting location: ", error);
          resolve(null); // Resolve with null on error
        }
      );
    } else {
      console.error("Geolocation is not supported by this browser.");
      resolve(null);
    }
  });
};

// Mock function to capture photo - replace with actual implementation
const capturePhoto = async (): Promise<string | null> => {
    // In a real app, this would use navigator.mediaDevices.getUserMedia
    // and potentially a canvas to capture and return a base64 image or blob URL.
    console.warn("Photo capture simulation. Returning placeholder.");
    // Placeholder - replace with actual photo data (e.g., base64 string)
    return "placeholder_photo_data";
};

export default function TrackerPage() {
  const [lastRecordType, setLastRecordType] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [employeeId, setEmployeeId] = useState<string | null>(null); // Store employee ID
  const router = useRouter();

  // TODO: Fetch employee ID and last record type on component mount
  useEffect(() => {
    // Fetch employee data (e.g., from localStorage or context after login)
    // const storedEmployeeId = localStorage.getItem('employeeId');
    // const storedLastRecord = localStorage.getItem('lastRecordType');
    // if (!storedEmployeeId) {
    //   router.push('/login'); // Redirect if not logged in
    // } else {
    //   setEmployeeId(storedEmployeeId);
    //   setLastRecordType(storedLastRecord);
    // }
    // Mock data for now:
    setEmployeeId("1"); // Assume employee ID 1 is logged in
    // Fetch last record for this employee from backend if needed
  }, [router]);

  const handleRecord = async (recordType: 'arrival' | 'lunch_start' | 'lunch_end' | 'departure') => {
    setIsLoading(true);
    setError(null);

    if (!employeeId) {
        setError("ID do funcionário não encontrado. Faça login novamente.");
        setIsLoading(false);
        return;
    }

    try {
      const location = await getGeoLocation();
      let photoData: string | null = null;

      // Capture photo for arrival and departure
      if (recordType === 'arrival' || recordType === 'departure') {
        photoData = await capturePhoto();
        if (!photoData) {
            // Handle photo capture failure (optional)
            console.warn("Falha ao capturar foto, continuando sem ela.");
            // setError("Falha ao capturar foto. Tente novamente.");
            // setIsLoading(false);
            // return;
        }
      }

      const response = await fetch('/api/record', { // Adjust API route if needed
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Add authorization header if needed (e.g., 'Authorization': `Bearer ${token}`)
        },
        body: JSON.stringify({
          employee_id: parseInt(employeeId, 10),
          record_type: recordType,
          latitude: location?.latitude,
          longitude: location?.longitude,
          photo_data: photoData, // Send photo data (e.g., base64)
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Falha ao registrar ponto');
      }

      setLastRecordType(recordType);
      // Optionally store last record type in localStorage
      // localStorage.setItem('lastRecordType', recordType);
      alert(`Registro de ${recordType} realizado com sucesso!`); // Simple feedback

    } catch (err: any) {
      setError(err.message || 'Ocorreu um erro ao registrar o ponto.');
      console.error('Record error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Determine which buttons should be enabled based on the last record
  const canArrive = !lastRecordType || lastRecordType === 'departure';
  const canStartLunch = lastRecordType === 'arrival';
  const canEndLunch = lastRecordType === 'lunch_start';
  const canDepart = lastRecordType === 'arrival' || lastRecordType === 'lunch_end';

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <h1 className="text-3xl font-bold mb-8">Registrar Ponto</h1>
      {error && <p className="text-red-500 mb-4">Erro: {error}</p>}
      <div className="grid grid-cols-2 gap-4 w-full max-w-xs">
        <Button
          onClick={() => handleRecord('arrival')}
          disabled={!canArrive || isLoading}
          className="bg-green-500 hover:bg-green-600 text-white"
        >
          {isLoading && lastRecordType !== 'arrival' ? 'Registrando...' : 'Entrada'}
        </Button>
        <Button
          onClick={() => handleRecord('departure')}
          disabled={!canDepart || isLoading}
          className="bg-red-500 hover:bg-red-600 text-white"
        >
          {isLoading && lastRecordType !== 'departure' ? 'Registrando...' : 'Saída'}
        </Button>
        <Button
          onClick={() => handleRecord('lunch_start')}
          disabled={!canStartLunch || isLoading}
          className="bg-yellow-500 hover:bg-yellow-600 text-white"
        >
          {isLoading && lastRecordType !== 'lunch_start' ? 'Registrando...' : 'Início Intervalo'}
        </Button>
        <Button
          onClick={() => handleRecord('lunch_end')}
          disabled={!canEndLunch || isLoading}
          className="bg-blue-500 hover:bg-blue-600 text-white"
        >
          {isLoading && lastRecordType !== 'lunch_end' ? 'Registrando...' : 'Fim Intervalo'}
        </Button>
      </div>
      {/* Optional: Display last record info */}
      {lastRecordType && <p className="mt-4 text-gray-600">Último registro: {lastRecordType}</p>}
       <Button onClick={() => router.push('/login')} variant="link" className="mt-8">Sair</Button>
    </div>
  );
}

