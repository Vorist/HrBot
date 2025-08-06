// frontend/src/components/tabs/GoodDialogsTab.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './GoodDialogsTab.css';

export default function GoodDialogsTab() {
  const [dialogs, setDialogs] = useState([]);
  const [expandedIndex, setExpandedIndex] = useState(null);
  const [comments, setComments] = useState({});

  useEffect(() => {
    fetchDialogs();
  }, []);

  const fetchDialogs = async () => {
    try {
      const res = await axios.get('/api/good_dialogs');
      const data = res.data;
      // API может вернуть либо массив, либо { items: [...] }
      const items = Array.isArray(data)
        ? data
        : Array.isArray(data.items)
        ? data.items
        : [];
      setDialogs(items);
    } catch (error) {
      console.error('❌ Помилка завантаження хороших діалогів:', error);
      setDialogs([]);
    }
  };

  const handleToggle = (index) => {
    setExpandedIndex(index === expandedIndex ? null : index);
  };

  const handleCommentChange = (index, value) => {
    setComments((prev) => ({ ...prev, [index]: value }));
  };

  const markAsBad = async (index) => {
    try {
      await axios.post('/api/good_dialogs/feedback', {
        index,
        comment: comments[index] || ''
      });
      // удалить из списка
      setDialogs((prev) => prev.filter((_, i) => i !== index));
      setExpandedIndex(null);
    } catch (error) {
      console.error('❌ Помилка при фідбеці:', error);
    }
  };

  const confirmGood = (index) => {
    // Просто сворачиваем карточку, без вызова API
    setExpandedIndex(null);
  };

  return (
    <div className="good-tab">
      <h2>✅ Хороші діалоги</h2>
      {dialogs.length === 0 ? (
        <p>📭 Немає хороших діалогів для відображення.</p>
      ) : (
        <div className="dialog-list">
          {dialogs.map((dialog, index) => (
            <div key={index} className="dialog-card">
              <div
                className="card-header"
                onClick={() => handleToggle(index)}
              >
                👤 {dialog.user || 'Кандидат'}, {dialog.date || 'дата невідома'}
              </div>

              {expandedIndex === index && (
                <div className="card-body">
                  <div className="dialog-content">
                    {Array.isArray(dialog.dialog) ? (
                      dialog.dialog.map((line, i) => (
                        <div key={i} className="dialog-line">
                          <strong>
                            {line.role === 'user' ? '👤' : '🤖'}
                          </strong>{' '}
                          {line.text}
                        </div>
                      ))
                    ) : (
                      <p>⚠️ Некоректний формат діалогу</p>
                    )}
                  </div>

                  <textarea
                    className="manager-comment"
                    placeholder="💬 Коментар менеджера..."
                    value={comments[index] || ''}
                    onChange={(e) =>
                      handleCommentChange(index, e.target.value)
                    }
                  />

                  <div className="button-group">
                    <button
                      className="bad"
                      onClick={() => markAsBad(index)}
                    >
                      ❌ Позначити як поганий
                    </button>
                    <button
                      className="confirm"
                      onClick={() => confirmGood(index)}
                    >
                      ✅ Залишити як хороший
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
