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

  useEffect(() => {
    fetchBadDialogs();
  }, []);

  const fetchBadDialogs = async () => {
    try {
      const { data } = await axios.get('/api/bad_dialogs');
      if (Array.isArray(data)) {
        setDialogs(data);
      } else {
        console.error('❌ Очікувався масив, а отримано:', data);
      }
    } catch (error) {
      console.error('❌ Помилка завантаження поганих діалогів:', error);
    }
  };

  const handleFeedbackChange = (index, text) => {
    setFeedbacks((f) => ({ ...f, [index]: text }));
  };

  const handleFeedbackSubmit = async (index) => {
    const comment = feedbacks[index] || '';
    if (!comment.trim()) return;
    try {
      await axios.post('/api/bad_dialogs/feedback', { index, comment });
      // убираем отправленный элемент из списка
      setDialogs((d) => d.filter((_, i) => i !== index));
      // и чистим фидбек
      setFeedbacks((f) => {
        const next = { ...f };
        delete next[index];
        return next;
      });
    } catch (error) {
      console.error('❌ Помилка збереження фідбеку:', error);
    }
  };

  return (
    <div className="bad-tab">
      <h2>⚠️ Погані діалоги</h2>
      <div className="dialog-list">
        {dialogs.map((dialogItem, index) => (
          <Card key={index}>
            {/* Если нужно — можно показывать дату: dialogItem.date */}
            {dialogItem.dialog.map((msg, i) => (
              <div key={i} className="dialog-line">
                {msg.role === 'user'
                  ? `👤 Пропозиція кандидата: ${msg.text}`
                  : `🤖 Відповідь бота: ${msg.text}`}
              </div>
            ))}

            <Textarea
              placeholder="Напиши, як покращити відповідь бота..."
              value={feedbacks[index] || ''}
              onChange={(e) => handleFeedbackChange(index, e.target.value)}
              className="mt-2"
            />

            <div className="button-group">
              <Button onClick={() => handleFeedbackSubmit(index)}>
                💾 Надіслати фідбек
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
