// frontend/src/components/tabs/BadDialogsTab.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './BadDialogsTab.css';

export default function BadDialogsTab() {
  const [dialogs, setDialogs] = useState([]);
  const [newDialog, setNewDialog] = useState('');
  const [feedbacks, setFeedbacks] = useState({});
  const [showCommentInput, setShowCommentInput] = useState({});

  useEffect(() => {
    fetchBadDialogs();
  }, []);

  const fetchBadDialogs = async () => {
    try {
      const response = await axios.get('/api/bad_dialogs');
      setDialogs(response.data);
    } catch (error) {
      console.error('Помилка завантаження поганих діалогів:', error);
    }
  };

  const handleDelete = async (index) => {
    try {
      await axios.delete(`/api/bad_dialogs/${index}`);
      setDialogs(dialogs.filter((_, i) => i !== index));
    } catch (error) {
      console.error('Не вдалося видалити діалог:', error);
    }
  };

  const handlePromoteToGood = async (index) => {
    try {
      await axios.post('/api/bad_dialogs/feedback', {
        index,
        comment: feedbacks[index] || ''
      });
      setDialogs(dialogs.filter((_, i) => i !== index));
    } catch (error) {
      console.error('Не вдалося перенести діалог у "хороші":', error);
    }
  };

  const handleAddNew = async () => {
    try {
      await axios.post('/api/bad_dialogs', {
        user: 'Кандидат',
        dialog: parseDialogText(newDialog)
      });
      setNewDialog('');
      fetchBadDialogs();
    } catch (error) {
      if (error.response && error.response.status === 409) {
        alert('Такий діалог вже існує.');
      } else {
        console.error('Помилка при додаванні:', error);
      }
    }
  };

  const handleTrain = async () => {
    try {
      const response = await axios.post('/api/training/bad');
      alert('Навчання завершено:\n\n' + response.data.message);
    } catch (error) {
      console.error('Помилка навчання:', error);
    }
  };

  const parseDialogText = (text) => {
    return text
      .split('\n')
      .filter(Boolean)
      .map((line) => {
        if (line.startsWith('👤')) return { role: 'user', text: line.replace('👤', '').trim() };
        if (line.startsWith('🤖')) return { role: 'bot', text: line.replace('🤖', '').trim() };
        return { role: 'bot', text: line }; // fallback
      });
  };

  return (
    <div className="bad-tab">
      <h2>⚠️ Погані діалоги</h2>

      <div className="bad-controls">
        <textarea
          placeholder="📥 Джерело: OLX\n👤 Добрий день\n🤖 Добрий день, слухаю вас..."
          value={newDialog}
          onChange={(e) => setNewDialog(e.target.value)}
        />
        <button onClick={handleAddNew}>➕ Додати</button>
        <button onClick={handleTrain}>🧠 Навчити</button>
      </div>

      <div className="dialog-list">
        {dialogs.map((d, index) => (
          <div className="dialog-card" key={index}>
            <div className="dialog-header">
              {d.user || 'Кандидат'}, {d.date || 'Дата невідома'}
            </div>

            <div className="dialog-body">
              {d.dialog.map((line, i) => (
                <div key={i} className="dialog-line">
                  <strong>{line.role === 'user' ? '👤' : '🤖'}</strong> {line.text}
                </div>
              ))}
            </div>

            <div className="dialog-footer">
              <textarea
                placeholder="Залишити коментар..."
                value={feedbacks[index] || ''}
                onChange={(e) =>
                  setFeedbacks({ ...feedbacks, [index]: e.target.value })
                }
              />
              <div className="dialog-actions">
                <button onClick={() => handlePromoteToGood(index)}>✅ В good</button>
                <button onClick={() => handleDelete(index)}>🗑️ Видалити</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
