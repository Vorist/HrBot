import React, { useEffect, useState, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

export default function StrategiesTab() {
  const [strategies, setStrategies] = useState([]);
  const [editingIndex, setEditingIndex] = useState(null);
  const [editedText, setEditedText] = useState("");
  const [saving, setSaving] = useState(false);
  const textareaRef = useRef(null);

  // ⏬ Завантаження стратегій
  const fetchStrategies = async () => {
    try {
      const res = await fetch("/api/strategies");
      if (!res.ok) throw new Error("Не вдалося завантажити стратегії");
      const data = await res.json();
      setStrategies(data);
    } catch (e) {
      toast.error(e.message || "⚠️ Помилка при завантаженні стратегій");
    }
  };

  // ⏫ Збереження зміненої відповіді
  const saveEdited = async (index) => {
    if (!editedText.trim()) {
      toast.error("⚠️ Поле не може бути порожнім");
      return;
    }

    setSaving(true);
    try {
      const res = await fetch("/api/strategies/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index, improved: editedText }),
      });

      if (!res.ok) throw new Error("Не вдалося зберегти відповідь");

      toast.success("✅ Відповідь збережено");
      setEditingIndex(null);
      setEditedText("");
      await fetchStrategies();
    } catch (err) {
      toast.error(err.message || "❌ Помилка при збереженні");
    } finally {
      setSaving(false);
    }
  };

  // 🔁 Ініціалізація
  useEffect(() => {
    fetchStrategies();
  }, []);

  // 🎯 Автофокус при редагуванні
  useEffect(() => {
    if (editingIndex !== null && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [editingIndex]);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">📈 Стратегії покращення</h2>

      {strategies.map((item, index) => (
        <Card key={index} className="border border-muted">
          <CardContent className="space-y-4 py-4">
            {/* 📌 Контекст */}
            <div>
              <span className="font-semibold">📌 Контекст:</span>
              <p className="text-sm whitespace-pre-wrap">{item.context}</p>
            </div>

            {/* 🤖 Початкова відповідь */}
            <div>
              <span className="font-semibold">🤖 Було:</span>
              <p className="text-sm text-red-600 whitespace-pre-wrap">
                {item.original}
              </p>
            </div>

            {/* ✅ Покращена відповідь */}
            <div>
              <span className="font-semibold">✅ Стало:</span>
              {editingIndex === index ? (
                <>
                  <Textarea
                    ref={textareaRef}
                    className="mt-2"
                    rows={4}
                    value={editedText}
                    onChange={(e) => setEditedText(e.target.value)}
                  />
                  <div className="flex gap-2 mt-2">
                    <Button
                      size="sm"
                      onClick={() => saveEdited(index)}
                      disabled={saving || !editedText.trim()}
                    >
                      {saving ? "Збереження..." : "💾 Зберегти"}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setEditingIndex(null);
                        setEditedText("");
                      }}
                    >
                      Скасувати
                    </Button>
                  </div>
                </>
              ) : (
                <div className="flex justify-between items-start mt-1">
                  <span className="whitespace-pre-wrap text-sm text-green-700">
                    {item.improved?.trim()
                      ? item.improved
                      : "— (ще не редаговано)"}
                  </span>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setEditingIndex(index);
                      setEditedText(item.improved || "");
                    }}
                  >
                    ✏️ Редагувати
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
