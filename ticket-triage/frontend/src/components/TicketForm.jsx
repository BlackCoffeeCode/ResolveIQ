import { useState } from 'react';
import { analyzeTicket } from '../api/ticketApi';
import './TicketForm.css';

function TicketForm({ onResult, onError, onLoadingChange }) {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [validationError, setValidationError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmed = message.trim();
    if (trimmed.length < 10) {
      setValidationError('Message must be at least 10 characters.');
      return;
    }

    setValidationError('');
    setLoading(true);
    onLoadingChange?.(true);

    try {
      const result = await analyzeTicket(trimmed);
      onResult(result);
      setMessage('');
    } catch (error) {
      onError(error);
    } finally {
      setLoading(false);
      onLoadingChange?.(false);
    }
  };

  return (
    <form className="ticket-form" onSubmit={handleSubmit}>
      <label htmlFor="ticket-message" className="ticket-form-label">
        Support Ticket Message
      </label>
      <textarea
        id="ticket-message"
        className="ticket-form-textarea"
        placeholder="Describe your support issue..."
        minLength={10}
        maxLength={2000}
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        rows={7}
      />
      <div className="ticket-form-footer">
        <span className="char-counter">{message.length}/2000</span>
        <button className="ticket-submit" type="submit" disabled={loading}>
          {loading ? (
            <>
              <span className="spinner" aria-hidden="true" />
              Analyzing...
            </>
          ) : (
            'Analyze Ticket'
          )}
        </button>
      </div>
      {validationError ? <p className="inline-error">{validationError}</p> : null}
    </form>
  );
}

export default TicketForm;
