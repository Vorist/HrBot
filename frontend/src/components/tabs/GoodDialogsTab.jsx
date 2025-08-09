// frontend/src/components/tabs/GoodDialogsTab.jsx
import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import './GoodDialogsTab.css';

export default function GoodDialogsTab() {
  const [dialogs, setDialogs] = useState([]);
  const [expanded, setExpanded] = useState(null);
  const [comments, setComments] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Загрузка диалогов
  const fetchDialogs = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await axios.get('good_dialogs');
      const data = res.data;
      const items = Array.isArray(data)
        ? data
        : Array.isArray(data.items)
        ? data.items
        : [];
      setDialogs(items);
    } catch (err) {
      setError('Не вдалося завантажити хороші діалоги');
      setDialogs([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDialogs();
  }, [fetchDialogs]);

  // Открытие/закрытие карточки
  const handleToggle = (index) => {
    setExpanded(expanded === index ? null : index);
  };

  // Комментарии менеджера
  const handleComment = (index, value) => {
    setComments((prev) => ({ ...prev, [index]: value }));
  };

  // Пометить как bad
  const markAsBad = async (index) => {
    setError('');
    try {
      await axios.post('good_dialogs/feedback', {
        index,
        comment: comments[index] || '',
      });
      setDialogs((prev) => prev.filter((_, i) => i !== index));
      setExpanded(null);
    } catch (err) {
      setError('Помилка при фідбеці');
    }
  };

  // Оставить как хороший — просто свернуть
  const confirmGood = () => setExpanded(null);

  // Рендерим отдельную карточку
  const renderDialog = (dialog, index) => (
    <div key={index} className={`dialog-card${expanded === index ? ' expanded' : ''}`}>
      <div className="card-header" onClick={() => handleToggle(index)}>
        👤 {dialog.user || 'Кандидат'}, {dialog.date || 'дата невідома'}
      </div>
      {expanded === index && (
        <div className="card-body">
          <div className="dialog-content">
            {Array.isArray(dialog.dialog)
              ? dialog.dialog.map((line, i) => (
                  <div key={i} className="dialog-line">
                    <b>{line.role === 'user' ? '👤' : '🤖'}</b> {line.text}
                  </div>
                ))
              : typeof dialog.dialog === 'string'
              ? dialog.dialog
                  .split('\n')
                  .map((line, i) => (
                    <div key={i} className="dialog-line">{line.trim()}</div>
                  ))
              : <div>⚠️ Некоректний формат діалогу</div>
            }
          </div>
          <textarea
            className="manager-comment"
            placeholder="💬 Коментар менеджера..."
            value={comments[index] || ''}
            onChange={e => handleComment(index, e.target.value)}
          />
          <div className="button-group">
            <button className="bad" onClick={() => markAsBad(index)}>
              ❌ Позначити як поганий
            </button>
            <button className="confirm" onClick={confirmGood}>
              ✅ Залишити як хороший
            </button>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="good-tab">
      <h2>✅ Хороші діалоги</h2>
      {loading ? (
        <p className="status">⏳ Завантаження...</p>
      ) : error ? (
        <p className="status error">{error}</p>
      ) : dialogs.length === 0 ? (
        <p className="status">📭 Немає хороших діалогів для відображення.</p>
      ) : (
        <div className="dialog-list">
          {dialogs.map(renderDialog)}
        </div>
      )}
    </div>
  );
}
