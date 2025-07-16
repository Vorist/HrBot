import React, { useState } from "react";
import RealDialogsTab from "./RealDialogsTab";
import GoodDialogsTab from "./GoodDialogsTab";
import BadDialogsTab from "./BadDialogsTab";
import StrategiesTab from "./StrategiesTab";
import FeedbackTab from "./FeedbackTab";
import { Button } from "@/components/ui/button";

const TABS = [
  { id: "real", label: "💬 Реальні діалоги" },
  { id: "good", label: "✅ Хороші діалоги" },
  { id: "bad", label: "⚠️ Погані діалоги" },
  { id: "strategies", label: "📈 Стратегії" },
  { id: "feedback", label: "💬 Фідбек" },
];

export default function Tabs() {
  const [activeTab, setActiveTab] = useState("real");

  const renderActiveTab = () => {
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
      default:
        return null;
    }
  };

  return (
    <div className="tabs-container">
      <div className="tabs-header">
        {TABS.map((tab) => (
          <Button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`tab-button ${activeTab === tab.id ? "active" : ""}`}
          >
            {tab.label}
          </Button>
        ))}
      </div>

      <div className="tabs-content">{renderActiveTab()}</div>
    </div>
  );
}
