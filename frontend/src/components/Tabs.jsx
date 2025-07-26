// frontend/src/components/Tabs.jsx
import React from 'react';
import './Tabs.css';

const tabs = [
  { id: 'real', label: '💬 Реальні діалоги' },
  { id: 'good', label: '✅ Хороші діалоги' },
  { id: 'bad', label: '⚠️ Погані діалоги' },
  { id: 'feedback', label: '💬 Фідбек' },
  { id: 'strategies', label: '📈 Стратегії' },
  { id: 'training', label: '🧠 Навчання' },
];

function Tabs({ activeTab, setActiveTab }) {
  return (
    <nav className="tabs-nav">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className={activeTab === tab.id ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}

export default Tabs;
