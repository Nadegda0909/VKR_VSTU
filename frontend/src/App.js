import React, { useState, useEffect } from 'react';
import { Layout, Button, notification } from 'antd';
import Header from './Header';
import Login from './Login';
import './App.css';

const { Content } = Layout;

const App = () => {
  const [data, setData] = useState(null);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    if (authenticated) {
      fetch('/api/data')  // Используем относительный путь
        .then((response) => response.json())
        .then((data) => setData(data));
    }
  }, [authenticated]);

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

  const handleLogin = (values) => {
    console.log('Logged in with values:', values);
    setAuthenticated(true);
  };

  if (!authenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <Layout className="layout">
      <Header />
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
