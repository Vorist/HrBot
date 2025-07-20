import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

export default function GoodDialogsTab() {
  const [dialogs, setDialogs] = useState([]);
  const [newDialogText, setNewDialogText] = useState("");
  const [newUserName, setNewUserName] = useState("");
  const [comment, setComment] = useState({});
  const [expanded, setExpanded] = useState({});
  const [training, setTraining] = useState(false);

  useEffect(() => {
    fetch("/api/good_dialogs")
      .then((res) => res.json())
      .then(setDialogs)
      .catch(() => toast.error("❌ Не вдалося завантажити good-діалоги"));
  }, []);

  const toggleExpand = (index) => {
    setExpanded((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  const handleMarkBad = async (index) => {
    const feedback = comment[index] || "";

    try {
      await fetch("/api/good_dialogs/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index, comment: feedback }),
      });

      setDialogs((prev) => prev.filter((_, i) => i !== index));
      toast.success("✅ Перенесено в bad + фідбек збережено");
    } catch {
      toast.error("❌ Помилка при перенесенні або фідбеці");
    }
  };

  const handleAdd = async () => {
    const user = newUserName.trim() || "Кандидат";
    const lines = newDialogText.trim().split("\n").filter(Boolean);

    const dialog = lines
      .map((line) => {
        if (line.startsWith("👤")) return { role: "user", text: line.slice(2).trim() };
        if (line.startsWith("🤖")) return { role: "bot", text: line.slice(2).trim() };
        return null;
      })
      .filter(Boolean);

    if (!dialog.length) {
      toast.error("⚠️ Діалог порожній або неправильний формат");
      return;
    }

    try {
      const res = await fetch("/api/good_dialogs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user, dialog }),
      });

      if (!res.ok) throw new Error();
      const data = await res.json();
      setDialogs((prev) => [...prev, data]);
      setNewDialogText("");
      setNewUserName("");
      toast.success("✅ Додано в good");
    } catch {
      toast.error("❌ Помилка при додаванні діалогу");
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
        const isExpanded = expanded[index];
        const dialogText = dialog.dialog
          .map((msg) => `${msg.role === "user" ? "👤" : "🤖"} ${msg.text}`)
          .join("\n");

        return (
          <Card key={index}>
            <CardContent className="space-y-2">
              <div
                className="cursor-pointer text-sm font-semibold"
                onClick={() => toggleExpand(index)}
              >
                👤 {dialog.user} — 📅 {dialog.date} {isExpanded ? "▲" : "▼"}
              </div>

              {isExpanded && (
                <>
                  <pre className="whitespace-pre-wrap text-sm">
                    {dialogText}
                  </pre>

                  <Textarea
                    placeholder="✍️ Ваш коментар"
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
        <Input
          value={newUserName}
          onChange={(e) => setNewUserName(e.target.value)}
          placeholder="Ім’я кандидата (необов’язково)"
        />
        <Textarea
          value={newDialogText}
          onChange={(e) => setNewDialogText(e.target.value)}
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
