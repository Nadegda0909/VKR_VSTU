import React from 'react';
import { Typography } from 'antd';
import DownloadExcelRaspFile from "./DownloadExcelRaspFile";
import DownloadExcelGroupFile from "./DownloadExcelGroupFile";

const { Title, Text } = Typography;

const DownloadPage = () => {
  return (
    <div className="site-layout-content">
        <Title level={2}>Скачивание файлов</Title>
        <Title level={3}>Группы цифровой кафедры</Title>
        <DownloadExcelGroupFile />
        <Title level={3}>Расписание цифровой кафедры</Title>
        <DownloadExcelRaspFile />
    </div>
  );
};

export default DownloadPage;
