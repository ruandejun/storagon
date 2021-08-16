import { takeEvery, put, call, select } from 'redux-saga/effects'
import actions from './action'
import { fetchApi, fetchApiJson } from 'actions/api'

export const getCurrentFolder = (state) => state.file ? (state.file.currentFolder ? state.file.currentFolder[state.file.currentFolder.length - 1] : '') : ''
export const getFolderTree = (state) => state.file ? state.file.currentFolder : []

export function* getFolderList() {
    const folderTree = yield select(getFolderTree)
    let folders = []

    let lastChilds = []
    let lastChildParent = ''
    for (var i = folderTree.length - 1; i >= 0; i--) {
        const folder = folderTree[i]
        let response = yield call(fetchApi, 'get', 'clapi/file/listFileAndFolder/', { folder_id: folder })
        console.log({ folders: response })
        let childrens = []

        if (response) {
            const current_folders = response && response.folderList ? JSON.parse(response.folderList) : []
            current_folders.map((item) => {
                childrens.push({ id: item.pk.toString(), name: item.fields.name, isDir: true, children: lastChildParent == item.pk.toString() ? lastChilds : [], path: item.pk.toString() })
                if (folder === '') {
                    folders.push({ id: item.pk.toString(), name: item.fields.name, isDir: true, children: lastChildParent == item.pk.toString() ? lastChilds : [], path: item.pk.toString() })
                }
            })
        }

        lastChilds = childrens
        lastChildParent = folder.toString()
    }

    yield put({
        type: actions.GET_FOLDER_LIST_SUCCESS,
        data: { name: 'Cloud Storage', children: folders, path: '' }
    })
}

export function* getFiles({ folder_id, offset, limit }) {
    const folder = folder_id ? folder_id : yield select(getCurrentFolder)
    let response = yield call(fetchApi, 'get', 'clapi/file/listFileAndFolder/', limit == 0 ? { folder_id: folder } : { folder_id: folder, offset, limit })
    console.log({ files: response })

    if (response) {
        let allFiles = []
        const current_files = response && response.fileList ? JSON.parse(response.fileList) : []
        const current_folders = response && response.folderList ? JSON.parse(response.folderList) : []
        current_folders.map((item) => {
            allFiles.push({ id: item.pk.toString(), name: item.fields.name, isDir: true })
        })
        current_files.map((item) => {
            const fileDic = response && response.fileInfoDict && response.fileInfoDict[item.pk] ? response.fileInfoDict[item.pk] : {}
            allFiles.push({ id: item.pk.toString(), extension: item.fields.file_name.match(/\.[0-9a-z]+$/i)[0], name: item.fields.file_name, ...item.fields, ...fileDic })
        })

        console.log({ allFiles })

        yield put({
            type: actions.GET_FILE_SUCCESS,
            data: allFiles
        })
    } else {
        yield put({
            type: actions.GET_FILE_FAIL,
            data: []
        })
    }
}

export function* updateFolder({ folder_id }) {
    yield put({
        type: actions.GET_FILE,
        folder_id
    })
    yield put({
        type: actions.GET_FOLDER_LIST
    })
}

export function* moveFile({ file_id, folder_id }) {
    let response = yield call(fetchApi, 'post', 'clapi/file/moveFile/', { file_id, folder_id })
    console.log({ moveFile: response })

    if (response) {
        yield put({
            type: actions.MOVE_FILE_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.MOVE_FILE_FAIL,
            data: []
        })
    }

    yield put({
        type: actions.GET_FILE
    })
}

export function* deleteFile({ file_id }) {
    let response = yield call(fetchApi, 'post', 'clapi/file/deleteFile/', { file_id })
    console.log({ deleteFile: response })

    if (response) {
        yield put({
            type: actions.DELETE_FILE_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.DELETE_FILE_FAIL,
            data: []
        })
    }

    yield put({
        type: actions.GET_FILE
    })
}

export function* editFile({ file_id, file_name }) {
    let response = yield call(fetchApi, 'post', 'clapi/file/editFile/', { file_id, file_name })
    console.log({ editFile: response })

    if (response) {
        yield put({
            type: actions.EDIT_FILE_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.EDIT_FILE_FAIL,
            data: []
        })
    }

    yield put({
        type: actions.GET_FILE
    })
}

export function* newFolder({ folder_name, folder_id }) {
    let response = yield call(fetchApi, 'post', 'clapi/file/newFolder/', { folder_name, folder_id })
    console.log({ newFolder: response })

    if (response) {
        yield put({
            type: actions.NEW_FOLDER_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.NEW_FOLDER_FAIL,
            data: []
        })
    }

    yield put({
        type: actions.GET_FILE
    })
}

export function* moveFolder({ folder_id, to_folder_id }) {
    let response = yield call(fetchApi, 'post', 'clapi/file/moveFolder/', { to_folder_id, folder_id })
    console.log({ moveFolder: response })

    if (response) {
        yield put({
            type: actions.MOVE_FOLDER_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.MOVE_FOLDER_FAIL,
            data: []
        })
    }

    yield put({
        type: actions.GET_FILE
    })
}

export function* deleteFolder({ folder_id }) {
    let response = yield call(fetchApi, 'post', 'clapi/file/deleteFolder/', { folder_id })
    console.log({ deleteFolder: response })

    if (response) {
        yield put({
            type: actions.DELETE_FOLDER_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.DELETE_FOLDER_FAIL,
            data: []
        })
    }

    yield put({
        type: actions.GET_FILE
    })
}

export function* editFolder({ folder_id, name }) {
    let response = yield call(fetchApi, 'post', 'clapi/file/editFolder/', { folder_id, name })
    console.log({ editFolder: response })

    if (response) {
        yield put({
            type: actions.EDIT_FOLDER_FAIL,
            data: response
        })
    } else {
        yield put({
            type: actions.EDIT_FOLDER_FAIL,
            data: []
        })
    }

    yield put({
        type: actions.GET_FILE
    })
}

export function* setFilePremium({ file_id, file_mode }) {
    let response = yield call(fetchApiJson, 'put', 'api/file/userfile/', [{ id: parseInt(file_id.toString()), file_mode }])
    console.log({ setPremium: response })

    if (response) {
        yield put({
            type: actions.SET_FILE_PREMIUM_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.SET_FILE_PREMIUM_FAIL,
            data: []
        })
    }

    yield put({
        type: actions.GET_FILE
    })
}

export default function* rootSaga() {
    yield [
        yield takeEvery(actions.GET_FILE, getFiles),
        yield takeEvery(actions.UPDATE_FOLDER, updateFolder),
        yield takeEvery(actions.MOVE_FILE, moveFile),
        yield takeEvery(actions.DELETE_FILE, deleteFile),
        yield takeEvery(actions.EDIT_FILE, editFile),
        yield takeEvery(actions.NEW_FOLDER, newFolder),
        yield takeEvery(actions.MOVE_FOLDER, moveFolder),
        yield takeEvery(actions.DELETE_FOLDER, deleteFolder),
        yield takeEvery(actions.EDIT_FOLDER, editFolder),
        yield takeEvery(actions.GET_FOLDER_LIST, getFolderList),
        yield takeEvery(actions.SET_FILE_PREMIUM, setFilePremium),
    ]
}