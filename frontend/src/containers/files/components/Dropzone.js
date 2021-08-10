import React, { useEffect, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { makeStyles } from '@material-ui/core/styles'
import ButtonList from './ButtonGroupSimple'
import { formatBytes } from 'actions/utils'

const useStyles = makeStyles(theme => ({
  root: {
    flexGrow: 1,
  },
  acceptedFiles: {
    fontSize: '12px',
    padding: '0px',
    margin: '0px',
  },
  container: {
    position: 'absolute',
    zIndex: '55',
    top: '-1px',
    background: '#f6f7fd',
    border: '1px solid #868DAA',
    borderTop: 'none',
    borderRadius: '0px 0px 5px 5px',
    padding: '20px 40px',
    margin: '0px 0px 0px 50px',
    '& .dropzone': {
      flex: "1",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      padding: "50px 20px",
      borderWidth: "2px",
      borderRadius: "2px",
      borderStyle: "dashed",
      backgroundColor: "#fff",
      margin: '10px 0px',
      color: "#bdbdbd",
      cursor: "pointer",
      outline: "none",
      transition: "border .24s ease-in-out",
      '&:focus': {
        borderColor: '#0492f2'
      },
      '& p': {
        padding: '0px',
        margin: '0px',
      }
    }
  },

}));

export default function UploadFiles(props) {
  const classes = useStyles();
  const { handleCancel, uploadFile } = props;
  const [files, setFiles] = useState([])

  const { getRootProps, getInputProps } = useDropzone({
    maxFiles: 1,
    onDrop: acceptedFiles => {
      console.log('acceptedFiles', acceptedFiles);
      setFiles(acceptedFiles.map(file => Object.assign(file, {
        preview: URL.createObjectURL(file)
      })));
    }
  });

  const removeFile = index => {
    var newFiles = [...files];
    newFiles.splice(index, 1);
    setFiles(newFiles);
  }

  const acceptedFiles = files.map((file, index) => (
    <li key={file.path}>
      {file.name} - {formatBytes(file.size)} ( <a href="#" onClick={() => removeFile(index)}><span>Remove</span></a>)
    </li>
  ));

  const handleSubmitUpload = () => {
    uploadFile(files[0])
  }

  const handleCancelUpload = () => {
    handleCancel();
  }

  const buttons = [
    {
      name: 'submit',
      icon: 'file-upload',
      label: 'Upload File To Server',
      class: 'green',
      onClick: handleSubmitUpload,
      disabled: !(files.length > 0)
    },
    {
      name: 'submit',
      icon: 'times',
      label: 'Cancel',
      type: 'link',
      onClick: handleCancelUpload
    }
  ];

  useEffect(() => () => {
    // Make sure to revoke the data uris to avoid memory leaks
    files.forEach(file => URL.revokeObjectURL(file.preview));
  }, [files]);

  return (
    <section className={classes.container} >
      <div {...getRootProps({ className: 'dropzone' })}>
        <input {...getInputProps()} />
        <p>Drag a file here, or click to select file</p>
      </div>
      <ul className={classes.acceptedFiles}>
        {acceptedFiles}
      </ul>
      <ButtonList buttons={buttons} />
    </section>
  );
}