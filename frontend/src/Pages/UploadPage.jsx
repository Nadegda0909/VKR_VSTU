import React from 'react';
import UploadButton from '../Components/UploadButton';
import { Typography } from 'antd';
import DownloadButton from "../Components/DownloadButton";

const { Title, Text } = Typography;

const UploadPage = () => {
  return (
    <div className="site-layout-content">
      <Title level={2}>Необходимые файлы</Title>
      <Title level={3}>Расписание ВолгГТУ</Title>
      <Text>C сайта ВУЗа</Text>
      <p></p>
      <div style={{ display: 'flex', marginBottom: 20 }}>
        <DownloadButton />
      </div>
      <Title level={3}>Список студентов</Title>
      <div style={{ display: 'flex' }}>
        <UploadButton />
      </div>
    </div>
  );
};

export default UploadPage;
