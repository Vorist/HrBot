// frontend/src/components/tabs/TrainingTab.jsx
import React, { useState } from 'react';
import axios from 'axios';
import './TrainingTab.css';

const trainingOptions = [
  { label: "✅ Навчити на good_dialogs", endpoint: "/api/training/good" },
  { label: "⚠️ Навчити на bad_dialogs", endpoint: "/api/training/bad" },
  { label: "💬 Навчити з урахуванням фідбеку", endpoint: "/api/training/feedback" },
  { label: "📥 Навчити на real_dialogs", endpoint: "/api/training/real" },
  { label: "🧠 Повне навчання",         endpoint: "/api/training/all" }
];

export default function TrainingTab() {
  const [status, setStatus] = useState('');
  const [log, setLog] = useState('');

  const handleTrain = async (endpoint) => {
    setStatus('⏳ Навчання запущено...');
    setLog('');
    try {
      const response = await axios.post(endpoint);
      // response.data — это строка stdout
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
    }
  };

  return (
    <div className="training-tab">
      <h2 className="training-title">🧠 Навчання бота</h2>

      <div className="training-buttons">
        {trainingOptions.map(({ label, endpoint }) => (
          <div key={endpoint} className="training-card">
            <span className="training-label">{label}</span>
            <button
              className="training-run-button"
              onClick={() => handleTrain(endpoint)}
            >
              Запустити
            </button>
          </div>
        ))}
      </div>

      {status && (
        <div className="training-status">
          <strong>Статус:</strong> {status}
        </div>
      )}

      {log && (
        <pre className="training-log">{log}</pre>
      )}
    </div>
  );
}
