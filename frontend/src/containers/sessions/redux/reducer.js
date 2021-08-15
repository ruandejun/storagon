import actions from './action'

const initState = {
    currentUser: null,
    fetching: false
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
            return { ...state, fetching: true };

        case actions.LOGIN_FAIL:
            return { ...state, fetching: false };
        default:
            return state
    }
}
