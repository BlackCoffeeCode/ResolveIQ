import './ResultPanel.css';

const CATEGORY_CLASSES = {
  Billing: 'badge-billing',
  Technical: 'badge-technical',
  Account: 'badge-account',
  'Feature Request': 'badge-feature',
  Security: 'badge-security',
  Other: 'badge-other',
};

const PRIORITY_CLASSES = {
  P0: 'priority-p0',
  P1: 'priority-p1',
  P2: 'priority-p2',
  P3: 'priority-p3',
};

function ResultPanel({ result }) {
  if (!result) {
    return (
      <section className="result-panel placeholder">
        <p>Submit a ticket to see analysis results</p>
      </section>
    );
  }

  const confidencePercent = Math.round((result.confidence_score || 0) * 100);
  const localDate = result.created_at
    ? new Date(result.created_at).toLocaleString()
    : 'N/A';

  return (
    <section className="result-panel">
      {result.is_security_escalated ? (
        <div className="security-banner">
          SECURITY FLAG: YES - Escalated to P0
        </div>
      ) : null}

      <div className="result-header">
        <div>
          <h2>Standard Triage</h2>
          <p className="meta">Ticket #{result.id} • {localDate}</p>
        </div>
        <div className="badge-row">
          <span className={`badge ${CATEGORY_CLASSES[result.category] || 'badge-other'}`}>
            {result.category === 'Security' ? '⚠️ Security' : result.category}
          </span>
          <span className={`badge ${PRIORITY_CLASSES[result.priority] || 'priority-p2'}`}>
            {result.priority}
          </span>
        </div>
      </div>

      <p className="urgency">
        {result.urgency ? '🔴 URGENT' : '🟢 Normal'}
      </p>
      <p className="security-status">
        Security flag: <strong>{result.is_security_escalated ? 'Yes' : 'No'}</strong>
      </p>

      <div className="confidence-wrap">
        <div className="confidence-meta">
          <span>Confidence</span>
          <strong>{confidencePercent}%</strong>
        </div>
        <div className="confidence-bar">
          <div
            className="confidence-fill"
            style={{ width: `${confidencePercent}%` }}
            role="progressbar"
            aria-valuenow={confidencePercent}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>
      </div>

      <div className="block">
        <h3>Signals</h3>
        <ul>
          {result.signals.map((signal, index) => (
            <li key={`${signal}-${index}`}>{signal}</li>
          ))}
        </ul>
      </div>

      <div className="block">
        <h3>Keywords</h3>
        <div className="keywords-grid">
          {result.keywords.map((keyword) => (
            <span key={keyword} className="keyword-chip">
              {keyword}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

export default ResultPanel;
