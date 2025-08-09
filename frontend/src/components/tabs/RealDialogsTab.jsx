import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './RealDialogsTab.css';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function RealDialogsTab() {
  const [dialogs, setDialogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [source, setSource] = useState('');
  const [dialogText, setDialogText] = useState('');
  const [adding, setAdding] = useState(false);

  const fetchDialogs = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const { data } = await axios.get('real_dialogs');
      if (!Array.isArray(data)) {
        throw new Error('Невірний формат відповіді');
      }
      setDialogs(data);
    } catch (err) {
      console.error('❌ Помилка завантаження діалогів:', err);
      const msg = err.response?.data?.detail || err.message;
      setError(`Не вдалося завантажити діалоги: ${msg}`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDialogs();
  }, [fetchDialogs]);

  const handleAdd = async () => {
    if (!source.trim() || !dialogText.trim()) {
      setError('Введіть і джерело, і текст діалогу');
      return;
    }
    setAdding(true);
    setError('');
    try {
      await axios.post('real_dialogs', { source, dialog: dialogText });
      setSource('');
      setDialogText('');
      await fetchDialogs();
    } catch (err) {
      console.error('❌ Помилка додавання діалогу:', err);
      const msg = err.response?.data?.detail || err.message;
      setError(`Не вдалося додати діалог: ${msg}`);
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (index) => {
    setError('');
    try {
      await axios.delete(`real_dialogs/${index}`);
      setDialogs((prev) => prev.filter((_, i) => i !== index));
    } catch (err) {
      console.error('❌ Помилка видалення діалогу:', err);
      const msg = err.response?.data?.detail || err.message;
      setError(`Не вдалося видалити #${index}: ${msg}`);
    }
  };

  const handleConvert = async (index, target) => {
    setError('');
    try {
      await axios.post('real_dialogs/convert', { index, target });
      setDialogs((prev) => prev.filter((_, i) => i !== index));
    } catch (err) {
      console.error('❌ Помилка конвертації діалогу:', err);
      const msg = err.response?.data?.detail || err.message;
      setError(`Не вдалося перемістити #${index}: ${msg}`);
    }
  };

  const renderDialogLines = (dialog) => {
    if (Array.isArray(dialog)) {
      return dialog.map((line, i) => (
        <div key={i} className="dialog-line">
          {line.role === 'user' ? '👤' : '🤖'} {line.text}
        </div>
      ));
    }
    if (typeof dialog === 'string') {
      return dialog
        .split('\n')
        .map((line, i) => (
          <div key={i} className="dialog-line">
            {line.trim()}
          </div>
        ));
    }
    return <div>⚠️ Некоректний формат діалогу</div>;
  };

  return (
    <div className="real-tab">
      <h2>💬 Реальні діалоги</h2>

      <div className="add-dialog-form">
        <Input
          placeholder="Джерело: Instagram, OLX тощо"
          value={source}
          onChange={(e) => setSource(e.target.value)}
        />
        <Textarea
          rows={4}
          placeholder="👤 Привіт, це актуально?\n🤖 Так, вакансія відкрита!"
          value={dialogText}
          onChange={(e) => setDialogText(e.target.value)}
        />
        <Button onClick={handleAdd} disabled={adding}>
          {adding ? 'Додаємо...' : '➕ Додати'}
        </Button>
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
            <Card key={`real-${idx}`}>
              <div className="source-line">📥 Джерело: {item.source}</div>
              <div className="dialog-text">{renderDialogLines(item.dialog)}</div>
              <div className="button-group">
                <Button onClick={() => handleConvert(idx, 'good')}>
                  ✅ В good
                </Button>
                <Button onClick={() => handleConvert(idx, 'bad')}>
                  ⚠️ В bad
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => handleDelete(idx)}
                >
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
