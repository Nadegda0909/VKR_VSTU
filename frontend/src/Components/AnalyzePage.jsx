import React from 'react';
import { Typography } from 'antd';
import ParserButton from "./ParserButton";
import GroupParserButton from "./GroupParserButton";
import VstuGroupMakerButton from "./VstuGroupMakerButton";
import OthersGroupMakerButton from "./OthersGroupMakerButton";
import RaspCreatorButton from "./RaspCreatorButton";
import GroupCreatorButton from "./GroupCreatorButton";
const { Title } = Typography;

const AnalyzePage = () => {
  return (
    <div className="site-layout-content">
      <Title level={2}>Обработка расписания</Title>
      <ParserButton />
      <Title level={2}>Формирование</Title>
      <GroupParserButton />
      <Title level={3}>Группы цифровой кафедры</Title>
      <VstuGroupMakerButton />
      <OthersGroupMakerButton />
      <Title level={3}>Сформировать Excel для групп</Title>
      <GroupCreatorButton />
      <Title level={3}>Сформировать Excel для расписания</Title>
      <RaspCreatorButton />
    </div>
  );
};

export default AnalyzePage;
