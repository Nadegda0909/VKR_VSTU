import React, { useState, useEffect } from 'react';
import { Layout, Menu, Button, notification } from 'antd';
import { TableOutlined, SnippetsOutlined, RiseOutlined, ClusterOutlined } from '@ant-design/icons';
import './App.css';

const { Header, Content } = Layout;

const items = [
  {
    label: 'Файлы',
    key: 'files',
    icon: <SnippetsOutlined />,
  },
  {
    label: 'Анализ',
    key: 'analyze',
    icon: <RiseOutlined />,
  },
  {
    label: 'Направления',
    key: 'napravlen',
    icon: <ClusterOutlined />,
  },
  {
    label: 'Расписания',
    key: 'raspis',
    icon: <TableOutlined />,
  },
];

const App = () => {
  const [current, setCurrent] = useState('files');
  const onClick = (e) => {
    console.log('click ', e);
    setCurrent(e.key);
  };

  return (
    <Layout className="layout">
      <Header className="header">
        <Menu onClick={onClick} selectedKeys={[current]} mode="horizontal" items={items} />
      </Header>
      <Content style={{ padding: '0 25px', textAlign: 'center', marginTop: '64px' }}>
        <div className="site-layout-content">
          <h1>Дипломная работа!</h1>
          <p>Loading...</p>
          <Button type="primary">Click Me</Button>
        </div>
      </Content>
    </Layout>
  );
};

export default App;
