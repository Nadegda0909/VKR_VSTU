import React from 'react';
import { Button } from 'antd';

const DownloadButton = () => {
  const handleClick = () => {

    fetch('/api/download_rasp', { method: 'POST' })
      .then(response => response.json())
      .then(data => console.log(data));
  };

  return (
    <Button type="primary" onClick={handleClick}>Загрузить</Button>
  );
};

export default DownloadButton;
