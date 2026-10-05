import { Fragment, useState } from 'react';
import './TicketList.css';

function TicketList({ tickets, loading, onRefresh }) {
  const [expandedTicketId, setExpandedTicketId] = useState(null);

  const toggleExpanded = (ticketId) => {
    setExpandedTicketId((current) => (current === ticketId ? null : ticketId));
  };

  return (
    <section className="ticket-list-panel">
      <div className="list-header">
        <h2>Recent Tickets</h2>
        <button type="button" className="refresh-button" onClick={onRefresh}>
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="skeleton-table" aria-hidden="true">
          <div className="skeleton-row" />
          <div className="skeleton-row" />
          <div className="skeleton-row" />
        </div>
      ) : tickets.length === 0 ? (
        <p className="empty-state">No tickets yet. Submit your first ticket above.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Timestamp</th>
                <th>Category</th>
                <th>Priority</th>
                <th>Urgency</th>
                <th>Confidence</th>
                <th>Security</th>
                <th>AI Analysis</th>
                <th>Message Preview</th>
              </tr>
            </thead>
            <tbody>
              {tickets.map((ticket) => {
                const isExpanded = expandedTicketId === ticket.id;
                const preview =
                  ticket.message.length > 60
                    ? `${ticket.message.slice(0, 60)}...`
                    : ticket.message;
                return (
                  <Fragment key={ticket.id}>
                    <tr
                      className={[
                        ticket.is_security_escalated ? 'security-row' : '',
                        ticket.priority === 'P0' ? 'p0-row' : '',
                        'clickable-row',
                      ]
                        .join(' ')
                        .trim()}
                      onClick={() => toggleExpanded(ticket.id)}
                    >
                      <td>{ticket.id}</td>
                      <td>{new Date(ticket.created_at).toLocaleString()}</td>
                      <td>{ticket.category}</td>
                      <td>{ticket.priority}</td>
                      <td>{ticket.urgency ? '🔴 Urgent' : '🟢 Normal'}</td>
                      <td>{Math.round(ticket.confidence_score * 100)}%</td>
                      <td>{ticket.is_security_escalated ? 'Yes' : 'No'}</td>
                      <td>{ticket.ai_analysis ? 'Available' : 'Not analyzed'}</td>
                      <td>{preview}</td>
                    </tr>
                    {isExpanded ? (
                      <tr className="expanded-row">
                        <td colSpan={9}>
                          <div className="expanded-ticket-content">
                            <p>
                              <strong>Full Message:</strong> {ticket.message}
                            </p>
                            <section className="expanded-ai-analysis">
                              <h3>AI Analysis</h3>
                              {ticket.ai_analysis ? (
                                <>
                                  <p>
                                    <strong>Category:</strong> {ticket.ai_analysis.category}
                                  </p>
                                  <p>
                                    <strong>Priority:</strong> {ticket.ai_analysis.priority}
                                  </p>
                                  <p>
                                    <strong>Summary:</strong> {ticket.ai_analysis.summary}
                                  </p>
                                  <p>
                                    <strong>Likely cause:</strong> {ticket.ai_analysis.likely_cause}
                                  </p>
                                  <strong>Suggested resolution:</strong>
                                  <ol>
                                    {ticket.ai_analysis.suggested_resolution.map((step, index) => (
                                      <li key={`${ticket.id}-${index}`}>{step}</li>
                                    ))}
                                  </ol>
                                  <p>
                                    <strong>Explanation:</strong> {ticket.ai_analysis.explanation}
                                  </p>
                                  <p className="meta">
                                    Analyzed {new Date(ticket.ai_analysis.analyzed_at).toLocaleString()}
                                  </p>
                                </>
                              ) : (
                                <p>No AI analysis has been saved for this ticket.</p>
                              )}
                            </section>
                          </div>
                        </td>
                      </tr>
                    ) : null}
                  </Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default TicketList;
