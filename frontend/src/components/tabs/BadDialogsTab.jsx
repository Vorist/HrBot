import React, { useEffect, useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { toast } from "sonner";

export default function BadDialogsTab() {
  const [dialogs, setDialogs] = useState([]);
  const [newDialog, setNewDialog] = useState("");
  const [comment, setComment] = useState({});
  const [expanded, setExpanded] = useState({});
  const [training, setTraining] = useState(false);
  const textareaRef = useRef(null);

  const fetchDialogs = async () => {
    try {
      const res = await fetch("/api/bad_dialogs");
      const data = await res.json();
      setDialogs(data);
    } catch {
      toast.error("❌ Не вдалося завантажити bad-діалоги");
    }
  };

  useEffect(() => {
    fetchDialogs();
  }, []);

  const toggleExpand = (index) => {
    setExpanded((prev) => {
      const newState = { ...prev, [index]: !prev[index] };
      if (newState[index]) {
        setTimeout(() => textareaRef.current?.focus(), 100);
      }
      return newState;
    });
  };

  const handleMarkGood = async (index) => {
    const dialog = dialogs[index];
    const text = dialog.text;
    const feedback = comment[index] || "";

    try {
      await fetch("/api/good_dialogs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      await fetch(`/api/bad_dialogs/${index}`, { method: "DELETE" });

      await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          comment: feedback,
          status: "positive",
          source: "bad_dialogs",
        }),
      });

      setDialogs((prev) => prev.filter((_, i) => i !== index));
      toast.success("✅ Перенесено в хороші + фідбек збережено");
    } catch {
      toast.error("❌ Помилка при перенесенні або фідбеці");
    }
  };

  const handleAdd = async () => {
    const dialog = newDialog.trim();
    if (!dialog) return;

    try {
      const res = await fetch("/api/bad_dialogs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: dialog }),
      });

      if (!res.ok) throw new Error("❌ Неможливо додати");

      const data = await res.json();
      setDialogs((prev) => [...prev, data]);
      setNewDialog("");
      toast.success("➕ Додано bad-діалог");
    } catch (err) {
      toast.error(err.message || "Помилка додавання діалогу");
    }
  };

  const handleDelete = async (index) => {
    try {
      const res = await fetch(`/api/bad_dialogs/${index}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error("Помилка видалення");

      setDialogs((prev) => prev.filter((_, i) => i !== index));
      toast.success("🗑 Діалог видалено");
    } catch (err) {
      toast.error(err.message || "Помилка при видаленні");
    }
  };

  const handleTrain = async () => {
    setTraining(true);
    try {
      const res = await fetch("/api/training/bad", { method: "POST" });
      const text = await res.text();
      toast.success("🧠 Навчання завершено");
      console.log(text);
    } catch {
      toast.error("❌ Помилка навчання");
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex-between">
        <h2 className="text-xl font-semibold">🚫 Погані діалоги</h2>
        <Button onClick={handleTrain} disabled={training}>
          {training ? "Навчання..." : "🧠 Навчити"}
        </Button>
      </div>

      {dialogs.map((dialog, index) => {
        const lines = dialog.text.split("\n");
        const firstUserLine = lines.find((l) => l.startsWith("👤")) || "";
        const meta = firstUserLine.slice(2, 50).split("—");

        const name = meta[0]?.trim() || "Кандидат";
        const date = meta[1]?.trim() || "Без дати";

        return (
          <Card key={index} className="bg-light-red">
            <CardContent>
              <div
                className="text-sm font-semibold clickable"
                onClick={() => toggleExpand(index)}
              >
                👤 {name} — 📅 {date} {expanded[index] ? "▲" : "▼"}
              </div>

              {expanded[index] && (
                <div className="space-y-2 mt-2">
                  <pre className="whitespace-pre-wrap text-sm">
                    {dialog.text}
                  </pre>

                  <Textarea
                    ref={textareaRef}
                    placeholder="✍️ Ваш коментар"
                    value={comment[index] || ""}
                    onChange={(e) =>
                      setComment({ ...comment, [index]: e.target.value })
                    }
                  />

                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleDelete(index)}
                    >
                      🗑 Видалити
                    </Button>
                    <Button size="sm" onClick={() => handleMarkGood(index)}>
                      ✅ Позначити як хороший
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        );
      })}

      <div className="flex flex-col gap-2">
        <Textarea
          value={newDialog}
          onChange={(e) => setNewDialog(e.target.value)}
          placeholder="📥 Джерело: OLX\n👤 Добрий день!\n🤖 Вітаю, чим можу допомогти?"
        />
        <Button onClick={handleAdd} className="self-end w-fit">
          ➕ Додати
        </Button>
      </div>
    </div>
  );
}
