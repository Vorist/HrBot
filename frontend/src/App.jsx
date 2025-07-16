import React, { useState } from "react";
import { Toaster } from "react-hot-toast";

import RealDialogsTab from "@/components/RealDialogsTab";
import GoodDialogsTab from "@/components/GoodDialogsTab";
import BadDialogsTab from "@/components/BadDialogsTab";
import StrategiesTab from "@/components/StrategiesTab";
import FeedbackTab from "@/components/FeedbackTab";
import TrainingTab from "@/components/TrainingTab";

const tabs = [
  { id: "real", label: "Реальні діалоги", icon: "💬" },
  { id: "good", label: "Хороші діалоги", icon: "✅" },
  { id: "bad", label: "Погані діалоги", icon: "⚠️" },
  { id: "strategies", label: "Стратегії", icon: "📈" },
  { id: "feedback", label: "Фідбек", icon: "💬" },
  { id: "training", label: "Навчання", icon: "🧠" },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("real");

  const renderTab = () => {
    switch (activeTab) {
      case "real": return <RealDialogsTab />;
      case "good": return <GoodDialogsTab />;
      case "bad": return <BadDialogsTab />;
      case "strategies": return <StrategiesTab />;
      case "feedback": return <FeedbackTab />;
      case "training": return <TrainingTab />;
      default: return null;
    }
  };

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#ffe4e6", padding: "1rem" }}>
      <Toaster position="top-center" toastOptions={{ duration: 4000 }} />

      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginBottom: "1.5rem" }}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`tab-button ${activeTab === tab.id ? "active" : ""}`}
          >
            <span>{tab.icon}</span> {tab.label}
          </button>
        ))}
      </div>

      <div>{renderTab()}</div>
    </div>
  );
}
