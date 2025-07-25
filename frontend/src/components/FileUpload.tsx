import React, { useRef, useState } from 'react';
import { config } from '../config';

type FileUploadProps = {
  onUpload: (text: string, pages: Array<{ page: number; text: string }>) => void;
};

const FileUpload: React.FC<FileUploadProps> = ({ onUpload }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await processFile(file);
  };

  const processFile = async (file: File) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${config.API.AUDIT}/uploadandaudit`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      onUpload(data.text, data.pages);
    } catch (error) {
      console.error('File upload failed:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div>
      <div 
        className={`upload-area ${isDragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <div className="upload-text">
          {isUploading ? (
            'Processing your document...'
          ) : (
            <>
              📄 <strong>Click to upload</strong> or drag and drop your document here
              <br />
              <span style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                Supports PDF and DOCX files
              </span>
            </>
          )}
        </div>
        <input
          type="file"
          accept=".pdf,.docx"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
      </div>
    </div>
  );
};

export default FileUpload; 