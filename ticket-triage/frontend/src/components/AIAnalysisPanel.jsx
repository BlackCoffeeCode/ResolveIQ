import './AIAnalysisPanel.css';

function AIAnalysisPanel({ ticket, analysis, loading, error }) {
  return (
    <section className="result-panel ai-analysis-panel" aria-live="polite">
      <div className="result-header">
        <div>
          <h2>AI Analysis</h2>
          {ticket ? <p className="meta">Ticket #{ticket.id}</p> : null}
        </div>
      </div>

      {!ticket ? (
        <p className="ai-placeholder">Submit a ticket to see its separate AI analysis.</p>
      ) : null}

      {loading ? (
        <p className="ai-status">
          <span className="ai-spinner" aria-hidden="true" />
          AI is analyzing this ticket...
        </p>
      ) : null}

      {error ? (
        <p className="ai-error" role="alert">
          {error}
        </p>
      ) : null}

      {analysis ? (
        <div className="ai-analysis-content">
          <div className="badge-row ai-badges">
            <span className="badge badge-ai-category">{analysis.category}</span>
            <span className={`badge ai-priority ai-priority-${analysis.priority.toLowerCase()}`}>
              {analysis.priority}
            </span>
          </div>
          <div className="block">
            <h3>Summary</h3>
            <p>{analysis.summary}</p>
          </div>
          <div className="block">
            <h3>Likely Cause</h3>
            <p>{analysis.likely_cause}</p>
          </div>
          <div className="block">
            <h3>Suggested Resolution</h3>
            <ol>
              {analysis.suggested_resolution.map((step, index) => (
                <li key={`${step}-${index}`}>{step}</li>
              ))}
            </ol>
          </div>
          <div className="block">
            <h3>AI Explanation</h3>
            <p>{analysis.explanation}</p>
          </div>
        </div>
      ) : null}
    </section>
  );
}

export default AIAnalysisPanel;