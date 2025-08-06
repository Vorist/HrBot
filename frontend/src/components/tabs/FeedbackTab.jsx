// frontend/src/components/tabs/FeedbackTab.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './FeedbackTab.css';

export default function FeedbackTab() {
  const [items, setItems] = useState([]);          // Все записи фідбеку
  const [comments, setComments] = useState({});    // Чернетки коментарів
  const [statusMsgs, setStatusMsgs] = useState({}); // Статуси по кожному індексу

  useEffect(() => {
    fetchFeedbackItems();
  }, []);

  async function fetchFeedbackItems() {
    try {
      const res = await axios.get('/api/feedback');
      // Беремо тільки ті, що в статусі "waiting"
      const waiting = Array.isArray(res.data)
        ? res.data.filter((fb) => fb.status === 'waiting')
        : [];
      setItems(waiting);
    } catch (err) {
      console.error('❌ Помилка завантаження фідбеків:', err);
    }
  }

  const handleCommentChange = (idx, value) => {
    setComments((c) => ({ ...c, [idx]: value }));
  };

  const submitFeedback = async (idx) => {
    const comment = (comments[idx] || '').trim();
    if (!comment) {
      setStatusMsgs((s) => ({ ...s, [idx]: '❗ Коментар не може бути порожнім' }));
      return;
    }
    try {
      // Оновлюємо існуючий фідбек
      await axios.post('/api/feedback/update', {
        index: idx,
        comment,
        status: 'applied'
      });
      setStatusMsgs((s) => ({ ...s, [idx]: '✅ Збережено' }));
      // Прибрати зі списку
      setItems((its) => its.filter((_, i) => i !== idx));
    } catch (err) {
      console.error('❌ Помилка при збереженні фідбеку:', err);
      setStatusMsgs((s) => ({ ...s, [idx]: '⚠️ Помилка збереження' }));
    }
  };

  return (
    <div className="feedback-tab">
      <h2>💬 Фідбек до діалогів</h2>

      {items.length === 0 ? (
        <p className="empty-message">✅ Немає діалогів, які потребують фідбеку</p>
      ) : (
        <div className="dialog-list">
          {items.map((item, idx) => (
            <div key={idx} className="dialog-card">
              <div className="dialog-content">
                {Array.isArray(item.dialog) ? (
                  item.dialog.map((line, i) => (
                    <div key={i} className="dialog-line">
                      <strong>{line.role === 'user' ? '👤' : '🤖'}</strong> {line.text}
                    </div>
                  ))
                ) : (
                  <div>⚠️ Некоректний формат діалогу</div>
                )}
              </div>

              <textarea
                placeholder="📝 Напишіть коментар по діалогу..."
                value={comments[idx] || ''}
                onChange={(e) => handleCommentChange(idx, e.target.value)}
              />

              <button
                className="submit-btn"
                onClick={() => submitFeedback(idx)}
              >
                💾 Зберегти фідбек
              </button>

              {statusMsgs[idx] && (
                <div className="status-message">{statusMsgs[idx]}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
