import { takeEvery, put, call, select } from 'redux-saga/effects'
import actions from './action'
import { fetchApi, fetchApiLogin } from 'actions/api'

export const getCurrentFolder = (state) => state.file ? state.file.currentFolder : {}

export function* getFiles({ folder_id, offset, limit }) {
    const folder = folder_id ? folder_id : yield select(getCurrentFolder)
    let response = yield call(fetchApi, 'get', 'clapi/file/listFileAndFolder/', limit == 0 ? { folder_id: folder } : { folder_id: folder, offset, limit })
    console.log({ files: response })

    if (response) {
        yield put({
            type: actions.GET_FILE_SUCCESS,
            data: response
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
        folder_id, offset: 0, limit: 15
    })
}

export function* moveFile({ file_id, folder_id }) {
    let response = yield call(fetchApi, 'post', 'clapi/file/moveFile/', {file_id, folder_id})
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
        type: actions.GET_FILE, offset: 0, limit: 15
    })
}

export function* deleteFile({ file_id }) {
    let response = yield call(fetchApi, 'post', 'clapi/file/deleteFile/', {file_id})
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
        type: actions.GET_FILE, offset: 0, limit: 15
    })
}

export function* editFile({ file_id, file_name }) {
    let response = yield call(fetchApi, 'post', 'clapi/file/editFile/', {file_id, file_name})
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
        type: actions.GET_FILE, offset: 0, limit: 15
    })
}

export function* newFolder({ folder_name, folder_id }) {
    let response = yield call(fetchApi, 'post', 'clapi/file/newFolder/', {folder_name, folder_id})
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
        type: actions.GET_FILE, offset: 0, limit: 15
    })
}

export function* moveFolder({ folder_id, to_folder_id }) {
    let response = yield call(fetchApi, 'post', 'clapi/file/moveFolder/', {to_folder_id, folder_id})
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
        type: actions.GET_FILE, offset: 0, limit: 15
    })
}

export function* deleteFolder({ folder_id }) {
    let response = yield call(fetchApi, 'post', 'clapi/file/deleteFolder/', {folder_id})
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
        type: actions.GET_FILE, offset: 0, limit: 15
    })
}

export function* editFolder({ folder_id, name }) {
    let response = yield call(fetchApi, 'post', 'clapi/file/editFolder/', {folder_id, name})
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
        type: actions.GET_FILE, offset: 0, limit: 15
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
    ]
}