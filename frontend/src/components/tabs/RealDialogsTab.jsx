// frontend/src/components/tabs/RealDialogsTab.jsx

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './RealDialogsTab.css';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function RealDialogsTab() {
  const [dialogs, setDialogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [source, setSource] = useState('');
  const [dialogText, setDialogText] = useState('');

  useEffect(() => {
    fetchDialogs();
  }, []);

  const fetchDialogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await axios.get('/api/real_dialogs/');
      if (Array.isArray(data)) {
        setDialogs(data);
      } else {
        throw new Error('Невірний формат відповіді');
      }
    } catch (err) {
      console.error('❌ Помилка завантаження реальних діалогів:', err);
      setError('Не вдалося завантажити діалоги');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    if (!source.trim() || !dialogText.trim()) return;
    try {
      await axios.post('/api/real_dialogs/', {
        source,
        dialog: dialogText,
      });
      setSource('');
      setDialogText('');
      fetchDialogs();
    } catch (err) {
      console.error('❌ Помилка додавання діалогу:', err);
      setError('Не вдалося додати діалог');
    }
  };

  const handleDelete = async (index) => {
    try {
      await axios.delete(`/api/real_dialogs/${index}`);
      setDialogs((prev) => prev.filter((_, i) => i !== index));
    } catch (err) {
      console.error('❌ Помилка видалення діалогу:', err);
      setError(`Не вдалося видалити діалог #${index}`);
    }
  };

  const handleConvert = async (index, target) => {
    try {
      await axios.post('/api/real_dialogs/convert', { index, target });
      setDialogs((prev) => prev.filter((_, i) => i !== index));
    } catch (err) {
      console.error('❌ Помилка конвертації діалогу:', err);
      setError('Не вдалося перемістити діалог');
    }
  };

  return (
    <div className="real-tab">
      <h2>💬 Реальні діалоги</h2>

      <div className="add-dialog-form">
        <Input
          placeholder="Source: Instagram, OLX тощо"
          value={source}
          onChange={(e) => setSource(e.target.value)}
        />
        <Textarea
          rows={4}
          placeholder="👤 Привіт, це актуально?\n🤖 Так, вакансія відкрита!"
          value={dialogText}
          onChange={(e) => setDialogText(e.target.value)}
        />
        <Button onClick={handleAdd}>➕ Додати</Button>
      </div>

      {loading ? (
        <p className="status">⏳ Завантаження...</p>
      ) : error ? (
        <p className="status error">{error}</p>
      ) : dialogs.length === 0 ? (
        <p className="status">Діалоги відсутні.</p>
      ) : (
        <div className="dialog-list">
          {dialogs.map((item, idx) => (
            <Card key={idx}>
              <div className="source-line">📥 Джерело: {item.source}</div>
              <div className="dialog-text">
                {Array.isArray(item.dialog) ? (
                  item.dialog.map((line, i) => (
                    <div key={i} className="dialog-line">
                      {line.role === 'user' ? '👤' : '🤖'} {line.text}
                    </div>
                  ))
                ) : (
                  <div>⚠️ Некоректний формат діалогу</div>
                )}
              </div>
              <div className="button-group">
                <Button onClick={() => handleConvert(idx, 'good')}>✅ В good</Button>
                <Button onClick={() => handleConvert(idx, 'bad')}>⚠️ В bad</Button>
                <Button variant="destructive" onClick={() => handleDelete(idx)}>
                  🗑️ Видалити
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
