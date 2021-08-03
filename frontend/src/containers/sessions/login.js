import React, { Fragment, useState, useRef } from 'react'
import img_login from '../../assets/images/img-login.png'
import loading from '../../assets/images/loading.gif'
import actions from './redux/action'
import {useDispatch, useSelector} from 'react-redux'

const {login} = actions

const Page = ({ history }) => {
    const [showLogin, setShowLogin] = useState(true)
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [email, setEmail] = useState('')
    const refForm = useRef(null)
    const dispatch = useDispatch()

    const handleForgotPassword = () => {
        setShowLogin(!showLogin)
    }

    const submitLogin = (event) => {
        event.preventDefault()
        dispatch(login(username, password))
        if(refForm){
            refForm.current.reset()
        }
    }

    const handleUsername = (event) => {
        setUsername(event.target.value)
    }

    const handlePassword = (event) => {
        setPassword(event.target.value)
    }

    const handleEmail = (event) => {
        setEmail(event.target.value)
    }

    return (
        <div className="login-container">
            <div className="row">
                <div className="small-12 large-7 large-centered medium-7 medium-centered columns">
                    {showLogin &&
                        <div className="login-form" >
                            <form ref={refForm} name="login_form" onSubmit={submitLogin}>
                                Username: <input type="text" name="username" size="50" value={username} onChange={handleUsername} required />
                                Password: <input type="password" name="password" size="20" value={password} onChange={handlePassword} required />
                                <p id="nameHelpText"><a onClick={handleForgotPassword} className="reset-pass-link">Forgot username or password ?</a></p>
                                <input type="submit" value="Login" ng-disabled="isProcessing" />
                            </form>
                            <div className="loader">
                                <img id="loading-image" src={loading} alt="Loading..." />
                            </div>
                        </div>
                    }
                    {!showLogin &&
                        <div className="login-form">
                            <form id="reset_form" name="reset_form">
                                Email: <input type="text" name="email" size="50" value={email} onChange={handleEmail}  required />
                                <p id="emailHelpText"><a onClick={handleForgotPassword} className="reset-pass-link">Back to login</a></p>
                                <input type="submit" value="Reset Password" ng-disabled="isProcessing" />
                            </form>
                            <div className="loader">
                                <img id="loading-image" src={loading} alt="Loading..." />
                            </div>
                        </div>
                    }
                </div>
            </div>
        </div>
    )
}

export default Page