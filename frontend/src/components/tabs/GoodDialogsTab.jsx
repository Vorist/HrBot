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
      const response = await axios.get('/api/good_dialogs');
      setDialogs(response.data);
    } catch (error) {
      console.error('Помилка завантаження хороших діалогів:', error);
    }
  };

  const handleToggle = (index) => {
    setExpandedIndex(index === expandedIndex ? null : index);
  };

  const handleCommentChange = (index, value) => {
    setComments({ ...comments, [index]: value });
  };

  const markAsBad = async (index) => {
    try {
      await axios.post('/api/good_dialogs/feedback', {
        index,
        comment: comments[index] || ''
      });
      setDialogs(dialogs.filter((_, i) => i !== index));
    } catch (error) {
      console.error('Помилка при фідбеці:', error);
    }
  };

  const confirmGood = async (index) => {
    try {
      await axios.post('/api/good_dialogs/confirm', { index });
    } catch (error) {
      console.error('Помилка при підтвердженні хорошого діалогу:', error);
    }
  };

  return (
    <div className="good-tab">
      <h2>✅ Хороші діалоги</h2>
      <div className="dialog-list">
        {dialogs.map((dialog, index) => (
          <div key={index} className="dialog-card">
            <div className="card-header" onClick={() => handleToggle(index)}>
              👤 {dialog.user || 'Кандидат'}, {dialog.date || 'дата невідома'}
            </div>

            {expandedIndex === index && (
              <div className="card-body">
                <div className="dialog-content">
                  {dialog.dialog.map((line, i) => (
                    <div key={i} className="dialog-line">
                      <strong>{line.role === 'user' ? '👤' : '🤖'}</strong> {line.text}
                    </div>
                  ))}
                </div>

                <textarea
                  placeholder="💬 Коментар менеджера..."
                  value={comments[index] || ''}
                  onChange={(e) => handleCommentChange(index, e.target.value)}
                />

                <div className="button-group">
                  <button className="bad" onClick={() => markAsBad(index)}>❌ Позначити як поганий</button>
                  <button className="confirm" onClick={() => confirmGood(index)}>✅ Залишити як хороший</button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
