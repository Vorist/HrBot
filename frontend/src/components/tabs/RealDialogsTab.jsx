// frontend/src/components/RealDialogsTab.jsx
import React, { useEffect, useRef, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { AnimatePresence, motion } from "framer-motion";
import { toast } from "react-hot-toast";

export default function RealDialogsTab() {
  const [dialogs, setDialogs] = useState([]);
  const [newDialog, setNewDialog] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    fetch("/api/real_dialogs")
      .then((res) => res.json())
      .then((data) => setDialogs(data))
      .catch((err) => console.error("❌ Failed to load dialogs", err));
  }, []);

  const handleAddDialog = () => {
    const dialog = newDialog.trim();
    if (!dialog) return;

    fetch("/api/real_dialogs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: dialog }),
    })
      .then(async (res) => {
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Помилка при додаванні");
        }
        return res.json();
      })
      .then((data) => {
        setDialogs((prev) => [...prev, data]);
        setNewDialog("");
        setTimeout(() => {
          bottomRef.current?.scrollIntoView({ behavior: "smooth" });
        }, 100);
        toast.success("✅ Діалог додано");
      })
      .catch((err) => {
        toast.error(err.message);
      });
  };

  const handleDeleteDialog = (index) => {
    fetch(`/api/real_dialogs/${index}`, { method: "DELETE" })
      .then((res) => {
        if (res.ok) {
          setDialogs((prev) => prev.filter((_, i) => i !== index));
          toast.success("🗑️ Діалог видалено");
        } else {
          toast.error("❌ Не вдалося видалити діалог");
        }
      })
      .catch((err) => console.error("❌ Failed to delete dialog", err));
  };

  const handleConvertAndTrain = async (index, target) => {
    try {
      const res = await fetch("/api/real_dialogs/convert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index, target }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Помилка при переміщенні");
      }

      setDialogs((prev) => prev.filter((_, i) => i !== index));
      toast.success(`📤 Діалог переміщено у ${target}`);

      const trainRes = await fetch(`/api/training/${target}`, { method: "POST" });
      const log = await trainRes.text();

      if (trainRes.ok) {
        toast.success(`🤖 Навчання на ${target} завершено`);
        console.log(log);
      } else {
        toast.error("❌ Помилка при навчанні");
        console.error(log);
      }
    } catch (err) {
      toast.error(err.message);
    }
  };

  const extractMeta = (text) => {
    const lines = text.split("\n");
    const sourceLine = lines.find((line) => line.startsWith("📥"));
    return {
      source: sourceLine?.replace("📥", "").trim() || "Невідоме джерело",
    };
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">💬 Реальні діалоги</h2>

      <AnimatePresence>
        {dialogs.map((dialog, index) => {
          const { source } = extractMeta(dialog.text);
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <Card>
                <CardContent className="space-y-2">
                  <p className="text-sm text-gray-600">{source}</p>
                  <pre className="whitespace-pre-wrap text-sm">{dialog.text}</pre>

                  <div className="flex gap-2 justify-end flex-wrap">
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleDeleteDialog(index)}
                    >
                      🗑 Видалити
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handleConvertAndTrain(index, "good")}
                    >
                      🔁 В хороші + навчити
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handleConvertAndTrain(index, "bad")}
                    >
                      ⚠️ В погані + навчити
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </AnimatePresence>

      <div className="flex flex-col gap-2 mt-4">
        <Textarea
          value={newDialog}
          onChange={(e) => setNewDialog(e.target.value)}
          placeholder={`📥 Джерело: OLX\n👤 Привіт...\n🤖 Вітаю!`}
          className="min-h-[120px]"
        />
        <Button onClick={handleAddDialog} className="self-end w-fit">
          ➕ Додати діалог
        </Button>
      </div>

      <div ref={bottomRef} />
    </div>
  );
}
