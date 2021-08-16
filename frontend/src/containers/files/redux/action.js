const actions = {
    GET_FILE: 'GET_FILE',
    GET_FILE_SUCCESS: 'GET_FILE_SUCCESS',
    GET_FILE_FAIL: 'GET_FILE_FAIL',
    CLEAR_UPLOAD: 'CLEAR_UPLOAD',
    UPLOADING_FILE: 'UPLOADING_FILE',
    UPLOADING_FILE_SUCCESS: 'UPLOADING_FILE_SUCCESS',
    UPLOADING_FILE_FAIL: 'UPLOADING_FILE_FAIL',
    UPDATE_PROGRESS: 'UPDATE_PROGRESS',
    UPLOAD_SPEED: 'UPLOAD_SPEED',
    UPDATE_FOLDER: 'UPDATE_FOLDER',
    MOVE_FILE: 'MOVE_FILE',
    MOVE_FILE_SUCCESS: 'MOVE_FILE_SUCCESS',
    MOVE_FILE_FAIL: 'MOVE_FILE_FAIL',
    DELETE_FILE: 'DELETE_FILE',
    DELETE_FILE_SUCCESS: 'DELETE_FILE_SUCCESS',
    DELETE_FILE_FAIL: 'DELETE_FILE_FAIL',
    EDIT_FILE: 'EDIT_FILE',
    EDIT_FILE_SUCCESS: 'EDIT_FILE_SUCCESS',
    EDIT_FILE_FAIL: 'EDIT_FILE_FAIL',
    NEW_FOLDER: 'NEW_FOLDER',
    NEW_FOLDER_SUCCESS: 'NEW_FOLDER_SUCCESS',
    NEW_FOLDER_FAIL: 'NEW_FOLDER_FAIL',
    MOVE_FOLDER: 'MOVE_FOLDER',
    MOVE_FOLDER_SUCCESS: 'MOVE_FOLDER_SUCCESS',
    MOVE_FOLDER_FAIL: 'MOVE_FOLDER_FAIL',
    DELETE_FOLDER: 'DELETE_FOLDER',
    DELETE_FOLDER_SUCCESS: 'DELETE_FOLDER_SUCCESS',
    DELETE_FOLDER_FAIL: 'DELETE_FOLDER_FAIL',
    EDIT_FOLDER: 'EDIT_FOLDER',
    EDIT_FOLDER_SUCCESS: 'EDIT_FOLDER_SUCCESS',
    EDIT_FOLDER_FAIL: 'EDIT_FOLDER_FAIL',
    GET_FOLDER_LIST: 'GET_FOLDER_LIST',
    GET_FOLDER_LIST_SUCCESS: 'GET_FOLDER_LIST_SUCCESS',
    GET_FOLDER_LIST_FAIL: 'GET_FOLDER_LIST_FAIL',
    SET_SELECTED_FILES: 'SET_SELECTED_FILES',
    SET_FILE_PREMIUM: 'SET_FILE_PREMIUM',
    SET_FILE_PREMIUM_SUCCESS: 'SET_FILE_PREMIUM_SUCCESS',
    SET_FILE_PREMIUM_FAIL: 'SET_FILE_PREMIUM_FAIL',
    getFolderList: () => {
        return {
            type: actions.GET_FOLDER_LIST,
        }
    },
    setSelectedFiles: (files) => {
        return{
            type: actions.SET_SELECTED_FILES,
            files
        }
    },
    updateFolder: (folders) => {
        return {
            type: actions.UPDATE_FOLDER,
            folders
        }
    },
    getFiles: (folder_id, offset, limit) => {
        return {
            type: actions.GET_FILE,
            folder_id, offset, limit
        }
    },
    updateProgress: (progress) => {
        return {
            type: actions.UPDATE_PROGRESS,
            progress
        }
    },
    updateSpeed: (speed) => {
        return {
            type: actions.UPLOAD_SPEED,
            speed
        }
    },
    moveFile: (file_id, folder_id) => {
        return {
            type: actions.MOVE_FILE,
            file_id, folder_id
        }
    },
    deleteFile: (file_id) => {
        return {
            type: actions.DELETE_FILE,
            file_id
        }
    },
    editFile: (file_id, file_name) => {
        return {
            type: actions.EDIT_FILE,
            file_id, file_name
        }
    },
    newFolder: (folder_name, folder_id) => {
        return {
            type: actions.NEW_FOLDER,
            folder_name, folder_id
        }
    },
    moveFolder: (folder_id, to_folder_id) => {
        return {
            type: actions.MOVE_FOLDER,
            folder_id, to_folder_id
        }
    },
    deleteFolder: (folder_id) => {
        return {
            type: actions.DELETE_FOLDER,
            folder_id
        }
    },
    editFolder: (folder_id, name) => {
        return {
            type: actions.EDIT_FOLDER,
            folder_id, name
        }
    },
    setFilePremium: (file_id, file_mode) =>{
        return {
            type: actions.SET_FILE_PREMIUM,
            file_id, file_mode
        }
    }
};

export default actions
