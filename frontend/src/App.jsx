import React, { useState } from "react";
import { Toaster } from "react-hot-toast";

import RealDialogsTab from "@/components/tabs/RealDialogsTab";
import GoodDialogsTab from "@/components/tabs/GoodDialogsTab";
import BadDialogsTab from "@/components/tabs/BadDialogsTab";
import StrategiesTab from "@/components/tabs/StrategiesTab";
import FeedbackTab from "@/components/tabs/FeedbackTab";
import TrainingTab from "@/components/tabs/TrainingTab";


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
      case "real":
        return <RealDialogsTab />;
      case "good":
        return <GoodDialogsTab />;
      case "bad":
        return <BadDialogsTab />;
      case "strategies":
        return <StrategiesTab />;
      case "feedback":
        return <FeedbackTab />;
      case "training":
        return <TrainingTab />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-pink-100 p-4">
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 4000,
          style: {
            border: "1px solid #ff006e",
            padding: "10px",
            background: "#fff0f5",
            color: "#000",
          },
        }}
      />

      <div className="flex flex-wrap gap-2 mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-full border transition 
              ${
                activeTab === tab.id
                  ? "bg-pink-600 text-white border-pink-700"
                  : "bg-white text-pink-700 border-pink-300 hover:bg-pink-200"
              }`}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      <div>{renderTab()}</div>
    </div>
  );
}
