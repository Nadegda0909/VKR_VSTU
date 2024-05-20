import React, { useState, useEffect } from 'react';
import { Button, notification } from 'antd';
import './App.css';

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('/api/data')  // Используем относительный путь
      .then((response) => response.json())
      .then((data) => setData(data));
  }, []);

  const handleClick = () => {
    notification.open({
      message: 'Notification Title',
      description: 'Button click sent to backend.',
      placement: 'topLeft',  // Устанавливаем размещение уведомления в верхнем левом углу
    });

    fetch('/api/button-click', { method: 'POST' })
      .then(response => response.json())
      .then(data => console.log(data));
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Data from FastAPI</h1>
        {data ? <p>{data.message}</p> : <p>Loading...</p>}
        <Button type="primary" onClick={handleClick}>Click Me</Button>
      </header>
    </div>
  );
}

export default App;
