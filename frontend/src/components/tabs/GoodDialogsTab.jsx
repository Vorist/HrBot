// frontend/src/components/GoodDialogsTab.jsx
import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

export default function GoodDialogsTab() {
  const [dialogs, setDialogs] = useState([]);
  const [newDialog, setNewDialog] = useState("");
  const [comment, setComment] = useState({});
  const [expanded, setExpanded] = useState({});
  const [training, setTraining] = useState(false);

  useEffect(() => {
    fetch("/api/good_dialogs")
      .then((res) => res.json())
      .then((data) => setDialogs(data))
      .catch(() => toast.error("❌ Не вдалося завантажити good-діалоги"));
  }, []);

  const toggleExpand = (index) => {
    setExpanded((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  const handleMarkBad = async (index) => {
    const dialog = dialogs[index];
    const text = dialog.text;
    const feedback = comment[index] || "";

    try {
      await fetch("/api/bad_dialogs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      await fetch(`/api/good_dialogs/${index}`, {
        method: "DELETE",
      });

      await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          comment: feedback,
          status: "negative",
          source: "good_dialogs",
        }),
      });

      setDialogs((prev) => prev.filter((_, i) => i !== index));
      toast.success("❌ Перенесено в погані + фідбек збережено");
    } catch (err) {
      toast.error("❌ Помилка при перенесенні або збереженні фідбеку");
    }
  };

  const handleAdd = async () => {
    const dialog = newDialog.trim();
    if (!dialog) return;

    try {
      const res = await fetch("/api/good_dialogs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: dialog }),
      });

      if (!res.ok) throw new Error("❌ Неможливо додати");

      const data = await res.json();
      setDialogs((prev) => [...prev, data]);
      setNewDialog("");
      toast.success("✅ Діалог додано");
    } catch {
      toast.error("❌ Помилка при додаванні good-діалогу");
    }
  };

  const handleTrain = async () => {
    setTraining(true);
    try {
      const res = await fetch("/api/training/good", { method: "POST" });
      const log = await res.text();

      if (res.ok) {
        toast.success("🧠 Навчання завершено");
        console.log(log);
      } else {
        toast.error("❌ Помилка під час навчання");
        console.error(log);
      }
    } catch {
      toast.error("❌ Помилка при навчанні");
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">✅ Хороші діалоги</h2>
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
          <Card key={index}>
            <CardContent className="space-y-2">
              <div
                className="cursor-pointer text-sm font-semibold text-primary"
                onClick={() => toggleExpand(index)}
              >
                👤 {name} — 📅 {date} {expanded[index] ? "▲" : "▼"}
              </div>

              {expanded[index] && (
                <>
                  <pre className="whitespace-pre-wrap text-sm">{dialog.text}</pre>

                  <Textarea
                    placeholder="✍️ Ваш коментар (необов'язково)"
                    value={comment[index] || ""}
                    onChange={(e) =>
                      setComment({ ...comment, [index]: e.target.value })
                    }
                  />

                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleMarkBad(index)}
                  >
                    ❌ Позначити як поганий
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
        );
      })}

      <div className="flex flex-col gap-2 mt-4">
        <Textarea
          value={newDialog}
          onChange={(e) => setNewDialog(e.target.value)}
          placeholder="📥 Джерело: Instagram\n👤 Привіт\n🤖 Доброго дня..."
          className="min-h-[100px]"
        />
        <Button onClick={handleAdd} className="self-end w-fit">
          ➕ Додати
        </Button>
      </div>
    </div>
  );
}
