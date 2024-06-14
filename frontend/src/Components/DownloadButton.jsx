import React from 'react';
import { UploadOutlined } from '@ant-design/icons';
import { Button, notification } from 'antd';

const DownloadButton = () => {
  const handleClick = () => {
    const eventSource = new EventSource('/api/download_rasp');

    eventSource.onmessage = function(event) {
      console.log('Received:', event.data);
      if (event.data === 'done') {
        notification.success({
          message: 'Success',
          description: 'Все файлы успешно обработаны',
          placement: 'topLeft',
        });
        eventSource.close();
      } else {
        notification.info({
          message: 'Notification',
          description: event.data,
          placement: 'topLeft',
        });
      }
    };

    eventSource.onerror = function() {
      console.error('EventSource failed.');
      eventSource.close();
    };
  };

  return (
    <Button icon={<UploadOutlined />} onClick={handleClick}>Загрузить</Button>
  );
};

export default DownloadButton;
