import React from 'react';
import styles from './SavePage.module.css'; // 또는 적절한 스타일 모듈 경로

const DownloadButton = ({ planId, disabled = false }) => {
  const handleDownload = () => {
  if (!planId || planId === 'undefined') {
    alert("다운로드할 일정을 선택하세요.");
    return;
  }

  const url = `http://localhost:8000/api/download_plan_pdf?plan_id=${planId}`;
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'travel_plan.pdf');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

  return (
    <button
      onClick={handleDownload}
      disabled={disabled}
      className={styles.showplanButton}
    >
      📄 일정 PDF 다운로드
    </button>
  );
};

export default DownloadButton;
