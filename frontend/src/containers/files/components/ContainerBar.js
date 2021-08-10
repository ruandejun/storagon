import React, { useState } from "react"
import { useDispatch, useSelector } from 'react-redux'
import { Menu, MenuItem, Divider, Box } from '@material-ui/core'
import { DragDropContext } from 'react-beautiful-dnd'
import useStyles from './Styles'
import InfoBoxes from './InfoBoxes'
import Dropzone from './Dropzone'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

import ViewItems from './ViewItems';

import actions from '../redux/action'
import { fetchApi } from 'actions/api'
import { Base64, reverse, generateEncryptionKey } from '../utils/index'
import Resumable from '../utils/resumable'
import CryptoJS from 'crypto-js'

const { getFiles, updateProgress, updateSpeed } = actions

const contextMenuInital = {
  mouseX: null,
  mouseY: null,
  selected: null
};

const Page = (props) => {
  const { messages, operations, isloading, uploadBox, buttons, handleUploaded } = props
  const classes = useStyles();
  const [itemContext, itemContexSet] = useState(contextMenuInital);
  const [contentContex, contentContexSet] = useState(contextMenuInital);
  const currentFolder = useSelector(state => state.file.currentFolder)
  const dispatch = useDispatch()

  const handleAddSelected = value => {
    operations.handleAddSelected(value);
  };

  const handleItemContextClick = event => {
    event.stopPropagation();
    event.preventDefault();
    contentContexSet(contextMenuInital);
    itemContexSet({
      mouseX: event.clientX - 2,
      mouseY: event.clientY - 4,
    });
  };

  const handleContentContextClick = event => {
    event.stopPropagation();
    event.preventDefault();
    itemContexSet(contextMenuInital);
    contentContexSet({
      mouseX: event.clientX - 2,
      mouseY: event.clientY - 4,
    });
  };

  const handleContextClose = () => {
    itemContexSet(contextMenuInital);
    contentContexSet(contextMenuInital);
  }

  const handleUploadFile = (upload_file) => {
    console.log({upload_file})
    try {
      var r = new Resumable({
        target: '/sf/upload/34124124124/',
        chunkSize: 1 * 1024 * 1024,
        simultaneousUploads: 1,
        maxFiles: 1
      })

      r.on('fileAdded', (file) => {
        console.log({ fileAdd: file })
        var reader = new FileReader();
        var md5 = CryptoJS.algo.MD5.create();
        reader.onload = (fileEvent) => {
          md5.update(CryptoJS.lib.WordArray.create(fileEvent.target.result))
          md5.update(file.size.toString())
          var file_hash = md5.finalize().toString(CryptoJS.enc.Hex)

          r.key = generateEncryptionKey()

          fetchApi('post', 'clapi/session/createUploadSession/', {
            file_hash: file_hash,
            file_size: file.size,
            file_name: file.fileName,
            folder_id: currentFolder,
            erfk: reverse(Base64.encode(r.key))
          })
            .then((data) => {
              console.log(data)

              r.opts.target = data.upload_link;
              r.duplicated = data.duplicated;
              r.uniqueIdentifier = data.session_id;

              if (data.encryptResumeFileKey) {
                r.key = Base64.decode(data.encryptResumeFileKey);
              }

              console.log({ key: r.key })

              file.initEncryptor(r.key)
              r.readyToUpload = true
              r.upload()
            })
            .catch((error) => {
              console.log(error)
            })
        }

        reader.readAsArrayBuffer(new Blob([file.file.slice(0, 1024 * 1024), file.file.slice(-1024 * 1024)]))

        r.opts.target = '/sf/upload/123123/'

        if (file.size > 50 * 1024 * 1024) {
          r.opts.chunkSize = 10 * 1024 * 1024;

          r.opts.forceChunkSize = true;
          console.log("Set chunk size to 10MB = " + r.getOpt('chunkSize'));
          file.bootstrap();
        }

        if (r.readyToUpload) {
          r.upload();
          r.startDate = new Date();
          r.lastDate = new Date();
          r.lastProgress = 0.0;
        }
      })

      r.on('fileError', (file, message) => {
        console.log({ error: file })
        alert(message)
        r = null
      })

      r.on('fileSuccess', (file, message) => {
        console.log({ success: file })
        r = null;
        if(handleUploaded){
          handleUploaded()
        }
        dispatch(getFiles(currentFolder, 0, 50))
      })

      var progress = 0
      r.on('progress', (file, message) => {
        if (r.progress() < progress)
          return

        progress = r.progress();
        dispatch(updateProgress(progress))

        var curDate = new Date();
        var curDuration = curDate - r.lastDate;
        var incProgress = progress - r.lastProgress;
        //update ui
        var fileSize = r.getSize();
        var curSpeed = (fileSize * incProgress) / curDuration;
        var avgSpeed = (fileSize * progress) / (curDate - r.startDate);

        if (curSpeed > 0 && curDuration > 1000) {
          //change last progress
          r.lastDate = curDate;
          r.lastProgress = progress;
        }

        var correctSpeed = avgSpeed;
        if (curSpeed < avgSpeed * 1.2 && curSpeed > avgSpeed * 0.3)
          correctSpeed = curSpeed;
        if (curSpeed >= 0 && curSpeed <= avgSpeed * 0.3)
          correctSpeed = (avgSpeed + curSpeed) / 2;

        dispatch(updateSpeed(correctSpeed.toFixed(2) + " KB/s (" + (progress * 100).toFixed(1) + "%)"))
      })

      r.on('cancel', () => {
        console.log('upload cancel')
        r = null
      })

      r.addFile(upload_file)
    } catch (error) {
      console.log({ error })
    }
  }

  return (
    <Box className={classes.root}>

      <div className={classes.messagesBox}>
        {messages.map((alert, index) => <InfoBoxes key={index} alert={alert} />)}
      </div>

      {isloading &&
        <Box className={classes.loadingBlock}>
          <div className="opaOverlaw"></div>
        </Box>
      }

      {uploadBox &&
        <Dropzone currentFolder={currentFolder} handleReload={operations.handleReload} uploadFile={handleUploadFile} handleCancel={operations.handleUpload} />
      }

      <div
        className={classes.container}
        onContextMenu={handleContentContextClick}
      >
        <DragDropContext onDragEnd={operations.handleDragEnd} >

          <ViewItems
            onContextMenuClick={handleItemContextClick}
            doubleClickFile={operations.handleDownload}
            doubleClickFolder={operations.handleSetMainFolder}
            addSelect={handleAddSelected}
          />

        </DragDropContext>
      </div>


      <Menu
        keepMounted
        open={itemContext.mouseY !== null}
        className={classes.menu}
        onContextMenu={handleContextClose}
        onClose={handleContextClose}
        anchorReference="anchorPosition"
        anchorPosition={
          itemContext.mouseY !== null && itemContext.mouseX !== null
            ? { top: itemContext.mouseY, left: itemContext.mouseX }
            : undefined
        }
      >
        {buttons.file.map((buttonGroup, index) =>
          [
            buttonGroup.map((button, index) =>
              <MenuItem key={index} disabled={button.disable} className={classes.menuItem} onClick={button.onClick}>
                <FontAwesomeIcon icon={button.icon} style={{ marginRight: 5 }} />{button.title}
              </MenuItem>
            ),
            <Divider />
          ]
        )}
      </Menu>

      <Menu
        keepMounted
        open={contentContex.mouseY !== null}
        className={classes.menu}
        onContextMenu={handleContextClose}
        onClose={handleContextClose}
        anchorReference="anchorPosition"
        anchorPosition={
          contentContex.mouseY !== null && contentContex.mouseX !== null
            ? { top: contentContex.mouseY, left: contentContex.mouseX }
            : undefined
        }
      >
        {buttons.container.map((buttonGroup, index) =>
          [
            buttonGroup.map((button, index) =>
              <MenuItem key={index} disabled={button.disable} className={classes.menuItem} onClick={button.onClick}>
                <FontAwesomeIcon icon={button.icon} style={{ marginRight: 5 }} />{button.title}
              </MenuItem>
            ),
            <Divider />
          ]
        )}
      </Menu>

    </Box>
  )
}

export default Page

