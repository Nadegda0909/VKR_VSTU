import React, { useState, useEffect } from 'react';
import { Layout, notification } from 'antd';
import Header from './Header';
import Login from './Login';
import './App.css';
import DownloadButton from "./Components/DownloadButton";

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

  const handleLogin = (values) => {
    console.log('Logged in with values:', values);
    setAuthenticated(true);
  };

  const openNotification = (message) => {
    notification.open({
      message: 'Обновление процесса',
      description: message,
      placement: 'topLeft',
    });
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
          <DownloadButton openNotification={openNotification} />  {/* Передаем функцию уведомления */}
        </div>
      </Content>
    </Layout>
  );
};

export default App;
