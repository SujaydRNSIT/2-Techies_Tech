import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Image, 
  Shield, 
  Building2, 
  Brain,
  FileText
} from 'lucide-react';

export default function InvestigationReport({ report }) {
  if (!report) return null;

  const findings = report.investigation_findings || {};
  const assessment = report.fraud_assessment || {};

  const getStatusIcon = (status, value) => {
    if (status === 'safe' || status === 'verified' || value === true) {
      return <CheckCircle className="w-5 h-5 text-success-500" />;
    }
    if (status === false || value === false) {
      return <XCircle className="w-5 h-5 text-danger-500" />;
    }
    return <AlertTriangle className="w-5 h-5 text-warning-500" />;
  };

  return (
    <div className="space-y-6">
      {/* Executive Summary */}
      <div className="card bg-gradient-to-r from-primary-50 to-blue-50 border-primary-200">
        <h3 className="text-lg font-bold text-primary-900 mb-3 flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Executive Summary
        </h3>
        <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">
          {report.executive_summary}
        </pre>
      </div>

      {/* Investigation Findings Grid */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Image Analysis */}
        <div className="card">
          <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
            <Image className="w-5 h-5 text-primary-600" />
            Image Analysis
          </h4>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center justify-between">
              <span>Damage Detected</span>
              {getStatusIcon('damage', findings.image_analysis?.damage_detected)}
            </li>
            <li className="flex items-center justify-between">
              <span>AI Generated</span>
              <span className={findings.image_analysis?.ai_generated_probability > 50 ? 'text-danger-600 font-medium' : 'text-success-600'}>
                {findings.image_analysis?.ai_generated_probability || 0}%
              </span>
            </li>
            <li className="flex items-center justify-between">
              <span>Manipulation</span>
              {getStatusIcon('manipulation', !findings.image_analysis?.manipulation_detected)}
            </li>
          </ul>
        </div>

        {/* Security Scan */}
        <div className="card">
          <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
            <Shield className="w-5 h-5 text-green-600" />
            Security Scan
          </h4>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center justify-between">
              <span>Overall Safe</span>
              {getStatusIcon('safe', findings.security_scan?.safe)}
            </li>
            <li className="flex items-center justify-between">
              <span>Security Score</span>
              <span className={findings.security_scan?.security_score > 20 ? 'text-danger-600 font-medium' : 'text-success-600'}>
                {findings.security_scan?.security_score || 0}/100
              </span>
            </li>
            <li className="flex items-center justify-between">
              <span>URL Scans</span>
              <span className="text-gray-600">{findings.security_scan?.url_scans || 0}</span>
            </li>
          </ul>
        </div>

        {/* Merchant Verification */}
        <div className="card">
          <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-blue-600" />
            Merchant Verification
          </h4>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center justify-between">
              <span>Verified</span>
              {getStatusIcon('verified', findings.merchant_verification?.verified)}
            </li>
            <li className="flex items-center justify-between">
              <span>Company</span>
              <span className="text-gray-600 truncate max-w-[150px]">
                {findings.merchant_verification?.company_name || 'Unknown'}
              </span>
            </li>
            <li className="flex items-center justify-between">
              <span>Funding</span>
              <span className="text-gray-600 capitalize">
                {findings.merchant_verification?.funding_stage || 'Unknown'}
              </span>
            </li>
          </ul>
        </div>

        {/* Fraud Pattern Check */}
        <div className="card">
          <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-600" />
            Fraud Pattern Check
          </h4>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center justify-between">
              <span>Similar Cases</span>
              <span className="text-gray-600">
                {findings.fraud_pattern_check?.similar_cases_found || 0} found
              </span>
            </li>
            <li className="flex items-center justify-between">
              <span>Pattern Match</span>
              {findings.fraud_pattern_check?.pattern_match ? (
                <XCircle className="w-5 h-5 text-danger-500" />
              ) : (
                <CheckCircle className="w-5 h-5 text-success-500" />
              )}
            </li>
            <li className="flex items-center justify-between">
              <span>Avg. Historical Score</span>
              <span className="text-gray-600">
                {findings.fraud_pattern_check?.avg_historical_fraud_score || 0}/100
              </span>
            </li>
          </ul>
        </div>
      </div>

      {/* Risk Factors */}
      {assessment.risk_factors?.length > 0 && (
        <div className="card bg-danger-50 border-danger-200">
          <h4 className="font-bold text-danger-900 mb-2">Risk Factors Detected</h4>
          <ul className="list-disc list-inside text-sm text-danger-800 space-y-1">
            {assessment.risk_factors.map((factor, idx) => (
              <li key={idx}>{factor}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Sponsor Integrations */}
      <div className="card bg-gray-50">
        <h4 className="font-bold text-gray-900 mb-3">AI Systems Used</h4>
        <div className="flex flex-wrap gap-2">
          {report.sponsor_integrations_used?.map((integration, idx) => (
            <span key={idx} className="badge badge-info text-xs">
              {integration}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
