// frontend/src/components/tabs/StrategiesTab.jsx
import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import './StrategiesTab.css';

export default function StrategiesTab() {
  const [strategies, setStrategies] = useState([]);
  const [editingIndex, setEditingIndex] = useState(null);
  const [editedText, setEditedText] = useState('');
  const [loading, setLoading] = useState(false);
  const [globalError, setGlobalError] = useState('');
  const [statuses, setStatuses] = useState({});
  const textareaRef = useRef(null);

  useEffect(() => {
    fetchStrategies();
  }, []);

  useEffect(() => {
    // Автофокус на textarea при начале редактирования
    if (editingIndex !== null && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.setSelectionRange(0, textareaRef.current.value.length);
    }
  }, [editingIndex]);

  const fetchStrategies = async () => {
    setLoading(true);
    setGlobalError('');
    try {
      const { data } = await axios.get('strategies');
      if (!Array.isArray(data)) throw new Error('Невірний формат відповіді');
      setStrategies(data);
    } catch (err) {
      setGlobalError('Не вдалося завантажити стратегії');
      setStrategies([]);
    } finally {
      setLoading(false);
    }
  };

  const startEditing = (index) => {
    setEditingIndex(index);
    setEditedText(textValue(strategies[index]?.improved));
    setStatuses((s) => ({ ...s, [index]: '' }));
  };

  const cancelEditing = () => {
    setEditingIndex(null);
    setEditedText('');
  };

  const saveImproved = async (index) => {
    if (!editedText.trim()) {
      setStatuses((s) => ({ ...s, [index]: '❗ Поле не може бути порожнім' }));
      return;
    }
    setStatuses((s) => ({ ...s, [index]: '⏳ Збереження...' }));
    try {
      await axios.post('strategies/update', {
        index,
        improved: editedText.trim(),
      });
      const updated = [...strategies];
      updated[index] = { ...updated[index], improved: editedText.trim() };
      setStrategies(updated);
      setStatuses((s) => ({ ...s, [index]: '✅ Збережено!' }));
      cancelEditing();
      // Мягкая подсветка карточки как успешно сохранённой
      setTimeout(() => setStatuses((s) => ({ ...s, [index]: '' })), 2000);
    } catch {
      setStatuses((s) => ({ ...s, [index]: '❌ Помилка збереження' }));
    }
  };

  // Универсальный безопасный геттер
  function textValue(field) {
    if (typeof field === 'string') return field;
    if (field && typeof field === 'object' && 'text' in field) return field.text;
    return '';
  }

  if (loading) return <p className="status">⏳ Завантаження стратегій...</p>;
  if (globalError) return <p className="status error">{globalError}</p>;
  if (!strategies.length) return <p className="status">📭 Стратегії відсутні.</p>;

  return (
    <div className="strategies-tab">
      <h2 className="strategies-title">📈 Стратегії покращення відповідей</h2>

      <div className="strategies-list">
        {strategies.map((s, i) => (
          <div
            key={i}
            className={
              "strategy-card" +
              (statuses[i]?.includes('Збережено') ? ' saved' : '') +
              (editingIndex === i ? ' editing' : '')
            }
            tabIndex={0}
          >
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
                  ref={textareaRef}
                  value={editedText}
                  aria-label="Поле редагування покращеної відповіді"
                  onChange={(e) => setEditedText(e.target.value)}
                  rows={4}
                  maxLength={1200}
                />
              ) : (
                <p>
                  {textValue(s.improved) || (
                    <em className="muted">Покращень ще немає</em>
                  )}
                </p>
              )}
            </div>
            <div className="section actions">
              {editingIndex === i ? (
                <>
                  <button
                    className="save"
                    aria-label="Зберегти зміни"
                    onClick={() => saveImproved(i)}
                  >
                    💾 Зберегти
                  </button>
                  <button
                    className="cancel"
                    aria-label="Скасувати редагування"
                    onClick={cancelEditing}
                  >
                    ❌ Скасувати
                  </button>
                </>
              ) : (
                <button
                  className="edit-button"
                  aria-label="Редагувати"
                  onClick={() => startEditing(i)}
                >
                  ✏️ Редагувати
                </button>
              )}
            </div>
            {statuses[i] && (
              <div
                className={
                  'status-message' +
                  (statuses[i].includes('Збережено') ? ' success' : '') +
                  (statuses[i].includes('Помилка') ? ' error' : '')
                }
              >
                {statuses[i]}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
