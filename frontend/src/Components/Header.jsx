import React, { useState } from 'react';
import { Layout, Menu } from 'antd';
import { TableOutlined, SnippetsOutlined, RiseOutlined, ClusterOutlined } from '@ant-design/icons';

const { Header: AntHeader } = Layout;

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

const Header = () => {
  const [current, setCurrent] = useState('files');
  const onClick = (e) => {
    console.log('click ', e);
    setCurrent(e.key);
  };

  return (
    <AntHeader className="header">
      <Menu onClick={onClick} selectedKeys={[current]} mode="horizontal" items={items} />
    </AntHeader>
  );
};

export default Header;
