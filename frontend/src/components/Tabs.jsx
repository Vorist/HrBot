import React, { useState } from "react";
import RealDialogsTab from "@/components/tabs/RealDialogsTab";
import GoodDialogsTab from "@/components/tabs/GoodDialogsTab";
import BadDialogsTab from "@/components/tabs/BadDialogsTab";
import StrategiesTab from "@/components/tabs/StrategiesTab";
import FeedbackTab from "@/components/tabs/FeedbackTab";

import { Button } from "@/components/ui/button";

const TABS = [
  { id: "real", label: "💬 Реальні діалоги", component: <RealDialogsTab /> },
  { id: "good", label: "✅ Хороші діалоги", component: <GoodDialogsTab /> },
  { id: "bad", label: "⚠️ Погані діалоги", component: <BadDialogsTab /> },
  { id: "strategies", label: "📈 Стратегії", component: <StrategiesTab /> },
  { id: "feedback", label: "💬 Фідбек", component: <FeedbackTab /> },
];

export default function Tabs() {
  const [activeTab, setActiveTab] = useState("real");

  const activeComponent = TABS.find((tab) => tab.id === activeTab)?.component;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {TABS.map((tab) => (
          <Button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            variant={activeTab === tab.id ? "default" : "outline"}
            className={activeTab === tab.id ? "font-bold" : ""}
          >
            {tab.label}
          </Button>
        ))}
      </div>

      <div className="pt-2">
        {activeComponent || <p className="text-red-500">❌ Вкладка не знайдена</p>}
      </div>
    </div>
  );
}
