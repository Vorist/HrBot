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
    <nav className="tabs-nav" role="tablist" aria-label="Main navigation">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isActive}
            onClick={() => setActiveTab(tab.id)}
            className={`btn ${isActive ? 'btn-primary' : 'btn-neutral'} tab-button`}
          >
            {tab.label}
          </button>
        );
      })}
    </nav>
  );
}

export default Tabs;
