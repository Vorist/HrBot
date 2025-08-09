// frontend/src/App.jsx
import React, { useState } from 'react';
import '@/index.css';
import Tabs from '@/components/Tabs';

import RealDialogsTab from '@/components/tabs/RealDialogsTab';
import GoodDialogsTab from '@/components/tabs/GoodDialogsTab';
import BadDialogsTab from '@/components/tabs/BadDialogsTab';
import FeedbackTab from '@/components/tabs/FeedbackTab';
import StrategiesTab from '@/components/tabs/StrategiesTab';
import TrainingTab from '@/components/tabs/TrainingTab';

const TAB_COMPONENTS = {
  real: RealDialogsTab,
  good: GoodDialogsTab,
  bad: BadDialogsTab,
  feedback: FeedbackTab,
  strategies: StrategiesTab,
  training: TrainingTab,
};

export default function App() {
  const [activeTab, setActiveTab] = useState('real');
  const ActiveTabComponent = TAB_COMPONENTS[activeTab] || RealDialogsTab;

  return (
    <div className="app-container">
      <h1 className="main-title">🧠 Панель керування HR-Ботом</h1>
      <Tabs activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="tab-content">
        <ActiveTabComponent />
      </div>
    </div>
  );
}
