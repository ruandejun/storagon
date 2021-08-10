import React, { useState, useEffect, useRef } from 'react'
import moment from 'moment'

import {
    FileBrowser,
    FileContextMenu,
    FileList,
    FileNavbar,
    FileToolbar,
    ChonkyIconName,
    ChonkyActions,
    FileViewMode
} from 'chonky'

import { useSelector, useDispatch } from 'react-redux'
import actions from './redux/action'
import { fetchApi } from 'actions/api'
import { Base64, reverse, generateEncryptionKey } from './utils/index'
import Resumable from './utils/resumable'
import CryptoJS from 'crypto-js'
import Modal from 'react-modal'
import loading from '../../assets/images/loading.gif'

const { getFiles, updateFolder, updateProgress, updateSpeed, editFile, editFolder, newFolder, deleteFile, deleteFolder, moveFile, moveFolder } = actions

const Page = ({ }) => {
    const dispatch = useDispatch()
    const currentFile = useSelector(state => state.file.currentFile)
    const folder = useSelector(state => state.file.currentFolder)
    const fetching = useSelector(state => state.file.fetching)
    const fileUploader = useRef()
    const currentFolder = folder ? folder : ''
    const [createFolderModal, setCreateFolderModal] = useState(false)
    const [createFolderName, setCreateFolderName] = useState('')

    let allFiles = []
    const current_files = currentFile && currentFile.fileList ? JSON.parse(currentFile.fileList) : []
    const current_folders = currentFile && currentFile.folderList ? JSON.parse(currentFile.folderList) : []
    console.log({ currentFolder, current_files, current_folders })
    current_folders.map((item) => {
        if (item.fields && item.fields.folder_type == 1) {
            allFiles.push({ id: item.pk.toString(), name: item.fields.name, isDir: true, icon: ChonkyIconName.trash })
        } else {
            allFiles.push({ id: item.pk.toString(), name: item.fields.name, isDir: true })
        }
    })
    current_files.map((item) => {
        allFiles.push({ id: item.pk, name: item.fields.file_name })
    })

    useEffect(() => {
        dispatch(getFiles(currentFolder, 0, 50))

        return () => { }
    }, [])
    const changeCurrentFolder = (folder_id) => {
        dispatch(updateFolder(folder_id))
    }

    const onSelectedFileToUpload = (event) => {
        if (event && event.target && event.target.files) {
            var upload_file = event.target.files[0]
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
    }

    const createFolder = () => {
        if (createFolderName.length > 0) {
            dispatch(newFolder(createFolderName, currentFolder))
            setCreateFolderName('')
            closeModal()
        }
    }

    const openDownloadFile = (file) => {
        const file_id = file.id
        fetchApi('get', 'clapi/file/getLink/', {file_id})
        .then((data) => {
            console.log(data)
            if(data.download_url_no_filename_list && data.download_url_no_filename_list.length > 0){
                window.open(data.download_url_no_filename_list[0], '_blank')
            }
        })
        .catch((error) => {
            console.log({error})
            alert('Cannot get download link')
        })
    }

    const handleFileAction = data => {
        console.log({ data })
        if (data) {
            let folders = []
            let files = []
            if (data.state && data.state.selectedFiles) {
                data.state.selectedFiles.map((item) => {
                    if (item.isDir) {
                        folders.push(item.id)
                    } else {
                        files.push(item.id)
                    }
                })
            }


            switch (data.id) {
                case 'upload_files':
                    fileUploader.current.click()
                    break
                case 'create_folder':
                    setCreateFolderModal(true)
                    break
                case 'open_files':
                    if (data.payload && data.payload.targetFile && data.payload.targetFile.isDir) {
                        changeCurrentFolder(data.payload.targetFile.id)
                    }
                    if (data.payload && data.payload.targetFile && !data.payload.targetFile.isDir) {
                        openDownloadFile(data.payload.targetFile)
                    }
                    break
                case 'move_files':
                    try {
                        let folder_id = data.payload.destination.id
                        if (files.length > 0)
                            dispatch(moveFile(files, folder_id))
                        if (folders.length > 0)
                            dispatch(moveFolder(folders, folder_id))
                    } catch (error) {
                        console.log({ error })
                    }
                    break
                case 'delete_files':
                    if (files.length > 0)
                        dispatch(deleteFile(files))
                    if (folders.length > 0)
                        dispatch(deleteFolder(folders))
                    break
                default:
            }
        }
    }

    console.log({ allFiles })

    const myFileActions = [
        ChonkyActions.UploadFiles,
        ChonkyActions.DownloadFiles,
        ChonkyActions.CreateFolder,
        ChonkyActions.DeleteFiles,
    ]

    const folderChain = [{ id: '', name: 'Home' }]
    const closeModal = () => {
        setCreateFolderModal(false)
    }

    return (
        <div>
            <div
                style={{
                    height: '70vh',
                    minWidth: '320px',
                    padding: '48px',
                    backgroundColor: 'white'
                }}>
                <FileBrowser
                    files={allFiles}
                    fileActions={myFileActions}
                    onFileAction={handleFileAction}
                    folderChain={folderChain}
                    style={{ height: '100%' }}
                >
                    <FileNavbar />
                    <FileToolbar />
                    <FileList />
                    <FileContextMenu />
                </FileBrowser>
                <input type="file" id="file" ref={fileUploader} style={{ display: "none" }} onChange={onSelectedFileToUpload} />
            </div>
            <Modal
                isOpen={createFolderModal}
                onRequestClose={closeModal}
                style={customStyles}
                contentLabel="Create folder"
            >
                <div className="modal" id="newfolder" aria-labelledby="Create Folder" aria-hidden="true" role="dialog">
                    <div className="modal-dialog">
                        <div className="modal-content">
                            <div className="modal-header">
                                <button type="button" className="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                                <h4 className="modal-title">Create folder</h4>
                            </div>
                            <div className="modal-body">
                                <form>

                                    <div className="form-group">
                                        <label>Folder name
                                            <input id="dirName" className="form-control" autofocus="autofocus" value={createFolderName} onChange={(event) => setCreateFolderName(event.target.value)} />
                                        </label>
                                    </div>
                                    <div className='form-btn-group'>
                                        <button type="button">Cancel</button>
                                        <button type="button" id="newDir" onClick={createFolder}>Create</button>
                                    </div>

                                </form>
                            </div>
                            <div className="modal-footer">
                                {!!fetching && <img id="loading-image" src={loading} alt="Loading..." />}
                            </div>
                        </div>
                    </div>
                </div>
            </Modal>
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