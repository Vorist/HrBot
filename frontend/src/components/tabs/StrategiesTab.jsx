// frontend/src/components/tabs/StrategiesTab.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './StrategiesTab.css';

export default function StrategiesTab() {
  const [strategies, setStrategies] = useState([]);
  const [editingIndex, setEditingIndex] = useState(null);
  const [editedText, setEditedText] = useState('');

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      const response = await axios.get('/api/strategies');
      setStrategies(response.data);
    } catch (error) {
      console.error("Помилка завантаження стратегій", error);
    }
  };

  const startEditing = (index, currentText) => {
    setEditingIndex(index);
    setEditedText(currentText);
  };

  const cancelEditing = () => {
    setEditingIndex(null);
    setEditedText('');
  };

  const saveImproved = async (index) => {
    try {
      await axios.post('/api/strategies/update', {
        index,
        improved: editedText,
      });
      const updated = [...strategies];
      updated[index].improved = editedText;
      setStrategies(updated);
      cancelEditing();
    } catch (error) {
      console.error("Помилка збереження відповіді", error);
    }
  };

  return (
    <div className="strategies-tab">
      <h2 className="strategies-title">📈 Стратегії покращення відповідей
      </h2>

      {strategies.map((s, i) => (
        <div key={i} className="strategy-card">
          <div className="section">
            <strong>📌 Контекст:</strong>
            <p>{s.context}</p>
          </div>

          <div className="section original">
            <strong>🧠 Було:</strong>
            <p>{s.original}</p>
          </div>

          <div className="section improved">
            <strong>✅ Стало:</strong>
            {editingIndex === i ? (
              <textarea
                value={editedText}
                onChange={(e) => setEditedText(e.target.value)}
              />
            ) : (
              <p>{s.improved}</p>
            )}
          </div>

          <div className="section">
            {editingIndex === i ? (
              <>
                <button className="save" onClick={() => saveImproved(i)}>📂 Зберегти</button>
                <button className="cancel" onClick={cancelEditing}>❌ Скасувати</button>
              </>
            ) : (
              <button className="edit-button" onClick={() => startEditing(i, s.improved)}>
                ✏️ Редагувати
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
