// frontend/src/components/tabs/TrainingTab.jsx
import React, { useState } from 'react';
import axios from 'axios';
import './TrainingTab.css';

const trainingOptions = [
  { label: "✅ Навчити на good_dialogs", endpoint: "training/good" },
  { label: "⚠️ Навчити на bad_dialogs", endpoint: "training/bad" },
  { label: "💬 Навчити з урахуванням фідбеку", endpoint: "training/feedback" },
  { label: "📥 Навчити на real_dialogs", endpoint: "training/real" },
  { label: "🧠 Повне навчання", endpoint: "training/all" }
];

export default function TrainingTab() {
  const [status, setStatus] = useState('');
  const [log, setLog] = useState('');
  const [activeIndex, setActiveIndex] = useState(null);

  const handleTrain = async (endpoint, idx) => {
    setStatus('⏳ Навчання запущено...');
    setLog('');
    setActiveIndex(idx);
    try {
      const response = await axios.post(endpoint);
      const output = typeof response.data === 'string'
        ? response.data
        : JSON.stringify(response.data, null, 2);
      setStatus('✅ Навчання завершено успішно');
      setLog(output);
    } catch (error) {
      console.error(error);
      setStatus('❌ Помилка під час навчання');
      let errMsg = '';
      if (error.response) {
        errMsg = typeof error.response.data === 'string'
          ? error.response.data
          : JSON.stringify(error.response.data, null, 2);
      } else {
        errMsg = error.message;
      }
      setLog(errMsg);
    } finally {
      setActiveIndex(null);
    }
  };

  return (
    <div className="training-tab">
      <h2 className="training-title">🧠 Навчання бота</h2>
      <div className="training-buttons">
        {trainingOptions.map(({ label, endpoint }, idx) => (
          <div key={endpoint} className="training-card">
            <span className="training-label">{label}</span>
            <button
              className={`training-run-button${activeIndex === idx ? ' loading' : ''}`}
              onClick={() => handleTrain(endpoint, idx)}
              disabled={!!activeIndex || status.startsWith('⏳')}
            >
              {activeIndex === idx ? 'Запуск...' : 'Запустити'}
            </button>
          </div>
        ))}
      </div>
      {status && (
        <div className={`training-status${status.startsWith('✅') ? ' success' : status.startsWith('❌') ? ' error' : ''}`}>
          <strong>Статус:</strong> {status}
        </div>
      )}
      {log && (
        <pre className="training-log">{log}</pre>
      )}
    </div>
  );
}
