import React, { useState, useEffect } from 'react';
import { UploadOutlined, LoadingOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { Button, Steps, notification } from 'antd';
import '../DownloadButton.css';  // Импортируем стили

const { Step } = Steps;

const DownloadButton = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [stepStatus, setStepStatus] = useState('process');

  useEffect(() => {
    fetch('/api/progress')
      .then(response => response.json())
      .then(data => {
        setCurrentStep(data.progress);
        if (data.progress === 4) {
          setStepStatus('finish');
        } else if (data.progress > 0) {
          setStepStatus('process');
        } else {
          setStepStatus('wait');
        }
      });
  }, []);

  const handleClick = () => {
    const eventSource = new EventSource('/api/download_rasp');

    setCurrentStep(1); // Начато скачивание
    setStepStatus('process');

    eventSource.onmessage = function(event) {
      console.log('Received:', event.data);

      if (event.data === 'Скачивание файлов началось...') {
        setCurrentStep(1);
      } else if (event.data === 'Файлы скачаны.') {
        setCurrentStep(2);
      } else if (event.data === 'Конвертация файлов началась...') {
        setCurrentStep(2);
      } else if (event.data === 'Файлы конвертированы.') {
        setCurrentStep(4);
      } else if (event.data === 'done') {
        setCurrentStep(4);
        notification.success({
          message: 'Успешно',
          description: 'Все файлы скачаны и конвертированы!',
          placement: 'topLeft',
        });
        setStepStatus('finish');
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
      setStepStatus('error');
      eventSource.close();
    };
  };

  const getIcon = (step) => {
    if (step < currentStep) return <CheckOutlined />;
    if (step === currentStep && stepStatus === 'process') return <LoadingOutlined />;
    if (stepStatus === 'error') return <CloseOutlined />;
    return null;
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <Button icon={<UploadOutlined />} onClick={handleClick} style={{ marginRight: 20 }}>Загрузить</Button>
      <Steps current={currentStep} status={stepStatus} className="custom-steps">
        <Step title="Ожидание запроса" icon={getIcon(0)} />
        <Step title="Скачивание" icon={getIcon(1)} />
        <Step title="Конвертация" icon={getIcon(2)} />
        <Step title="Все файлы скачаны и конвертированы" icon={getIcon(3)} />
      </Steps>
    </div>
  );
};

export default DownloadButton;
