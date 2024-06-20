import React from 'react';
import {Typography} from 'antd';
import DownloadExcelRaspFile from "../Components/DownloadExcelRaspFile";
import DownloadExcelGroupFile from "../Components/DownloadExcelGroupFile";
import GroupCreatorButton from "../Components/GroupCreatorButton";
import RaspCreatorButton from "../Components/RaspCreatorButton";


const { Title } = Typography;

const DownloadPage = () => {
  return (
    <div className="site-layout-content">
        <Title level={2}>Скачивание файлов</Title>
        <Title level={3}>Группы цифровой кафедры</Title>
        <GroupCreatorButton />
        <p></p>
        <DownloadExcelGroupFile />
        <Title level={3}>Расписание цифровой кафедры</Title>
        <RaspCreatorButton />
        <p></p>
        <DownloadExcelRaspFile />
    </div>
  );
};

export default DownloadPage;
