import { useEffect, useRef, useState } from 'react';
import { analyzeTicketWithAI, getTickets } from './api/ticketApi';
import TicketForm from './components/TicketForm';
import ResultPanel from './components/ResultPanel';
import AIAnalysisPanel from './components/AIAnalysisPanel';
import TicketList from './components/TicketList';
import './App.css';

function App() {
  const [currentResult, setCurrentResult] = useState(null);
  const [aiAnalysis, setAIAnalysis] = useState(null);
  const [aiAnalysisLoading, setAIAnalysisLoading] = useState(false);
  const [aiAnalysisError, setAIAnalysisError] = useState('');
  const aiRequestId = useRef(0);
  const [tickets, setTickets] = useState([]);
  const [listLoading, setListLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [toast, setToast] = useState('');
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    fetchTickets();
  }, []);

  useEffect(() => {
    if (!toast) {
      return undefined;
    }
    const timer = window.setTimeout(() => setToast(''), 3000);
    return () => window.clearTimeout(timer);
  }, [toast]);

  const subtitle =
    'Explainable support ticket triage with category, urgency, and priority rules.';

  const fetchTickets = async () => {
    setListLoading(true);
    try {
      const data = await getTickets(50);
      setTickets(data.tickets || []);
    } catch (error) {
      setToast(error?.response?.data?.detail || 'Failed to fetch tickets');
    } finally {
      setListLoading(false);
    }
  };

  const handleResult = (result) => {
    setCurrentResult(result);
    setAIAnalysis(null);
    setAIAnalysisError('');
    setAIAnalysisLoading(true);
    const requestId = aiRequestId.current + 1;
    aiRequestId.current = requestId;

    void analyzeTicketWithAI(result.id)
      .then((analysis) => {
        if (requestId === aiRequestId.current) {
          setAIAnalysis(analysis);
        }
        void fetchTickets();
      })
      .catch((error) => {
        if (requestId === aiRequestId.current) {
          setAIAnalysisError(
            error?.response?.data?.detail ||
              'AI analysis is currently unavailable. Standard triage is still available.'
          );
        }
      })
      .finally(() => {
        if (requestId === aiRequestId.current) {
          setAIAnalysisLoading(false);
        }
      });

    void fetchTickets();
  };

  const handleError = (error) => {
    setToast(error?.response?.data?.detail || 'Something went wrong while analyzing');
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>ResolveIQ</h1>
          <p>{subtitle}</p>
        </div>
        <button
          type="button"
          className="theme-toggle"
          onClick={() => setTheme((current) => (current === 'light' ? 'dark' : 'light'))}
        >
          {theme === 'light' ? 'Switch to Dark' : 'Switch to Light'}
        </button>
      </header>

      <main className="app-content">
        <TicketForm
          onResult={handleResult}
          onError={handleError}
          onLoadingChange={setAnalyzing}
        />
        <ResultPanel result={currentResult} />
        <AIAnalysisPanel
          ticket={currentResult}
          analysis={aiAnalysis}
          loading={aiAnalysisLoading}
          error={aiAnalysisError}
        />
        <TicketList tickets={tickets} loading={listLoading || analyzing} onRefresh={fetchTickets} />
      </main>

      {toast ? (
        <div className="toast" role="status" aria-live="polite">
          {toast}
        </div>
      ) : null}
    </div>
  );
}

export default App;
