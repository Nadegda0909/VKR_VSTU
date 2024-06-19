import React, { useState, useEffect } from 'react';
import { Layout, Menu } from 'antd';
import { SnippetsOutlined, RiseOutlined, ClusterOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

const { Header: AntHeader } = Layout;

const items = [
  {
    label: 'Загрузка',
    key: 'upload',
    icon: <SnippetsOutlined />,
  },
  {
    label: 'Обработка',
    key: 'analyze',
    icon: <RiseOutlined />,
  },
  {
    label: 'Скачивание',
    key: 'download',
    icon: <ClusterOutlined />,
  },
];

const Header = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [current, setCurrent] = useState('upload');

  useEffect(() => {
    const path = location.pathname.substring(1);
    if (path) {
      setCurrent(path);
    } else {
      navigate('/upload');
    }
  }, [location, navigate]);

  const onClick = (e) => {
    setCurrent(e.key);
    navigate(`/${e.key}`);
  };

  return (
    <AntHeader className="header">
      <Menu onClick={onClick} selectedKeys={[current]} mode="horizontal" items={items} />
    </AntHeader>
  );
};

export default Header;
