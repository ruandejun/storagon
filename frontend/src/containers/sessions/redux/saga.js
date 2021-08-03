import { takeEvery, put, call, fork } from 'redux-saga/effects'
import actions from './action'
import { fetchApi, fetchApiLogin } from "../../../actions/api"
import { push } from 'react-router-redux'
import Token from '../../../actions/token'

export function* signUp({ payload }) {

}

export function* login({ payload }) {
    let response = yield call(fetchApiLogin, 'post', 'clapi/user/login/', payload)
    console.log({response})
    if (response == 'success') {
        let response1 = yield call(fetchApiLogin, 'get', 'clapi/user/getUserInfo/')

        console.log({response1})

    // Token.setToken(response.key);

    // let uresponse = yield call(fetchApi, 'get', 'rest-auth/user/');
    //   if (uresponse) {
    //   Token.setUser(uresponse);

    //   yield put({
    //     type: actions.LOGIN_SUCCESSFULLY,
    //     payload: uresponse
    //   });

    //   let lresponse = yield call(fetchApi, 'get', 'words/language-selection/get_active_combination/');
    //   if (lresponse && lresponse.combination && lresponse.is_active) {
    //     yield put({
    //       type: actions.GET_ACTIVE_PAIR_SUCCESS,
    //       payload: lresponse
    //     });

    //     if(lresponse.value > 0){
    //       yield put(push('/dashboard/course'))
    //     } else {
    //       yield put(push('/vocabulary_test'));
    //     }
    //   } else {
    //     yield put(push('/select_language'));
    //   }
    // }
  } else {
        yield put({
            type: actions.LOGIN_FAIL,
            payload: response
        })
    }
}

export function* getUser() {
}

export function* updateProfile() {
}


export function* getProfile() {
}

export function* logOut() {
    Token.destroy()
    yield put({
        type: actions.REMOVE_CURRENT_USER,
    })
    yield put(push('/'));
}

export default function* rootSaga() {
    yield [
        yield takeEvery(actions.LOGIN, login),
        yield takeEvery(actions.SIGN_UP, signUp),
        yield takeEvery(actions.GET_USER, getUser),
        yield takeEvery(actions.UPDATE_PROFILE, updateProfile),
        yield takeEvery(actions.GET_PROFILE, getProfile),
        yield takeEvery(actions.LOG_OUT, logOut),
    ]
}

