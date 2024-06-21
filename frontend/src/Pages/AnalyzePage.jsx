import React from 'react';
import { Typography } from 'antd';
import ParserButton from "../Components/ParserButton";
import GroupParserButton from "../Components/GroupParserButton";
import VstuGroupMakerButton from "../Components/VstuGroupMakerButton";
import OthersGroupMakerButton from "../Components/OthersGroupMakerButton";
import RaspCreatorButton from "../Components/RaspCreatorButton";
import GroupCreatorButton from "../Components/GroupCreatorButton";
import CreateOnlyRaspVstu from "../Components/CreateOnlyRaspVstu";
import CreateOnlyRaspOthers from "../Components/CreateOnlyRaspOthers";
const { Title } = Typography;

const AnalyzePage = () => {
  return (
    <div className="site-layout-content">
      <Title level={2}>Обработка расписания</Title>
      <ParserButton />
      <Title level={3}>Формирование</Title>
      <GroupParserButton />
      <Title level={3}>Группы цифровой кафедры</Title>
      <Title level={4}>Для ВолгГТУ</Title>
      <VstuGroupMakerButton />
      <Title level={4}>Для остальных университетов</Title>
      <OthersGroupMakerButton />
      <Title level={3}>Расписание цифровой кафедры</Title>
      <Title level={4}>Для ВолгГТУ</Title>
      <CreateOnlyRaspVstu />
      <Title level={4}>Для остальных университетов</Title>
      <CreateOnlyRaspOthers />


    </div>
  );
};

export default AnalyzePage;
