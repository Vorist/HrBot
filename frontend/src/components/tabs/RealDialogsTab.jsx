import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '@/components/tabs/RealDialogsTab.css';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function RealDialogsTab() {
  const [dialogs, setDialogs] = useState([]);
  const [source, setSource] = useState('');
  const [dialogText, setDialogText] = useState('');

  useEffect(() => {
    fetchDialogs();
  }, []);

  const fetchDialogs = async () => {
    try {
      const res = await axios.get('/api/real_dialogs');
      setDialogs(res.data);
    } catch (err) {
      console.error('❌ Помилка завантаження:', err);
    }
  };

  const handleAdd = async () => {
    if (!source.trim() || !dialogText.trim()) return;
    try {
      await axios.post('/api/real_dialogs', {
        source,
        dialog: dialogText,
      });
      setSource('');
      setDialogText('');
      fetchDialogs();
    } catch (err) {
      console.error('❌ Помилка додавання:', err);
    }
  };

  const handleDelete = async (index) => {
    try {
      await axios.delete(`/api/real_dialogs/${index}`);
      setDialogs((prev) => prev.filter((_, i) => i !== index));
    } catch (err) {
      console.error('❌ Помилка видалення:', err);
    }
  };

  const handleConvert = async (index, target) => {
    try {
      await axios.post('/api/real_dialogs/convert', {
        index,
        target,
      });
      setDialogs((prev) => prev.filter((_, i) => i !== index));
    } catch (err) {
      console.error('❌ Помилка конвертації:', err);
    }
  };

  return (
    <div className="real-tab">
      <h2>💬 Реальні діалоги</h2>

      <div className="add-dialog-form">
        <Input
          placeholder="source: OLX / Instagram"
          value={source}
          onChange={(e) => setSource(e.target.value)}
        />
        <Textarea
          rows={6}
          placeholder={`bot Привіт, це актуально?\nuser Так, вакансія ще відкрита!`}
          value={dialogText}
          onChange={(e) => setDialogText(e.target.value)}
        />
        <Button onClick={handleAdd}>➕ Додати</Button>
      </div>

      <div className="dialog-list">
        {dialogs.map((d, i) => (
          <Card key={i}>
            <div className="source-line">📥 Джерело: {d.source}</div>
            <div className="dialog-text">
              {d.dialog.map((line, idx) => (
                <div key={idx}>
                  {line.role === 'user' ? '👤' : '🤖'} {line.text}
                </div>
              ))}
            </div>
            <div className="button-group">
              <Button onClick={() => handleConvert(i, 'good')}>✅ В хороші</Button>
              <Button onClick={() => handleConvert(i, 'bad')}>⚠️ В погані</Button>
              <Button onClick={() => handleDelete(i)} variant="destructive">🗑️</Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
