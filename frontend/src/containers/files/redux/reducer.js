import actions from './action'
import { TransactionTypeFilter } from 'actions/constants'

const initState = {
    currentFolder: [''],
    currentFilesAndFolders: null,
    foldersList: {},
    uploadProgress: 0,
    currentUpload: null,
    uploadSpeed: "0 KB/s (0%)",
    fetching: false,
    selectedFiles: [],
    bufferedItems: null
};

export default function appReducer(state = initState, action) {
    console.log( action )
    switch (action.type) {
        case actions.SET_SELECTED_FILES:
            return { ...state, selectedFiles: action.files};
        case actions.UPDATE_FOLDER:
            return { ...state, currentFolder: action.folders, fetching: false };
        case actions.GET_FILE:
            return { ...state, currentFilesAndFolders: null, fetching: false };
        case actions.GET_FILE_SUCCESS:
            return { ...state, currentFilesAndFolders: action.data, fetching: false };
        case actions.CLEAR_UPLOAD:
            return { ...state, uploadProgress: 0, currentUpload: null, uploadSpeed: 0, fetching: false }
        case actions.UPDATE_PROGRESS:
            return { ...state, uploadProgress: action.progress, fetching: false }
        case actions.UPLOAD_SPEED:
            return { ...state, uploadSpeed: action.speed, fetching: false }
        case actions.GET_FOLDER_LIST_SUCCESS:
            return { ...state, foldersList: action.data, fetching: false }
        case actions.UPLOADING_FILE:
        case actions.MOVE_FILE:
        case actions.DELETE_FILE:
        case actions.DELETE_FOLDER:
        case actions.EDIT_FILE:
        case actions.EDIT_FOLDER:
        case actions.NEW_FOLDER:
            return { ...state, fetching: true }
        case actions.MOVE_FILE_SUCCESS:
        case actions.DELETE_FILE_SUCCESS:
        case actions.DELETE_FOLDER_SUCCESS:
        case actions.EDIT_FILE_SUCCESS:
        case actions.EDIT_FOLDER_SUCCESS:
        case actions.NEW_FOLDER_SUCCESS:
            return { ...state, fetching: false }
        case actions.UPLOADING_FILE_FAIL:
        case actions.MOVE_FILE_FAIL:
        case actions.DELETE_FILE_FAIL:
        case actions.DELETE_FOLDER_FAIL:
        case actions.EDIT_FILE_FAIL:
        case actions.EDIT_FOLDER_FAIL:
        case actions.NEW_FOLDER_FAIL:
            return { ...state, fetching: false }
        default:
            return state
    }
}
