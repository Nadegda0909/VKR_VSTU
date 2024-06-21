import React, { useState, useEffect } from 'react';
import { PlayCircleOutlined, LoadingOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { Button, Steps, notification } from 'antd';
import '../ParserButton.css';

const { Step } = Steps;

const ParserButton = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [stepStatus, setStepStatus] = useState('process');

  useEffect(() => {
    fetch('/api/parser_progress')
      .then(response => response.json())
      .then(data => {
        setCurrentStep(data.parser_progress);
        if (data.parser_progress === 4) {
          setStepStatus('finish');
        } else if (data.parser_progress > 0) {
          setStepStatus('process');
        } else {
          setStepStatus('wait');
        }
      });
  }, []);

  const handleClick = () => {
    const eventSource = new EventSource('/api/run_parser');

    setCurrentStep(1); // Начат запуск парсера
    setStepStatus('process');

    eventSource.onmessage = function(event) {
      console.log('Received:', event.data);

      if (event.data === 'Запуск парсера...') {
        setCurrentStep(1);
      } else if (event.data === 'Парсер успешно завершен.') {
        setCurrentStep(4);
        notification.success({
          message: 'Успешно',
          description: 'Расписание ВолгГТУ обработано!',
          placement: 'topLeft',
        });
        setStepStatus('finish');
        eventSource.close();
      } else if (event.data === 'Ошибка при выполнении парсера.') {
        setStepStatus('error');
        eventSource.close();
      }
    };

    eventSource.onerror = function() {
      console.error('EventSource failed.');
      notification.error({
        message: 'Ошибка',
        description: 'Произошла ошибка при обработке расписания',
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
      <Button icon={<PlayCircleOutlined />} onClick={handleClick} style={{ marginRight: 20 }}>Обработать расписание ВолгГТУ</Button>
      <Steps current={currentStep} status={stepStatus} className="custom-steps">
        <Step title="Ожидание запроса" icon={getIcon(0)} />
        <Step title="Обработка расписания ВолгГТУ" icon={getIcon(1)} />
        <Step title="Расписание ВолгГТУ обработано" icon={getIcon(2)} />
      </Steps>
    </div>
  );
};

export default ParserButton;
