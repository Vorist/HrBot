import React, { useEffect, useRef, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function FeedbackTab() {
  const [feedbacks, setFeedbacks] = useState([]);
  const [newFeedback, setNewFeedback] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    fetch("/api/training/feedback")
      .then((res) => res.json())
      .then((data) => setFeedbacks(data))
      .catch(() => toast.error("❌ Не вдалося завантажити фідбеки"));
  }, []);

  useEffect(() => {
    if (selectedIndex !== null) {
      const selected = feedbacks[selectedIndex];
      setNewFeedback(selected?.comment || "");
      setTimeout(() => textareaRef.current?.focus(), 100);
    }
  }, [selectedIndex]);

  const handleSendFeedback = async () => {
    if (!newFeedback.trim() || selectedIndex === null) return;

    try {
      const res = await fetch("/api/training/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          index: selectedIndex,
          comment: newFeedback.trim(),
        }),
      });

      if (!res.ok) throw new Error("❌ Не вдалося зберегти фідбек");

      const updated = await res.json();
      setFeedbacks(updated);
      toast.success("✅ Фідбек збережено");
      setSelectedIndex(null);
      setNewFeedback("");
    } catch (err) {
      toast.error(err.message || "Помилка при збереженні");
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">💬 Фідбек по діалогам</h2>

      {feedbacks.map((item, index) => {
        const isSelected = selectedIndex === index;
        const hasComment = !!item.comment?.trim();
        const dialogText = Array.isArray(item.dialog)
          ? item.dialog.map((d) => `${d.role === "user" ? "👤" : "🤖"} ${d.text}`).join("\n")
          : typeof item.dialog === "string"
          ? item.dialog
          : "⚠️ Невідомий формат діалогу";

        return (
          <Card
            key={index}
            onClick={() => setSelectedIndex(index)}
            className={`cursor-pointer ${isSelected ? "highlighted-card" : "default-card"}`}
          >
            <CardContent className="space-y-2">
              <div className="text-sm whitespace-pre-wrap">
                <strong>📄 Діалог:</strong>
                <br />
                {dialogText}
              </div>

              {item.status && (
                <div className="text-xs text-muted-foreground italic">
                  🏷 Статус: {item.status}
                </div>
              )}

              {hasComment && !isSelected && (
                <div className="text-xs text-green-600 font-semibold">
                  💬 Коментар збережено
                </div>
              )}

              {isSelected && (
                <>
                  <Textarea
                    ref={textareaRef}
                    value={newFeedback}
                    onChange={(e) => setNewFeedback(e.target.value)}
                    placeholder="✍️ Напиши новий коментар до діалогу"
                  />
                  <div className="flex gap-2 justify-end">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setSelectedIndex(null);
                        setNewFeedback("");
                      }}
                    >
                      Скасувати
                    </Button>
                    <Button
                      onClick={handleSendFeedback}
                      disabled={!newFeedback.trim()}
                    >
                      💾 Зберегти фідбек
                    </Button>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
