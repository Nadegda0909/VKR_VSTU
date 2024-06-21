import React, { useState, useEffect } from 'react';
import { UploadOutlined, LoadingOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { Button, Upload, Steps, notification } from 'antd';
import axios from 'axios';

const { Step } = Steps;

const UploadCkStudentsButton = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [stepStatus, setStepStatus] = useState('process');

  useEffect(() => {
    fetch('/api/progress_upload')
      .then(response => response.json())
      .then(data => {
        setCurrentStep(data.progress);
        if (data.progress === 2) {
          setStepStatus('finish');
        } else if (data.progress === 1) {
          setStepStatus('process');
        } else {
          setStepStatus('wait');
        }
      });
  }, []);

  const handleUpload = async (info) => {
    setCurrentStep(1); // Начато чтение файла
    setStepStatus('process');
    const formData = new FormData();
    formData.append('file', info.file);

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.status === 200) {
        const eventSource = new EventSource('/api/upload_progress');
        eventSource.onmessage = function(event) {
          console.log('Received:', event.data);

          if (event.data === 'Файл загружен') {
            setCurrentStep(2);
            notification.success({
              message: 'Успешно',
              description: 'Файл успешно загружен!',
              placement: 'topLeft',
            });
            setStepStatus('finish');
            eventSource.close();
          } else {
            setCurrentStep(1);
          }
        };

        eventSource.onerror = function() {
          console.error('EventSource failed.');
          notification.error({
            message: 'Ошибка',
            description: 'Произошла ошибка при загрузке файла',
            placement: 'topLeft',
          });
          setStepStatus('error');
          eventSource.close();
        };
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Upload failed:', error);
      notification.error({
        message: 'Ошибка',
        description: 'Произошла ошибка при загрузке файла',
        placement: 'topLeft',
      });
      setStepStatus('error');
    }
  };

  const getIcon = (step) => {
    if (step < currentStep) return <CheckOutlined />;
    if (step === currentStep && stepStatus === 'process') return <LoadingOutlined />;
    if (stepStatus === 'error') return <CloseOutlined />;
    return null;
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <Upload customRequest={handleUpload} showUploadList={false} accept=".csv">
        <Button icon={<UploadOutlined />}>Загрузить CSV</Button>
      </Upload>
      <Steps current={currentStep} status={stepStatus} style={{ marginLeft: 20 }}>
        <Step title="Ожидание загрузки" icon={getIcon(0)} />
        <Step title="Загрузка файла" icon={getIcon(1)} />
        <Step title="Файл загружен" icon={getIcon(2)} />
      </Steps>
    </div>
  );
};

export default UploadCkStudentsButton;
