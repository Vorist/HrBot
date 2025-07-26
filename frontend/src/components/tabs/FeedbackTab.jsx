// frontend/src/components/tabs/FeedbackTab.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './FeedbackTab.css';

export default function FeedbackTab() {
  const [dialogs, setDialogs] = useState([]);
  const [comments, setComments] = useState({});

  useEffect(() => {
    fetchDialogsNeedingFeedback();
  }, []);

  const fetchDialogsNeedingFeedback = async () => {
    try {
      const response = await axios.get('/api/feedback');
      const filtered = response.data.filter((d) => !d.comment || d.comment.trim() === '');
      setDialogs(filtered);
    } catch (error) {
      console.error('Помилка завантаження фідбек-діалогів:', error);
    }
  };

  const handleCommentChange = (index, value) => {
    setComments({ ...comments, [index]: value });
  };

  const submitFeedback = async (index) => {
    try {
      await axios.post('/api/feedback', {
        index,
        comment: comments[index] || ''
      });

      setDialogs(dialogs.filter((_, i) => i !== index));
    } catch (error) {
      console.error('Помилка при збереженні фідбеку:', error);
    }
  };

  return (
    <div className="feedback-tab">
      <h2>💬 Фідбек до діалогів</h2>
      {dialogs.length === 0 ? (
        <p className="empty-message">✅ Немає діалогів, які потребують фідбеку</p>
      ) : (
        <div className="dialog-list">
          {dialogs.map((item, index) => (
            <div key={index} className="dialog-card">
              <div className="dialog-content">
                {item.dialog.map((line, i) => (
                  <div key={i} className="dialog-line">
                    <strong>{line.role === 'user' ? '👤' : '🤖'}</strong> {line.text}
                  </div>
                ))}
              </div>

              <textarea
                placeholder="📝 Напишіть загальний фідбек по діалогу..."
                value={comments[index] || ''}
                onChange={(e) => handleCommentChange(index, e.target.value)}
              />

              <button className="submit-btn" onClick={() => submitFeedback(index)}>
                💾 Зберегти фідбек
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
