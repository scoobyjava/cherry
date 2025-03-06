import React from "react";
import { useFetchData } from "../utils/useFetchData";

interface ApiResponse {
  id: string;
  name: string;
  status: string;
}

export const DataDisplay: React.FC = () => {
  const { data, loading, error, retry } = useFetchData<ApiResponse[]>(
    "http://localhost:8000/api/items"
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center p-6">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4 m-4">
        <h3 className="text-lg font-medium text-red-800">
          Error fetching data
        </h3>
        <p className="text-red-700 mt-2">{error.message}</p>
        <button
          onClick={retry}
          className="mt-3 bg-red-100 hover:bg-red-200 text-red-800 font-semibold py-2 px-4 rounded"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Items</h2>
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {data?.map((item) => (
          <div
            key={item.id}
            className="border rounded-lg shadow-sm p-4 bg-white"
          >
            <h3 className="font-medium">{item.name}</h3>
            <p className="text-sm text-gray-500">{item.status}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
