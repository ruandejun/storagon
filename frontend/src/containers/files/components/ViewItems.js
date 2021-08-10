import React from "react";
import { connect } from 'react-redux';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Box, Checkbox, Tooltip } from '@material-ui/core'
import { Droppable, Draggable } from 'react-beautiful-dnd'
import clsx from "clsx"

import { toAbsoluteUrl, convertDate, formatBytes } from "actions/utils"
import useStyles from './Styles'
import config from './config.json'
import { useSelector } from "react-redux"

const Page = (props) => {
  const { onContextMenuClick, addSelect } = props;
  const classes = useStyles();
  const currentFilesAndFolders = useSelector(state => state.file.currentFilesAndFolders)
  const selectedFiles = useSelector(state => state.file.selectedFiles)

  const getThumb = (item) => {
    try {
      const url = typeof config.icons[item.extension] !== 'undefined' ? toAbsoluteUrl(config.icons[item.extension]) : toAbsoluteUrl(config.icons.broken)
      return url
    } catch (error) {
      return toAbsoluteUrl(config.icons.broken);
    }
  }

  const handleContextMenuClick = async (item, event) => {
    addSelect(item);
    onContextMenuClick(event);
  }

  const checkIsSelected = item => {
    return selectedFiles.includes(item);
  }

  function getStyle(style, snapshot) {
    if (!snapshot.isDraggingOver) {
      return style;
    }
    return {
      ...style,
      background: '#f00 !important',
    };
  }

  const FileItem = ({ item, index }) => {
    let isSelected = checkIsSelected(item);

    return (
      <Draggable
        draggableId={item.id}
        index={index}
        isDragDisabled={item.private}
      >
        {(provided, snapshot) => (
          <Box
            onContextMenu={(event) => handleContextMenuClick(item, event)}
            className={clsx(
              classes.itemFile,
              {
                "selected": selectedFiles.includes(item.id),
                "selectmode": selectedFiles.length > 0,
                "notDragging": !snapshot.isDragging,
                'fileCuted': false
              })
            }
            onDoubleClick={() => props.doubleClickFile(item.id)}
            ref={provided.innerRef}
            {...provided.draggableProps}
            {...provided.dragHandleProps}
          >
            {item.private &&
              <span className={`icon-lock ${classes.locked}`} /> ||
              <Checkbox className={classes.checkbox} checked={isSelected} onChange={() => addSelect(item)} value={item.id} />
            }
            <span className={classes.extension}>{item.extension}</span>

            <div className={classes.infoBox}>
              <img src={getThumb(item)} />
            </div>
            <Tooltip title={item.name}>
              <div className={classes.itemTitle}>
                <span>{item.name}</span>
              </div>
            </Tooltip>

          </Box>
        )}
      </Draggable>
    );
  }

  const FolderItem = ({ item, index }) => {
    let isSelected = checkIsSelected(item);
    return (

          <Box
            className={clsx(
              classes.itemFile,
              {
                "selected": selectedFiles.includes(item.id),
                "selectmode": selectedFiles.length > 0,
                'fileCuted': false
              })
            }
            onDoubleClick={() => props.doubleClickFolder(item.id)}
            onContextMenu={(event) => handleContextMenuClick(item, event)}
          >
            <Droppable droppableId={item.id} type="CONTAINERITEM" isCombineEnabled>
              {(provided, snapshot) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  style={getStyle(provided.droppableProps.style, snapshot)}
                >
                  {item.private &&
                    <span className={`icon-lock ${classes.locked}`} /> ||
                    <Checkbox className={classes.checkbox} checked={isSelected} onChange={() => addSelect(item)} value={item.id} />
                  }
                  <div className={classes.infoBox}>
                    <img src={snapshot.isDraggingOver ? toAbsoluteUrl(config.icons.folderopen) : toAbsoluteUrl(config.icons.folder)} />
                  </div>
                  <Tooltip title={<>
                    <b>Name :</b> {item.name} <br />
                    <b>Created :</b> {convertDate(item.created)}
                  </>
                  }>
                    <div className={classes.itemTitle}>
                      <span>{item.name}</span>
                    </div>
                  </Tooltip>
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </Box>
    )
  }

  const ListFolderItem = ({ item, index }) => {
    let isSelected = checkIsSelected(item);

    return (
      <Draggable index={index} draggableId={item.id}>
        {(provided, snapshot) => (
          <TableRow
            ref={provided.innerRef}
            className={clsx(
              classes.tableListRow,
              {
                "selected": selectedFiles.includes(item.id),
                'fileCuted': false,
                "selectmodeTable": selectedFiles.length > 0
              })
            }
            onDoubleClick={() => props.doubleClickFolder(item.id)}
            onContextMenu={(event) => handleContextMenuClick(item, event)}
            {...provided.draggableProps}
            {...provided.dragHandleProps}
          >
            <Droppable droppableId={item.id} type="CONTAINERITEM" isCombineEnabled>
              {(provided, snapshot) => (
                <>
                  <TableCell className={classes.tableCell}><Checkbox checked={isSelected} onChange={() => addSelect(item)} value={item.id} /></TableCell>
                  <TableCell className={classes.tableCell}><img style={{ "width": "20px" }} src={snapshot.isDraggingOver ? toAbsoluteUrl(config.icons.folderopen) : toAbsoluteUrl(config.icons.folder)} /></TableCell>
                  <TableCell className={classes.tableCell} align="left">
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      style={getStyle(provided.droppableProps.style, snapshot)}
                    >
                      {item.name}
                      {provided.placeholder}
                    </div>
                  </TableCell>
                  <TableCell className={classes.tableCell} align="left">{''}</TableCell>
                  <TableCell className={classes.tableCell} align="left">{''}</TableCell>
                  <TableCell className={classes.tableCell} align="left">{''}</TableCell>
                  <TableCell className={classes.tableCell} align="left">{''}</TableCell>
                  <TableCell className={classes.tableCell} align="left">{''}</TableCell>
                </>
              )}
            </Droppable>
          </TableRow>
        )}
      </Draggable>
    );
  }

  const ListFileItem = ({ item, index }) => {
    let isSelected = checkIsSelected(item);

    return (
      <Draggable
        draggableId={'file-' + item.id}
        index={index}
      >
        {(provided, snapshot) => (
          <TableRow
            onContextMenu={(event) => handleContextMenuClick(item, event)}
            className={clsx(
              classes.tableListRow,
              {
                "selected": selectedFiles.includes(item.id),
                'fileCuted': false,
                "selectmodeTable": selectedFiles.length > 0
              })
            }
            onDoubleClick={() => props.doubleClickFile(item.id)}
            ref={provided.innerRef}
            {...provided.draggableProps}
            {...provided.dragHandleProps}
          >
            <TableCell className={classes.tableCell}>
              <Checkbox checked={isSelected} onChange={() => addSelect(item)} value={item.id} />
            </TableCell>
            <TableCell className={classes.tableCell}>
              <img style={{ "width": "20px", 'maxHeight': '30px' }} src={getThumb(item)} />
            </TableCell>
            <TableCell className={classes.tableCell} align="left" style={{ color: item.file_mode == 1 ? '#E0AE10' : 'black' }}>{item.name}</TableCell>
            <TableCell className={classes.tableCell} align="center">{formatBytes(item.file_size)}</TableCell>
            <TableCell className={classes.tableCell} align="center">{convertDate(item.last_download_date)}</TableCell>
            <TableCell className={classes.tableCell} align="center">{convertDate(item.created_date)}</TableCell>
            <TableCell className={classes.tableCell} align="center">{item.download_count}</TableCell>
            <TableCell className={classes.tableCell} align="center">{item.download_count_24h}</TableCell>
          </TableRow>
        )}
      </Draggable>
    );
  }

  const ListView = () => {
    return (
      <TableContainer component={Box}>
        <Table className={classes.table} size="small" aria-label="a dense table">

          <TableHead>
            <TableRow className={classes.tableHead}>
              <TableCell style={{ "width": '20px' }}></TableCell>
              <TableCell style={{ "width": '35px' }} align="left"></TableCell>
              <TableCell align="left">Name</TableCell>
              <TableCell style={{ "width": '80px' }} align="center">Size</TableCell>
              <TableCell style={{ "width": '150px' }} align="center">Last Download Date</TableCell>
              <TableCell style={{ "width": '150px' }} align="center">Upload Date</TableCell>
              <TableCell style={{ "width": '80px' }} align="center">Total Download</TableCell>
              <TableCell style={{ "width": '80px' }} align="center">Today Download</TableCell>
            </TableRow>
          </TableHead>

          <Droppable droppableId="listDroppablContainer" type="CONTAINERITEM" isCombineEnabled>
            {(provided, snapshot) => (
              <TableBody ref={provided.innerRef} {...provided.droppableProps} >

                {currentFilesAndFolders && currentFilesAndFolders.map((item, index) => (
                  item.isDir && <ListFolderItem key={index} index={index} item={item} />
                ))}

                {currentFilesAndFolders && currentFilesAndFolders.map((item, index) => (
                  !item.isDir && <ListFileItem key={index} index={index} item={item} />
                ))}

                {provided.placeholder}
              </TableBody>
            )}
          </Droppable>

        </Table>
      </TableContainer>
    )
  }

  const GridView = () => {
    return (
      <div className={classes.itemsList}>

        <Droppable droppableId="mainDroppablContainer" type="CONTAINERITEM" isCombineEnabled>
          {(provided, snapshot) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
            >
              {currentFilesAndFolders && currentFilesAndFolders.map((item, index) => (
                item.isDir && <FolderItem key={index} index={index} item={item} />
              ))}

              {currentFilesAndFolders && currentFilesAndFolders.map((item, index) => (
                !item.isDir && <FileItem key={index} index={index} item={item} />
              ))}

              {provided.placeholder}
            </div>
          )}
        </Droppable>

      </div>
    )
  }

  return (
    <>
      {props.itemsView === 'grid' ? <GridView /> : <ListView />}
    </>
  )
}

export default Page