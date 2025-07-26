import React, { useState } from 'react';
import axios from 'axios';
import '@/components/ui/TrainingTab.css'; // стилі до цієї вкладки

const trainingOptions = [
  { label: "✅ Навчити на good_dialogs", endpoint: "/api/train/good" },
  { label: "⚠️ Навчити на bad_dialogs", endpoint: "/api/train/bad" },
  { label: "💬 Навчити з урахуванням фідбеку", endpoint: "/api/train/feedback" },
  { label: "📥 Навчити на real_dialogs", endpoint: "/api/train/real" },
  { label: "🧠 Повне навчання", endpoint: "/api/train/all" }
];

export default function TrainingTab() {
  const [status, setStatus] = useState(null);
  const [log, setLog] = useState('');

  const handleTrain = async (endpoint) => {
    setStatus("⏳ Навчання запущено...");
    setLog('');
    try {
      const response = await axios.post(endpoint);
      setStatus("✅ Навчання завершено успішно");
      setLog(response.data?.log || "✓ Без додаткових повідомлень.");
    } catch (error) {
      setStatus("❌ Помилка під час навчання");
      setLog(error.response?.data?.error || "Невідома помилка.");
    }
  };

  return (
    <div className="training-tab">
      <h2 className="training-title">🧠 Навчання бота</h2>

      <div className="training-buttons">
        {trainingOptions.map(({ label, endpoint }) => (
          <div key={endpoint} className="training-card">
            <span>{label}</span>
            <button className="custom-button" onClick={() => handleTrain(endpoint)}>Запустити</button>
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
