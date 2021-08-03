import actions from './action'

const initState = {
    currentUser: null
};

export default function appReducer(state = initState, action) {
    console.log({action})
    switch (action.type) {
        default:
            return state
    }
}
