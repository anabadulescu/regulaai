import React, { useState } from 'react';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';

interface Scan {
  id: string;
  domain: string;
  date: string;
  gdprScore: number;
  status: 'passing' | 'failed' | 'pending';
}

const Dashboard: React.FC = () => {
  const [scans] = useState<Scan[]>([
    // Sample data - replace with actual API call
    {
      id: '1',
      domain: 'example.com',
      date: '2024-01-15T10:30:00Z',
      gdprScore: 85,
      status: 'passing'
    },
    // Add more sample data...
  ]);

  const exportToPDF = () => {
    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(16);
    doc.text('RegulaAI Scan Report', 14, 15);
    
    // Add date
    doc.setFontSize(10);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 22);
    
    // Add table
    const tableColumn = ['Domain', 'Date', 'GDPR Score', 'Status'];
    const tableRows = scans.map(scan => [
      scan.domain,
      new Date(scan.date).toLocaleString(),
      scan.gdprScore.toString(),
      scan.status
    ]);
    
    (doc as any).autoTable({
      head: [tableColumn],
      body: tableRows,
      startY: 30,
      theme: 'grid',
      styles: {
        fontSize: 8,
        cellPadding: 2,
      },
      headStyles: {
        fillColor: [41, 128, 185],
        textColor: 255,
        fontSize: 10,
        fontStyle: 'bold',
      },
    });
    
    doc.save('regulaai-scan-report.pdf');
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Left Navigation */}
      <nav className="w-64 bg-white shadow-lg">
        <div className="p-4">
          <h1 className="text-xl font-bold text-gray-800">RegulaAI</h1>
        </div>
        <ul className="mt-4">
          <li className="px-4 py-2 text-gray-600 hover:bg-gray-100 cursor-pointer">
            Domains
          </li>
          <li className="px-4 py-2 bg-blue-50 text-blue-600 border-r-4 border-blue-600">
            Scans
          </li>
          <li className="px-4 py-2 text-gray-600 hover:bg-gray-100 cursor-pointer">
            Settings
          </li>
        </ul>
      </nav>

      {/* Main Content */}
      <div className="flex-1 p-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Recent Scans</h2>
          <div className="space-x-4">
            <button
              onClick={exportToPDF}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Export PDF
            </button>
            <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
              Run New Scan
            </button>
          </div>
        </div>

        {/* Scan Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Domain
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  GDPR Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {scans.map((scan) => (
                <tr key={scan.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {scan.domain}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(scan.date).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {scan.gdprScore}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        scan.status === 'passing'
                          ? 'bg-green-100 text-green-800'
                          : scan.status === 'failed'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {scan.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 