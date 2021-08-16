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

