import React from 'react';
import { DownloadOutlined } from '@ant-design/icons';
import { Button, notification } from 'antd';
import axios from "axios";


const DownloadExcelGroupFile = () => {
  const handleDownload = async () => {
    try {
      const response = await axios.get('/api/download_group_file', {
        responseType: 'blob', // важный момент для корректной обработки бинарного содержимого файла
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'group_ck.xlsx'); // Укажите имя файла здесь
      document.body.appendChild(link);
      link.click();

      notification.success({
        message: 'Успешно',
        description: 'Файл успешно скачан!',
        placement: 'topLeft',
      });
    } catch (error) {
      console.error('Download failed:', error);
      notification.error({
        message: 'Ошибка',
        description: 'Произошла ошибка при скачивании файла',
        placement: 'topLeft',
      });
    }
  };

  return (
      <Button icon={<DownloadOutlined />} onClick={handleDownload}>Скачать файл</Button>
  );
};

export default DownloadExcelGroupFile;
