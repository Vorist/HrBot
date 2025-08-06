// frontend/src/components/tabs/StrategiesTab.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './StrategiesTab.css';

export default function StrategiesTab() {
  const [strategies, setStrategies] = useState([]);
  const [editingIndex, setEditingIndex] = useState(null);
  const [editedText, setEditedText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchStrategies = async () => {
    setLoading(true);
    setError('');
    try {
      const { data } = await axios.get('/api/strategies');
      if (!Array.isArray(data)) {
        throw new Error('Невірний формат відповіді від сервера');
      }
      setStrategies(data);
    } catch (err) {
      console.error('Помилка завантаження стратегій', err);
      setError('Не вдалося завантажити стратегії');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStrategies();
  }, []);

  const startEditing = (index) => {
    setEditingIndex(index);
    setEditedText(
      typeof strategies[index]?.improved === 'string'
        ? strategies[index].improved
        : ''
    );
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
      updated[index] = { ...updated[index], improved: editedText };
      setStrategies(updated);
      cancelEditing();
    } catch (err) {
      console.error('Помилка збереження стратегії', err);
      setError('Не вдалося зберегти зміни');
    }
  };

  if (loading) {
    return <p>Завантаження стратегій...</p>;
  }
  if (error) {
    return <p className="error">{error}</p>;
  }
  if (!strategies.length) {
    return <p>Стратегії відсутні.</p>;
  }

  // Помощная функция для безопасного извлечения текста
  const textValue = (field) => {
    if (typeof field === 'string') return field;
    if (field && typeof field === 'object' && 'text' in field) return field.text;
    return '';
  };

  return (
    <div className="strategies-tab">
      <h2 className="strategies-title">📈 Стратегії покращення відповідей</h2>

      {strategies.map((s, i) => (
        <div key={i} className="strategy-card">
          <div className="section">
            <strong>📌 Контекст:</strong>
            <p>{textValue(s.context)}</p>
          </div>

          <div className="section original">
            <strong>🧠 Було:</strong>
            <p>{textValue(s.original)}</p>
          </div>

          <div className="section improved">
            <strong>✅ Стало:</strong>
            {editingIndex === i ? (
              <textarea
                value={editedText}
                onChange={(e) => setEditedText(e.target.value)}
              />
            ) : (
              <p>
                {textValue(s.improved) || <em>Покращень ще немає</em>}
              </p>
            )}
          </div>

          <div className="section">
            {editingIndex === i ? (
              <>
                <button className="save" onClick={() => saveImproved(i)}>
                  💾 Зберегти
                </button>
                <button className="cancel" onClick={cancelEditing}>
                  ❌ Скасувати
                </button>
              </>
            ) : (
              <button
                className="edit-button"
                onClick={() => startEditing(i)}
              >
                ✏️ Редагувати
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
