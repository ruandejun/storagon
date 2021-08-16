const actions = {
    LOGIN: 'LOGIN',
    SIGN_UP: 'SIGN_UP',
    GET_USER: 'GET_USER',
    LOGIN_SUCCESSFULLY: 'LOGIN_SUCCESSFULLY',
    LOGIN_FAIL: 'LOGIN_FAIL',
    SIGN_UP_SUCCESS: 'SIGN_UP_SUCCESS',
    REMOVE_CURRENT_USER: 'REMOVE_CURRENT_USER',
    UNMOUNT_ERROR: 'UNMOUNT_ERROR',
    GET_ACTIVE_PAIR_SUCCESS: 'GET_ACTIVE_PAIR_SUCCESS',
    UPDATE_PROFILE: 'UPDATE_PROFILE',
    UPDATE_PROFILE_SUCCESS: 'UPDATE_PROFILE_SUCCESS',
    UPDATE_PROFILE_FAIL: 'UPDATE_PROFILE_FAIL',
    GET_PROFILE: 'GET_PROFILE',
    GET_PROFILE_SUCCESS: 'GET_PROFILE_SUCCESS',
    LOG_OUT: 'LOG_OUT',
    CLEAR_ERROR: 'CLEAR_ERROR',
    FORGOT_PASSWORD: 'FORGOT_PASSWORD',
    FORGOT_PASSWORD_SUCCESS: 'FORGOT_PASSWORD_SUCCESS',
    FORGOT_PASSWORD_FAIL: 'FORGOT_PASSWORD_FAIL',
    clearError: () => {
      return {
        type: actions.CLEAR_ERROR
      }
    },
    login: (username, password) => {
      return {
        type: actions.LOGIN,
        payload: { username, password }
      }
    },
    signUp: (username,password,email,captcha) => {
        return  {
          type: actions.SIGN_UP,
          payload: {username,password,email,captcha}
        }
    },
    forgotPassword: (email) => {
      return {
        type: actions.FORGOT_PASSWORD,
        email
      }
    },
    getUser: (pathname) => {
      return {
        type: actions.GET_USER,
        pathname
      }
    },
    unmountError: () => {
      return {
        type: actions.UNMOUNT_ERROR,
      }
    },
    updateProfile: (payload) => {
      return {
        type: actions.UPDATE_PROFILE,
        payload
      }
    },
    getProfile: () => {
      return  {
        type: actions.GET_PROFILE,
      }
    },
    logOut: () => {
      return  {
        type: actions.LOG_OUT,
      }
    }
  };
  
  export default actions
  