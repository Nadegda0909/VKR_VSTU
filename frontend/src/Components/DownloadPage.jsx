import React from 'react';
import { Typography } from 'antd';

const { Title, Text } = Typography;

const DownloadPage = () => {
  return (
    <div className="site-layout-content">
        <Title level={2}>Скачивание файлов</Title>
        <Title level={3}>Группы цифровой кафедры</Title>
        <Title level={3}>Расписание цифровой кафедры</Title>
    </div>
  );
};

export default DownloadPage;
