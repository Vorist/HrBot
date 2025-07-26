import React, { useState } from 'react';
import './App.css';
import Tabs from './components/Tabs';

import RealDialogsTab from './components/tabs/RealDialogsTab';
import GoodDialogsTab from './components/tabs/GoodDialogsTab';
import BadDialogsTab from './components/tabs/BadDialogsTab';
import FeedbackTab from './components/tabs/FeedbackTab';
import StrategiesTab from './components/tabs/StrategiesTab';
import TrainingTab from './components/tabs/TrainingTab';

function App() {
  const [activeTab, setActiveTab] = useState('real');

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'real':
        return <RealDialogsTab />;
      case 'good':
        return <GoodDialogsTab />;
      case 'bad':
        return <BadDialogsTab />;
      case 'feedback':
        return <FeedbackTab />;
      case 'strategies':
        return <StrategiesTab />;
      case 'training':
        return <TrainingTab />;
      default:
        return <RealDialogsTab />;
    }
  };

  return (
    <div className="app-container">
      <h1 className="main-title">🧠 Панель керування HR-Ботом</h1>
      <Tabs activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="tab-content">{renderActiveTab()}</div>
    </div>
  );
}

export default App;
