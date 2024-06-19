import React, { useState, useEffect } from 'react';
import { Layout } from 'antd';
import Header from './Components/Header';
import Login from './Components/Login';
import './App.css';
import DownloadButton from "./Components/DownloadButton";
import UploadButton from "./Components/UploadButton";
import { Typography } from 'antd';
const { Title, Text } = Typography;

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
      <Content style={{ padding: '0 25px', marginTop: '64px' }}>
        <div className="site-layout-content">
          <Title level={2}>Необходимые файлы</Title>
          <Title level={3}>Расписание ВолгГТУ</Title>
          <Text>C сайта ВУЗа</Text>
          <div style={{ display: 'flex', marginBottom: 20 }}>
            <DownloadButton />  {/* Кнопка скачивания */}
          </div>
          <Title level={3}>Список студентов</Title>
          <div style={{ display: 'flex' }}>
            <UploadButton />    {/* Кнопка загрузки */}
          </div>
        </div>
      </Content>
    </Layout>
  );
};

export default App;
