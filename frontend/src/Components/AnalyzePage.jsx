import React from 'react';
import { Typography } from 'antd';
import ParserButton from "./ParserButton";
const { Title } = Typography;

const AnalyzePage = () => {
  return (
    <div className="site-layout-content">
      <Title level={2}>Обработка расписания</Title>
      <ParserButton />
      <Title level={2}>Формирование</Title>
      <Title level={3}>Группы цифровой кафедры</Title>
    </div>
  );
};

export default AnalyzePage;
