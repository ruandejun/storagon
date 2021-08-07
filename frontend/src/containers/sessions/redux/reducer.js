import actions from './action'

const initState = {
    currentUser: null
};

export default function appReducer(state = initState, action) {
    console.log({ action })
    switch (action.type) {
        case actions.LOGIN_SUCCESSFULLY:
        case actions.UPDATE_PROFILE_SUCCESS:
        case actions.GET_PROFILE_SUCCESS:
            return { ...state, currentUser: action.payload };
        default:
            return state
    }
}
