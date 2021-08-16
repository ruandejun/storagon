import { takeEvery, put, call, fork } from 'redux-saga/effects'
import actions from './action'
import { fetchApi, fetchApiLogin } from "actions/api"
import { push } from 'connected-react-router'
import Token from 'actions/token'

const extractProfile = (uresponse) => {
    let user = {}
    if (uresponse && uresponse.user_id) {
        user.user_id = uresponse.user_id
    }
    if (uresponse && uresponse.username) {
        user.username = uresponse.username
    }
    if (uresponse && uresponse.profiles) {
        try {
            const profiles = JSON.parse(uresponse.profiles)
            if (profiles && profiles.length > 0) {
                user.profile = profiles[0]
            }
        } catch (error) {
            console.log({ error })
        }
    }

    return user
}

export function* signUp({ payload }) {
    let response = yield call(fetchApiLogin, 'post', 'clapi/user/signup/', payload)
    console.log({ response })
    if (response && response.token) {
        Token.setToken(response.token);

        let uresponse = yield call(fetchApi, 'get', 'clapi/user/getUserInfo/')
        console.log({ uresponse })
        if (uresponse) {
            const user = extractProfile(uresponse)
            Token.setUser(user);

            yield put(push('/fm2'))
            yield put({
                type: actions.LOGIN_SUCCESSFULLY,
                payload: user
            });
        } else {
            yield put({
                type: actions.LOGIN_FAIL,
                message: 'Username or password is not valid'
            })
        }
    } else {
        if(response && response.error){
            yield put({
                type: actions.LOGIN_FAIL,
                message: response.error
            })
        } else {
            yield put({
                type: actions.LOGIN_FAIL,
                message: 'Username or password is not valid'
            })
        }
    }
}

export function* login({ payload }) {
    let response = yield call(fetchApiLogin, 'post', 'clapi/user/login/', payload)
    console.log({ response })
    if (response && response.token) {
        Token.setToken(response.token);

        let uresponse = yield call(fetchApi, 'get', 'clapi/user/getUserInfo/')
        console.log({ uresponse })
        if (uresponse) {
            const user = extractProfile(uresponse)
            Token.setUser(user);

            yield put(push('/fm2'))
            yield put({
                type: actions.LOGIN_SUCCESSFULLY,
                payload: user
            });
        } else {
            yield put({
                type: actions.LOGIN_FAIL,
                message: 'Username or password is not valid'
            })
        }
    } else {
        if(response && response.error){
            yield put({
                type: actions.LOGIN_FAIL,
                message: response.error
            })
        } else {
            yield put({
                type: actions.LOGIN_FAIL,
                message: 'Username or password is not valid'
            })
        }
    }
}

export function* getUser() {
}

export function* updateProfile() {
}


export function* getProfile() {
    let response = yield call(fetchApi, 'get', 'clapi/user/getUserInfo/')
    console.log({ profile: response })
    if (response) {
        const user = extractProfile(response)
        Token.setUser(user);

        yield put({
            type: actions.GET_PROFILE_SUCCESS,
            payload: user
        });
    }
}

export function* forgotPassword({email}) {
    let response = yield call(fetchApiLogin, 'post', 'clapi/user/sendResetPasswordEmail/', {email})
    console.log({ forgotPassword: response })

    if (response && response.error) {
        yield put({
            type: actions.FORGOT_PASSWORD_FAIL,
            message: response.error
        })
    } else {
        yield put({
            type: actions.FORGOT_PASSWORD_SUCCESS,
            message: 'Reset password link sent successfully. Please check your email'
        })
    }
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
        yield takeEvery(actions.FORGOT_PASSWORD, forgotPassword),
    ]
}

