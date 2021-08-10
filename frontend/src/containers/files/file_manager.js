import React, { useState, useEffect, useRef } from 'react'
import moment from 'moment'

import { useSelector, useDispatch } from 'react-redux'
import actions from './redux/action'
import { fetchApi } from 'actions/api'
import { Base64, reverse, generateEncryptionKey } from './utils/index'
import Resumable from './utils/resumable'
import CryptoJS from 'crypto-js'
import { Paper, Grid, Box, Collapse } from '@material-ui/core/'
import { makeStyles } from '@material-ui/core/styles'
import FolderBar from './components/FolderBar'
import TopBar from './components/TopBar'
import ContainerBar from './components/ContainerBar'
import PopupDialog from './components/PopupDialog'
import { convertDate, formatBytes } from 'actions/utils'
import PerfectScrollbar from 'react-perfect-scrollbar'
import '../../assets/css/PerfectScroll.css'

const { getFiles, updateFolder, updateProgress, updateSpeed, editFile, editFolder, newFolder,
    setSelectedFiles, deleteFile, deleteFolder, moveFile, moveFolder, getFolderList, setFilePremium } = actions

const useStyles = makeStyles(theme => ({
    root: {
        flexGrow: 1,
    },
    folderSide: {
        flexGrow: 1,
        background: '#f9fafc',
        borderRight: '1px solid #E9eef9'
    },
    paper: {
        padding: theme.spacing(2),
        textAlign: 'center',
        color: theme.palette.text.secondary,
    },
    fmMinimized: {

    },
    fmExpanded: {
        position: "fixed",
        top: '0',
        left: '0',
        height: '100%',
        width: '100%',
        zIndex: '999',
        padding: '20px',
        background: 'rgba(255, 255, 255, 0.7)'
    },
    containerWrapper: {
        position: 'relative'
    },
    infoMessages: {
        position: 'absolute',
        width: '100%',
        bottom: '0',
        left: '0',
        padding: '10px 20px',
        fontSize: '13px',
        background: '#fff',
        textAlign: 'center',
        borderTop: '1px solid #E9eef9'
    },
}))

const Page = ({ }) => {
    const dispatch = useDispatch()
    const currentFilesAndFolders = useSelector(state => state.file.currentFilesAndFolders)
    const foldersList = useSelector(state => state.file.foldersList)
    const folder = useSelector(state => state.file.currentFolder)
    const selectedFiles = useSelector(state => state.file.selectedFiles)
    const fetching = useSelector(state => state.file.fetching)
    const [isloading, setLoading] = React.useState(false)
    const [messagesList, setMessages] = useState([])
    const [uploadBox, setuploadBox] = React.useState(false)
    const fileUploader = useRef()
    const currentFolder = folder ? folder : ''
    const classes = useStyles()
    const selecMessages = selectedFiles.length > 0

    const [popupData, setPopup] = useState({
        open: false,
    })

    useEffect(() => {
        dispatch(getFiles(currentFolder, 0, 50))
        dispatch(getFolderList())

        return () => { }
    }, [])

    const handleClose = () => {
        setPopup({
            open: false
        });
    };

    const handleClickPopupOpen = (data) => {
        setPopup({
            ...data,
            open: true,
        });
    }

    const operations = {

        handleAddSelected: (path) => {
            let temp = selectedFiles ? [...selectedFiles] : []
            const filter = temp.filter(item => item.id == path.id)
            if (filter && filter.length > 0) {
                const index = temp.indexOf(filter[0])
                temp.splice(index, 1)
            } else {
                temp.push(path)
            }
            dispatch(setSelectedFiles(temp))
        },

        handleUnsetSelected: () => {
            dispatch(setSelectedFiles([]))
        },

        handleSelectAll: () => {
            let temp = []
            currentFilesAndFolders.map((item) => {
                if (!item.isDir) {
                    temp.push(item)
                }
            })
            dispatch(setSelectedFiles(temp))
        },

        handleGotoParent: () => {
        },

        handleSetMainFolder: (value, history = false) => {
            console.log({ value, history })
            dispatch(updateFolder(value))
        },

        handleDelete: () => {
            let folders = []
            let files = []
            if (selectedFiles) {
                selectedFiles.map((item) => {
                    if (item.isDir) {
                        folders.push(item.id)
                    } else {
                        files.push(item.id)
                    }
                })
            }

            const handleDeleteSubmit = () => {
                setPopup({
                    open: false
                });
                if (files.length > 0)
                    dispatch(deleteFile(files))
                if (folders.length > 0)
                    dispatch(deleteFolder(folders))

                dispatch(setSelectedFiles([]))
            }

            handleClickPopupOpen({
                title: `Deleting selected files and folders: ${selectedFiles.length} items `,
                description: `All selected files and folder will remove without recover`,
                handleClose: handleClose,
                handleSubmit: handleDeleteSubmit,
                nameInputSets: {}
            });
        },

        handleNewFolder: () => {
            var folderName = 'newfolder';
            const handleNewFolderChange = value => {
                folderName = value;
            }
            const handleNewFolderSubmit = () => {
                setPopup({
                    open: false
                });
                dispatch(newFolder(folderName, currentFolder))
            }

            handleClickPopupOpen({
                title: `Creating new folder`,
                description: 'Dont use spaces, localised symbols or emojies. This can affect problems',
                handleClose: handleClose,
                handleSubmit: handleNewFolderSubmit,
                nameInputSets: {
                    label: 'Folder Name',
                    value: folderName,
                    callBack: handleNewFolderChange,
                }
            });
        },

        handleRename: () => {
            var item = selectedFiles[0];
            var renameTxt = item.name;
            const handleRenameChange = value => {
                renameTxt = value;
            }
            const handleRenameSubmit = () => {
                setPopup({
                    open: false
                });
                if (item.isDir) {
                    dispatch(editFolder(item.id, renameTxt))
                } else {
                    dispatch(editFile(item.id, renameTxt))
                }
                dispatch(setSelectedFiles([]))
            }

            handleClickPopupOpen({
                title: `Renaming of ${item.name}`,
                handleClose: handleClose,
                handleSubmit: handleRenameSubmit,
                nameInputSets: {
                    label: 'Folder Name',
                    value: renameTxt,
                    callBack: handleRenameChange,
                }
            });
        },

        handleReload: () => {
            setLoading(true);
            setMessages([{
                title: `Wait While Reloading`,
                type: 'info',
                message: '',
                progress: true,
                disableClose: true
            }]);
            dispatch(getFiles(currentFolder, 0, 50))
            dispatch(getFolderList())
            setTimeout(() => {
                setLoading(false)
                setMessages([])
            }, 500)
        },

        handleUpload: () => {
            setuploadBox(!uploadBox);
            setLoading(!isloading);
        },

        handleDownload: () => {
            let file = selectedFiles[0];

            const file_id = file.id
            fetchApi('get', 'clapi/file/getLink/', { file_id })
                .then((data) => {
                    console.log(data)
                    if (data.download_url_no_filename_list && data.download_url_no_filename_list.length > 0) {
                        window.open(data.download_url_no_filename_list[0], '_blank')
                    }
                })
                .catch((error) => {
                    console.log({ error })
                    alert('Cannot get download link')
                })
        },

        handleViewChange: (type) => {
            // props.listViewChange(type);
        },

        handleDragEnd: (result) => {
            console.log({ result })
            setLoading(!isloading);
            try {
                let destination;
                if (result.source && result.destination && result.destination.droppableId != 'listDroppablContainer') {
                    let folder_id = result.destination.droppableId
                    destination = result.draggableId
                    if(destination.indexOf('file-') >= 0){
                        dispatch(moveFile([destination], folder_id))
                    } else {
                        dispatch(moveFolder([destination.replace('file-', '')], folder_id))
                    }
                }

                setMessages([{
                    title: `File Successfully Moved`,
                    type: 'success',
                    message: 'File that you dragged successfully moved',
                    timer: 3000,
                }])

            } catch (error) {

            }
            setLoading(!isloading);
        },

        handleSetPremium: () => {
            let file = selectedFiles[0]
            const file_mode = file.file_mode == 0 ? 1 : 0
            
            dispatch(setFilePremium(file.id, file_mode))
        }
    }

    const handleUploaded = () => {
        setuploadBox(false)
        setLoading(false)
    }

    const openDownloadFile = (file) => {
        const file_id = file.id
        fetchApi('get', 'clapi/file/getLink/', { file_id })
            .then((data) => {
                console.log(data)
                if (data.download_url_no_filename_list && data.download_url_no_filename_list.length > 0) {
                    window.open(data.download_url_no_filename_list[0], '_blank')
                }
            })
            .catch((error) => {
                console.log({ error })
                alert('Cannot get download link')
            })
    }

    const allButtons = {
        delete: {
            title: 'Delete',
            icon: 'trash',
            onClick: operations.handleDelete,
            disable: !(selectedFiles.length > 0)
        },
        rename: {
            title: 'Rename',
            icon: 'edit',
            onClick: operations.handleRename,
            disable: !(selectedFiles.length === 1)

        },
        newFolder: {
            title: 'New Folder',
            icon: 'folder-plus',
            onClick: operations.handleNewFolder,
        },
        goParent: {
            title: 'Go to parent folder',
            icon: 'level-up-alt',
            onClick: operations.handleGotoParent,
            // disable: props.selectedFolder === props.foldersList.path
        },
        selectAll: {
            title: 'Select all',
            icon: 'check-double',
            onClick: operations.handleSelectAll,
            // disable: !(selectedFiles.length !== props.filesList.length)
        },
        selectNone: {
            title: 'Select none',
            icon: 'minus-square',
            onClick: operations.handleUnsetSelected,
            disable: (selectedFiles.length === 0)
        },
        selectFile: {
            title: 'Select file',
            icon: 'check',
            onClick: operations.handleReturnCallBack,
            // disable: typeof selectCallback === 'undefined'
        },
        reload: {
            title: 'Reload',
            icon: 'sync',
            onClick: operations.handleReload,
        },
        uploadFile: {
            title: 'Upload Files',
            icon: 'file-upload',
            onClick: operations.handleUpload,
        },
        searchFile: {
            title: 'Search File',
            icon: 'search',
            onClick: operations.handleSearchFile,
        },
        download: {
            title: 'Download File',
            icon: 'file-download',
            onClick: operations.handleDownload,
            disable: selectedFiles.length > 1
        },
        gridView: {
            title: 'Grid view',
            icon: 'th',
            onClick: () => operations.handleViewChange('grid'),
            // disable: props.itemsView === 'grid'
        },
        listView: {
            title: 'List View',
            icon: 'bars',
            onClick: () => operations.handleViewChange('list'),
            // disable: props.itemsView === 'list'
        },
        setPremium: {
            title: 'Set / Unset Premium File',
            icon: 'wallet',
            onClick: operations.handleSetPremium,
            disable: selectedFiles.length > 1
        },
        cut: {
            title: 'Cut',
            icon: 'cut',
            onClick: operations.handleCut,
            // disable: !(props.selectedFiles.length > 0)
        },
        paste: {
            title: 'Paste',
            icon: 'paste',
            onClick: operations.handlePaste,
            // disable: !(props.bufferedItems.files.length > 0)
        },
    }

    const aviableButtons = {
        topbar: [
            [allButtons.goParent],
            [allButtons.newFolder, allButtons.uploadFile, allButtons.reload, allButtons.download],
            [allButtons.delete, allButtons.rename],
            [allButtons.selectNone, allButtons.selectAll],
            [allButtons.gridView, allButtons.listView],
        ],

        file: [
            [allButtons.cut, allButtons.paste, allButtons.rename, allButtons.download, allButtons.setPremium, allButtons.delete]
        ],
        container: [
            [allButtons.cut, allButtons.paste, allButtons.rename, allButtons.delete]
        ],
    }

    return (
        <div>
            <div className={classes.fmMinimized}>
                <Paper>
                    {popupData.open && <PopupDialog {...popupData} />}
                    <Grid container>
                        <Grid item xs={3} sm={2} className={classes.folderSide}>
                            <PerfectScrollbar>
                                <div style={{ maxHeight: '70vh' }}>
                                    <FolderBar foldersList={foldersList} onFolderClick={operations.handleSetMainFolder} selectedFolder={currentFolder} />
                                </div>
                            </PerfectScrollbar>
                        </Grid>
                        <Grid className={classes.containerWrapper} item xs={9} sm={10}>
                            <TopBar buttons={aviableButtons} />
                            <PerfectScrollbar>
                                <div style={{ maxHeight: '70vh' }}>
                                    <ContainerBar buttons={aviableButtons} messages={messagesList} isloading={isloading} uploadBox={uploadBox} operations={operations} handleUploaded={handleUploaded} />
                                </div>
                            </PerfectScrollbar>
                            <Collapse in={selecMessages}>
                                <Box className={classes.infoMessages}>
                                    {selectedFiles.length > 0 && <div className="text"><b>{selectedFiles.length}</b> items are selected</div>}
                                </Box>
                            </Collapse>
                        </Grid>
                    </Grid>
                </Paper>
            </div>
        </div>
    )
}

export default Page

const customStyles = {
    content: {
        top: '50%',
        left: '50%',
        right: 'auto',
        bottom: 'auto',
        marginRight: '-50%',
        transform: 'translate(-50%, -50%)',
        width: '560px',
        border: 'none',
        backgroundColor: 'transparent'
    },
}