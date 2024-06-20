import React, { useState, useEffect } from 'react';
import { PlayCircleOutlined, LoadingOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { Button, Steps, notification } from 'antd';
import '../ParserButton.css';

const { Step } = Steps;

const RaspCreatorButton = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [stepStatus, setStepStatus] = useState('process');

  useEffect(() => {
    fetch('/api/ck_excel_rasp_progress')
      .then(response => response.json())
      .then(data => {
        setCurrentStep(data.ck_excel_rasp_progress);
        if (data.ck_excel_rasp_progress === 4) {
          setStepStatus('finish');
        } else if (data.ck_excel_rasp_progress > 0) {
          setStepStatus('process');
        } else {
          setStepStatus('wait');
        }
      });
  }, []);

  const handleClick = () => {
    const eventSource = new EventSource('/api/run_ck_excel_rasp');

    setCurrentStep(1); // Начат запуск парсера
    setStepStatus('process');

    eventSource.onmessage = function(event) {
      console.log('Received:', event.data);

      if (event.data === 'Создается Excel-файл с расписанием...') {
        setCurrentStep(1);
      } else if (event.data === 'Excel-файл с расписанием создан.') {
        setCurrentStep(4);
        notification.success({
          message: 'Успешно',
          description: 'Excel-файл с расписанием создан!',
          placement: 'topLeft',
        });
        setStepStatus('finish');
        eventSource.close();
      } else if (event.data === 'Ошибка при создании Excel-файла расписания.') {
        setStepStatus('error');
        eventSource.close();
      }
    };

    eventSource.onerror = function() {
      console.error('EventSource failed.');
      notification.error({
        message: 'Ошибка',
        description: 'Произошла ошибка при создании Excel-файла расписания',
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
      <Button icon={<PlayCircleOutlined />} onClick={handleClick} style={{ marginRight: 20 }}>Создать группы и расписание ЦК для ВолгГТУ</Button>
      <Steps current={currentStep} status={stepStatus} className="custom-steps">
        <Step title="Ожидание запроса" icon={getIcon(0)} />
        <Step title="Создание Excel" icon={getIcon(1)} />
        <Step title="Excel-файл с расписанием создан" icon={getIcon(2)} />
      </Steps>
    </div>
  );
};

export default RaspCreatorButton;
