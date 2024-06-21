import React, { useState, useEffect } from 'react';
import { PlayCircleOutlined, LoadingOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { Button, Steps, notification } from 'antd';
import '../ParserButton.css';

const { Step } = Steps;

const OthersGroupMakerButton = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [stepStatus, setStepStatus] = useState('process');

  useEffect(() => {
    fetch('/api/group_maker_for_others_progress')
      .then(response => response.json())
      .then(data => {
        setCurrentStep(data.group_maker_for_others_progress);
        if (data.group_maker_for_others_progress === 4) {
          setStepStatus('finish');
        } else if (data.group_maker_for_others_progress > 0) {
          setStepStatus('process');
        } else {
          setStepStatus('wait');
        }
      });
  }, []);

  const handleClick = () => {
    const eventSource = new EventSource('/api/run_group_maker_for_others');

    setCurrentStep(1); // Начат запуск парсера
    setStepStatus('process');

    eventSource.onmessage = function(event) {
      console.log('Received:', event.data);

      if (event.data === 'Создаются группы и расписание для ВолгГТУ...') {
        setCurrentStep(1);
      } else if (event.data === 'Группы и расписание для ВолгГТУ созданы.') {
        setCurrentStep(4);
        notification.success({
          message: 'Успешно',
          description: 'Группы и расписание для ВолгГТУ созданы!',
          placement: 'topLeft',
        });
        setStepStatus('finish');
        eventSource.close();
      } else if (event.data === 'Ошибка при создании групп и расписания для ВолгГТУ.') {
        setStepStatus('error');
        eventSource.close();
      }
    };

    eventSource.onerror = function() {
      console.error('EventSource failed.');
      notification.error({
        message: 'Ошибка',
        description: 'Произошла ошибка при выполнении парсера',
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
      <Button icon={<PlayCircleOutlined />} onClick={handleClick} style={{ marginRight: 20 }}>Создать группы ЦК</Button>
      <Steps current={currentStep} status={stepStatus} className="custom-steps">
        <Step title="Ожидание запроса" icon={getIcon(0)} />
        <Step title="Создание групп и расписания" icon={getIcon(1)} />
        <Step title="Списки групп и расписание созданы" icon={getIcon(2)} />
      </Steps>
    </div>
  );
};

export default OthersGroupMakerButton;
