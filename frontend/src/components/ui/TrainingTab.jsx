import React, { useState } from "react";
import axios from "axios";
import "@/components/ui/TrainingTab.css";

const trainingOptions = [
  { label: "✅ Навчити на good_dialogs", endpoint: "/api/train/good" },
  { label: "⚠️ Навчити на bad_dialogs", endpoint: "/api/train/bad" },
  { label: "💬 Навчити з урахуванням фідбеку", endpoint: "/api/train/feedback" },
  { label: "🔄 Навчити на real_dialogs", endpoint: "/api/train/real" },
  { label: "🧠 Повне навчання", endpoint: "/api/train/full" },
];

const TrainingTab = () => {
  const [status, setStatus] = useState("");

  const handleTraining = async (endpoint) => {
    try {
      setStatus("⏳ Виконується...");
      const response = await axios.post(endpoint);
      if (response.data.success) {
        setStatus("✅ Навчання завершено успішно.");
      } else {
        setStatus("⚠️ Помилка під час навчання.");
      }
    } catch (error) {
      console.error(error);
      setStatus("❌ Сталася помилка при запиті.");
    }
  };

  return (
    <div className="training-tab">
      {trainingOptions.map((option, index) => (
        <div className="training-option" key={index}>
          <span>{option.label}</span>
          <button onClick={() => handleTraining(option.endpoint)}>Запустити</button>
        </div>
      ))}
      {status && <div className="status-message">{status}</div>}
    </div>
  );
};

export default TrainingTab;
