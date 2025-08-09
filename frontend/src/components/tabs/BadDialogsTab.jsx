// frontend/src/components/tabs/BadDialogsTab.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './BadDialogsTab.css';
import { Card } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';

export default function BadDialogsTab() {
  const [dialogs, setDialogs] = useState([]);
  const [feedbacks, setFeedbacks] = useState({});
  const [sending, setSending] = useState({});
  const [error, setError] = useState('');

  useEffect(() => {
    fetchBadDialogs();
    // eslint-disable-next-line
  }, []);

  const fetchBadDialogs = async () => {
    try {
      setError('');
      const { data } = await axios.get('bad_dialogs');
      if (Array.isArray(data)) {
        setDialogs(data);
      } else {
        setError('Сервер повернув некоректний формат.');
        setDialogs([]);
      }
    } catch (error) {
      setError('Не вдалося завантажити погані діалоги');
      setDialogs([]);
      console.error('❌ Помилка завантаження поганих діалогів:', error);
    }
  };

  const handleFeedbackChange = (index, text) => {
    setFeedbacks((f) => ({ ...f, [index]: text }));
  };

  const handleFeedbackSubmit = async (index) => {
    const comment = (feedbacks[index] || '').trim();
    if (!comment) return;
    setSending((prev) => ({ ...prev, [index]: true }));
    setError('');
    try {
      await axios.post('bad_dialogs/feedback', { index, comment });
      setDialogs((d) => d.filter((_, i) => i !== index));
      setFeedbacks((f) => {
        const next = { ...f };
        delete next[index];
        return next;
      });
    } catch (error) {
      setError('❌ Не вдалося зберегти фідбек.');
      console.error('❌ Помилка збереження фідбеку:', error);
    } finally {
      setSending((prev) => ({ ...prev, [index]: false }));
    }
  };

  return (
    <div className="bad-tab">
      <h2>⚠️ Погані діалоги</h2>
      {error && <div className="status error">{error}</div>}
      <div className="dialog-list">
        {dialogs.length === 0 && !error && (
          <div className="status">Усі діалоги вже розглянуті! 👌</div>
        )}
        {dialogs.map((dialogItem, index) => (
          <Card key={index}>
            <div className="dialog-content">
              {dialogItem.dialog.map((msg, i) => (
                <div key={i} className="dialog-line">
                  <b>{msg.role === 'user' ? '👤 Кандидат:' : '🤖 Бот:'}</b>
                  <span>{msg.text}</span>
                </div>
              ))}
            </div>
            <Textarea
              placeholder="Як поліпшити відповідь бота чи весь діалог?.."
              value={feedbacks[index] || ''}
              onChange={(e) => handleFeedbackChange(index, e.target.value)}
              className="manager-comment"
              disabled={sending[index]}
            />
            <div className="button-group">
              <Button
                onClick={() => handleFeedbackSubmit(index)}
                disabled={
                  !feedbacks[index] ||
                  !feedbacks[index].trim() ||
                  sending[index]
                }
              >
                {sending[index] ? '⏳ Надсилаємо...' : '💾 Надіслати фідбек'}
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
