import React, { useState, useEffect } from 'react';
import { Layout, Button, notification } from 'antd';
import Header from './Header';  // Импортируем новый компонент
import './App.css';

const { Content } = Layout;

const App = () => {
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
    <Layout className="layout">
      <Header />  {/* Используем новый компонент */}
      <Content style={{ padding: '0 25px', textAlign: 'center', marginTop: '64px' }}>
        <div className="site-layout-content">
          <h1>Дипломная работа!</h1>
          {data ? <p>{data.message}</p> : <p>Loading...</p>}
          <Button type="primary" onClick={handleClick}>Click Me</Button>
        </div>
      </Content>
    </Layout>
  );
};

export default App;
