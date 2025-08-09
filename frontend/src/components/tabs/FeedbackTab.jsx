// frontend/src/components/tabs/FeedbackTab.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './FeedbackTab.css';

export default function FeedbackTab() {
  const [items, setItems] = useState([]);
  const [comments, setComments] = useState({});
  const [statusMsgs, setStatusMsgs] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFeedbackItems();
  }, []);

  async function fetchFeedbackItems() {
    setLoading(true);
    try {
      const res = await axios.get('feedback');
      // Только те, что в статусе "waiting"
      const waiting = Array.isArray(res.data)
        ? res.data.filter((fb) => fb.status === 'waiting')
        : [];
      setItems(waiting);
    } catch (err) {
      console.error('❌ Помилка завантаження фідбеків:', err);
    }
    setLoading(false);
  }

  const handleCommentChange = (id, value) => {
    setComments((c) => ({ ...c, [id]: value }));
  };

  const submitFeedback = async (id) => {
    const comment = (comments[id] || '').trim();
    if (!comment) {
      setStatusMsgs((s) => ({ ...s, [id]: '❗ Коментар не може бути порожнім' }));
      return;
    }
    try {
      await axios.post('feedback/update', {
        id,
        comment,
        status: 'applied',
      });
      setStatusMsgs((s) => ({ ...s, [id]: '✅ Збережено' }));
      setItems((its) => its.filter((fb) => fb.id !== id));
    } catch (err) {
      console.error('❌ Помилка при збереженні фідбеку:', err);
      setStatusMsgs((s) => ({ ...s, [id]: '⚠️ Помилка збереження' }));
    }
  };

  return (
    <div className="feedback-tab">
      <h2>💬 Фідбек до діалогів</h2>
      {loading ? (
        <p className="status">⏳ Завантаження...</p>
      ) : items.length === 0 ? (
        <p className="empty-message">✅ Немає діалогів, які потребують фідбеку</p>
      ) : (
        <div className="dialog-list">
          {items.map((item) => (
            <div key={item.id} className="dialog-card">
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
                value={comments[item.id] || ''}
                onChange={(e) => handleCommentChange(item.id, e.target.value)}
              />

              <button
                className="submit-btn"
                onClick={() => submitFeedback(item.id)}
                disabled={!!statusMsgs[item.id] && statusMsgs[item.id].startsWith('✅')}
              >
                💾 Зберегти фідбек
              </button>

              {statusMsgs[item.id] && (
                <div
                  className={`status-message${
                    statusMsgs[item.id].startsWith('✅') ? ' success' : statusMsgs[item.id].startsWith('⚠️') ? ' error' : ''
                  }`}
                >
                  {statusMsgs[item.id]}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
