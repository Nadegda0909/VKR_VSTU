import React, { useState, useEffect } from 'react';
import { Layout } from 'antd';
import Header from './Components/Header';
import Login from './Components/Login';
import './App.css';
import DownloadButton from "./Components/DownloadButton";
import UploadButton from "./Components/UploadButton";

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
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginBottom: 20 }}>
            <DownloadButton />  {/* Кнопка скачивания */}
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <UploadButton />    {/* Кнопка загрузки */}
          </div>
        </div>
      </Content>
    </Layout>
  );
};

export default App;
