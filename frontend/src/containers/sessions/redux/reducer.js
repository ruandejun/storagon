import actions from './action'

const initState = {
    currentUser: null,
    fetching: false,
    errorString: '',
    successString: ''
};

export default function appReducer(state = initState, action) {
    console.log({ action })
    switch (action.type) {
        case actions.LOGIN_SUCCESSFULLY:
        case actions.UPDATE_PROFILE_SUCCESS:
        case actions.GET_PROFILE_SUCCESS:
            return { ...state, currentUser: action.payload, fetching: false };

        case actions.LOGIN:
        case actions.SIGN_UP:
        case actions.FORGOT_PASSWORD:
            return { ...state, fetching: true, errorString: '', successString: '' };

        case actions.LOGIN_FAIL:
            return { ...state, fetching: false, errorString: action.message }
        case actions.FORGOT_PASSWORD_SUCCESS:
            return { ...state, fetching: false, successString: action.message, errorString: '' }
        case actions.FORGOT_PASSWORD_FAIL:
            return { ...state, fetching: false, successString: '', errorString: action.message }
        case actions.CLEAR_ERROR:
            return { ...state, errorString: '', fetching: false, successString: '' }
        default:
            return state
    }
}
