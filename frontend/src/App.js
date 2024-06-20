import React, { useState, useEffect } from 'react';
import { Layout } from 'antd';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './Components/Header';
import Login from './Components/Login';
import UploadPage from './Pages/UploadPage';
import AnalyzePage from './Pages/AnalyzePage';
import DownloadPage from './Pages/DownloadPage';
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

  const handleLogin = (values) => {
    console.log('Logged in with values:', values);
    setAuthenticated(true);
  };

  if (!authenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <Router>
      <Layout className="layout">
        <Header />
        <Content style={{ padding: '0 25px', marginTop: '64px' }}>
          <Routes>
            <Route path="/" element={<Navigate to="/upload" />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/analyze" element={<AnalyzePage />} />
            <Route path="/download" element={<DownloadPage />} />
          </Routes>
        </Content>
      </Layout>
    </Router>
  );
};

export default App;
