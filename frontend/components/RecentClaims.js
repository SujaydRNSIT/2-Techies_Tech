import { useState, useEffect } from 'react';
import axios from 'axios';
import { RefreshCw, Eye, ArrowUpDown } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function RecentClaims({ onSelectClaim, refreshTrigger }) {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sortOrder, setSortOrder] = useState('desc');

  const fetchClaims = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/claims?limit=10`);
      setClaims(response.data.claims || []);
    } catch (error) {
      console.error('Error fetching claims:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClaims();
  }, [refreshTrigger]);

  const getDecisionBadge = (decision) => {
    switch (decision) {
      case 'approved':
        return <span className="badge badge-success">Approved</span>;
      case 'rejected':
        return <span className="badge badge-danger">Rejected</span>;
      default:
        return <span className="badge badge-warning">Review</span>;
    }
  };

  const getScoreColor = (score) => {
    if (score <= 30) return 'text-success-600';
    if (score <= 70) return 'text-warning-600';
    return 'text-danger-600';
  };

  const sortedClaims = [...claims].sort((a, b) => {
    const dateA = new Date(a.created_at);
    const dateB = new Date(b.created_at);
    return sortOrder === 'desc' ? dateB - dateA : dateA - dateB;
  });

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">Recent Claims</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
            title="Sort"
          >
            <ArrowUpDown className="w-4 h-4" />
          </button>
          <button
            onClick={fetchClaims}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {claims.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No claims submitted yet</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-3 font-medium text-gray-600">Claim ID</th>
                <th className="text-left py-2 px-3 font-medium text-gray-600">Merchant</th>
                <th className="text-right py-2 px-3 font-medium text-gray-600">Amount</th>
                <th className="text-center py-2 px-3 font-medium text-gray-600">Score</th>
                <th className="text-center py-2 px-3 font-medium text-gray-600">Decision</th>
                <th className="text-center py-2 px-3 font-medium text-gray-600">Action</th>
              </tr>
            </thead>
            <tbody>
              {sortedClaims.map((claim) => (
                <tr key={claim.claim_id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-3 font-mono text-xs">{claim.claim_id}</td>
                  <td className="py-3 px-3">{claim.merchant_name}</td>
                  <td className="py-3 px-3 text-right">₹{claim.refund_amount?.toLocaleString()}</td>
                  <td className="py-3 px-3 text-center">
                    <span className={`font-bold ${getScoreColor(claim.fraud_score)}`}>
                      {claim.fraud_score}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-center">
                    {getDecisionBadge(claim.decision)}
                  </td>
                  <td className="py-3 px-3 text-center">
                    <button
                      onClick={() => onSelectClaim(claim.claim_id)}
                      className="p-1 text-primary-600 hover:bg-primary-50 rounded"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
