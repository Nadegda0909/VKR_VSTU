import React, { useState } from 'react';
import { UploadOutlined } from '@ant-design/icons';
import { Button, Steps, notification } from 'antd';

const { Step } = Steps;

const DownloadButton = () => {
  const [currentStep, setCurrentStep] = useState(0);

  const handleClick = () => {
    const eventSource = new EventSource('/api/download_rasp');

    setCurrentStep(1);  // Начато скачивание

    eventSource.onmessage = function(event) {
      console.log('Received:', event.data);

      if (event.data === 'Скачивание файлов началось...') {
        setCurrentStep(1);
      } else if (event.data === 'Файлы скачаны.') {
        setCurrentStep(2);
      } else if (event.data === 'Конвертация файлов началась...') {
        setCurrentStep(3);
      } else if (event.data === 'Файлы конвертированы.') {
        setCurrentStep(4);
      } else if (event.data === 'done') {
        notification.success({
          message: 'Успешно',
          description: 'Все файлы успешно обработаны',
          placement: 'topLeft',
        });
        eventSource.close();
      }
    };

    eventSource.onerror = function() {
      console.error('EventSource failed.');
      notification.error({
        message: 'Ошибка',
        description: 'Произошла ошибка при обработке файлов',
        placement: 'topLeft',
      });
      eventSource.close();
    };
  };

  return (
    <>
      <Steps current={currentStep}>
        <Step title="Ожидание запроса" />
        <Step title="Начато скачивание" />
        <Step title="Начата конвертация" />
        <Step title="Все закончено успешно" />
      </Steps>
      <Button icon={<UploadOutlined />} onClick={handleClick} style={{ marginTop: 20 }}>Загрузить</Button>
    </>
  );
};

export default DownloadButton;
