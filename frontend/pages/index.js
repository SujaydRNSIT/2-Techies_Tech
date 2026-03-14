import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Shield, 
  Upload, 
  Loader2, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  FileText,
  MessageSquare,
  ChevronDown,
  ChevronUp,
  Activity
} from 'lucide-react';

import SponsorBadges from '../components/SponsorBadges';
import FraudScoreGauge from '../components/FraudScoreGauge';
import InvestigationReport from '../components/InvestigationReport';
import RecentClaims from '../components/RecentClaims';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Dashboard() {
  const [formData, setFormData] = useState({
    order_id: '',
    merchant_name: '',
    payment_id: '',
    refund_amount: '',
    claim_reason: ''
  });
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showReport, setShowReport] = useState(false);
  const [showResponse, setShowResponse] = useState(false);
  const [refreshClaims, setRefreshClaims] = useState(0);
  const [sponsorStatus, setSponsorStatus] = useState(null);

  useEffect(() => {
    // Fetch sponsor integration status
    axios.get(`${API_URL}/sponsor-status`)
      .then(res => setSponsorStatus(res.data.integrations))
      .catch(console.error);
  }, []);

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const submitData = new FormData();
      Object.keys(formData).forEach(key => {
        submitData.append(key, formData[key]);
      });
      if (image) {
        submitData.append('image', image);
      }

      const response = await axios.post(`${API_URL}/submit-claim`, submitData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setResult(response.data);
      setRefreshClaims(prev => prev + 1);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getDecisionBadge = (decision) => {
    switch (decision) {
      case 'approved':
        return (
          <div className="flex items-center gap-2 badge-success px-4 py-2 text-base">
            <CheckCircle className="w-5 h-5" />
            REFUND APPROVED
          </div>
        );
      case 'rejected':
        return (
          <div className="flex items-center gap-2 badge-danger px-4 py-2 text-base">
            <XCircle className="w-5 h-5" />
            REFUND REJECTED
          </div>
        );
      default:
        return (
          <div className="flex items-center gap-2 badge-warning px-4 py-2 text-base">
            <AlertCircle className="w-5 h-5" />
            MANUAL REVIEW REQUIRED
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-primary-600 p-2 rounded-lg">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">RefundShield AI</h1>
                <p className="text-sm text-gray-500">Autonomous Refund Fraud Investigator</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-success-500" />
              <span className="text-sm text-gray-600">System Online</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Sponsor Badges */}
        <section className="mb-8">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Powered By
          </h2>
          <SponsorBadges />
        </section>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Form */}
          <div>
            <div className="card">
              <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                <FileText className="w-6 h-6 text-primary-600" />
                Submit Refund Claim
              </h2>

              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Order ID *
                    </label>
                    <input
                      type="text"
                      name="order_id"
                      value={formData.order_id}
                      onChange={handleInputChange}
                      className="input-field"
                      placeholder="e.g., ORDER123"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Payment ID *
                    </label>
                    <input
                      type="text"
                      name="payment_id"
                      value={formData.payment_id}
                      onChange={handleInputChange}
                      className="input-field"
                      placeholder="Razorpay Payment ID"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Merchant Name *
                    </label>
                    <input
                      type="text"
                      name="merchant_name"
                      value={formData.merchant_name}
                      onChange={handleInputChange}
                      className="input-field"
                      placeholder="e.g., Amazon"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Refund Amount (₹) *
                    </label>
                    <input
                      type="number"
                      name="refund_amount"
                      value={formData.refund_amount}
                      onChange={handleInputChange}
                      className="input-field"
                      placeholder="0.00"
                      min="1"
                      step="0.01"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Claim Reason *
                  </label>
                  <textarea
                    name="claim_reason"
                    value={formData.claim_reason}
                    onChange={handleInputChange}
                    className="input-field"
                    rows="3"
                    placeholder="Describe the reason for refund..."
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Evidence Image
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors">
                    {imagePreview ? (
                      <div className="relative">
                        <img
                          src={imagePreview}
                          alt="Preview"
                          className="max-h-48 mx-auto rounded-lg"
                        />
                        <button
                          type="button"
                          onClick={() => { setImage(null); setImagePreview(null); }}
                          className="absolute top-2 right-2 bg-danger-500 text-white p-1 rounded-full hover:bg-danger-600"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <label className="cursor-pointer block">
                        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <span className="text-gray-600">Click to upload evidence image</span>
                        <span className="text-gray-400 text-sm block mt-1">
                          PNG, JPG up to 10MB
                        </span>
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handleImageChange}
                          className="hidden"
                        />
                      </label>
                    )}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Investigating with AI Agents...
                    </>
                  ) : (
                    <>
                      <Shield className="w-5 h-5" />
                      Submit for Investigation
                    </>
                  )}
                </button>
              </form>

              {error && (
                <div className="mt-4 p-4 bg-danger-50 border border-danger-200 rounded-lg flex items-center gap-2 text-danger-800">
                  <AlertCircle className="w-5 h-5" />
                  {error}
                </div>
              )}
            </div>

            {/* Recent Claims */}
            <div className="mt-6">
              <RecentClaims 
                refreshTrigger={refreshClaims}
                onSelectClaim={(claimId) => console.log('Selected:', claimId)}
              />
            </div>
          </div>

          {/* Right Column - Results */}
          <div>
            {result ? (
              <div className="space-y-6 animate-slide-in">
                {/* Result Card */}
                <div className="card border-2 border-primary-200">
                  <h2 className="text-xl font-bold text-gray-900 mb-6 text-center">
                    Investigation Result
                  </h2>

                  <div className="flex justify-center mb-6">
                    <FraudScoreGauge score={result.fraud_score} />
                  </div>

                  <div className="text-center mb-6">
                    {getDecisionBadge(result.decision)}
                  </div>

                  {result.refund_id && (
                    <div className="bg-success-50 border border-success-200 rounded-lg p-4 mb-4">
                      <p className="text-sm text-success-800">
                        <span className="font-semibold">Refund ID:</span> {result.refund_id}
                      </p>
                      <p className="text-sm text-success-800">
                        <span className="font-semibold">Status:</span> {result.refund_status}
                      </p>
                    </div>
                  )}

                  {result.decision === 'rejected' && (
                    <div className="bg-danger-50 border border-danger-200 rounded-lg p-4 mb-4">
                      <p className="text-sm text-danger-800">
                        <span className="font-semibold">Reason:</span> {result.decision_reason}
                      </p>
                    </div>
                  )}
                </div>

                {/* Investigation Report */}
                <div className="card">
                  <button
                    onClick={() => setShowReport(!showReport)}
                    className="w-full flex items-center justify-between text-left"
                  >
                    <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                      <FileText className="w-5 h-5 text-primary-600" />
                      Investigation Report
                    </h3>
                    {showReport ? (
                      <ChevronUp className="w-5 h-5 text-gray-500" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-500" />
                    )}
                  </button>
                  
                  {showReport && (
                    <div className="mt-4">
                      <InvestigationReport report={result.investigation_report} />
                    </div>
                  )}
                </div>

                {/* Customer Response */}
                <div className="card">
                  <button
                    onClick={() => setShowResponse(!showResponse)}
                    className="w-full flex items-center justify-between text-left"
                  >
                    <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                      <MessageSquare className="w-5 h-5 text-primary-600" />
                      Automated Customer Response
                    </h3>
                    {showResponse ? (
                      <ChevronUp className="w-5 h-5 text-gray-500" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-500" />
                    )}
                  </button>
                  
                  {showResponse && (
                    <div className="mt-4">
                      <div className="bg-gray-50 rounded-lg p-4 whitespace-pre-wrap text-sm text-gray-700">
                        {result.customer_response}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="card h-96 flex flex-col items-center justify-center text-center">
                <Shield className="w-16 h-16 text-gray-300 mb-4" />
                <h3 className="text-xl font-semibold text-gray-500 mb-2">
                  Ready to Investigate
                </h3>
                <p className="text-gray-400 max-w-sm">
                  Submit a refund claim to see AI agents analyze evidence, check security, verify merchants, and detect fraud patterns.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* API Status Footer */}
        {sponsorStatus && (
          <footer className="mt-12 card bg-gray-50">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
              Integration Status
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(sponsorStatus).map(([key, value]) => (
                <div
                  key={key}
                  className={`flex items-center gap-2 p-2 rounded-lg ${
                    value.configured ? 'bg-success-50' : 'bg-gray-100'
                  }`}
                >
                  <div
                    className={`w-2 h-2 rounded-full ${
                      value.configured ? 'bg-success-500' : 'bg-gray-400'
                    }`}
                  />
                  <span className={`text-sm ${value.configured ? 'text-success-800' : 'text-gray-600'}`}>
                    {value.name}
                  </span>
                </div>
              ))}
            </div>
          </footer>
        )}
      </main>
    </div>
  );
}
