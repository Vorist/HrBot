import React, { useState } from "react";
import { Button } from "@/components/ui/button";

export default function TrainingTab() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [log, setLog] = useState("");

  const train = async (type) => {
    setLoading(true);
    setStatus(`⏳ Навчання ${type}...`);
    setLog("");

    try {
      const res = await fetch(`/api/training/${type}`, { method: "POST" });
      const output = await res.text();

      if (res.ok) {
        setStatus(`✅ Навчання на '${type}' завершено`);
      } else {
        setStatus(`❌ Помилка під час навчання (${type})`);
      }

      setLog(output);
    } catch (err) {
      const message = err.message || "Невідома помилка";
      setStatus(`❌ Помилка: ${message}`);
      setLog(message);
    } finally {
      setLoading(false);
    }
  };

  const trainingTypes = [
    { type: "good", label: "✅ Навчити на good_dialogs" },
    { type: "bad", label: "⚠️ Навчити на bad_dialogs" },
    { type: "feedback", label: "💬 Навчити з урахуванням фідбеку" },
    { type: "real", label: "📥 Навчити на real_dialogs" },
    { type: "all", label: "🧠 Повне навчання (all)" },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">🧠 Навчання бота</h2>

      <div className="flex flex-wrap gap-3">
        {trainingTypes.map(({ type, label }) => (
          <Button key={type} onClick={() => train(type)} disabled={loading}>
            {label}
          </Button>
        ))}
      </div>

      {status && (
        <p className="text-sm font-medium text-gray-800">
          {status}
        </p>
      )}

      {log && (
        <pre className="bg-white p-3 rounded text-sm whitespace-pre-wrap max-h-[400px] overflow-auto border border-gray-300">
          {log}
        </pre>
      )}
    </div>
  );
}
