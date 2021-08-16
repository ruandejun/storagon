import React, { Fragment, useState, useEffect, useCallback } from 'react'
import loading from '../../assets/images/loading.gif'
import ReCAPTCHA from 'react-google-recaptcha'
import { useDispatch, useSelector } from 'react-redux'
import actions from './redux/action'
import { Alert } from '@material-ui/lab'

const { signUp, clearError } = actions

const Page = ({ history }) => {
    const [error, setError] = useState(false)
    const [token, setToken] = useState(null)
    const dispatch = useDispatch()
    const [email, setEmail] = useState('')
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const fetching = useSelector(state => state.auth.fetching)
    const errorString = useSelector(state => state.auth.errorString)

    useEffect(() => {
        dispatch(clearError())

        return () => {
        }
    }, [])

    const onSignup = (event) => {
        event.preventDefault()

        if (password != confirmPassword) {
            setError(true)
            return
        } else {
            setError(false)
        }
        if (!token) {
            alert('Please confirm the reCaptcha')
            return
        }

        dispatch(signUp(username, password, email, token))
    }

    return (
        <div className="login-container">
            <div className="row">
                <div className="small-12 large-7 large-centered medium-7 medium-centered columns">
                    <div className="login-form">
                        {errorString && errorString.length > 0 &&
                            <Alert severity="error" style={{ marginBottom: 8 }}>{errorString}</Alert>
                        }
                        <form id="signup_form" name="signup_form">
                            Username: <input type="text" name="username" size="50" ng-model="username" required value={username} onChange={event => setUsername(event.target.value)} />
                            Password: <input type="password" name="password" id="password" size="20" ng-model="password" required value={password} onChange={event => setPassword(event.target.value)} />
                            Retype Password: <input type="password" name="retype_password" id="retype_password" size="20" ng-model="retype_password" required pw-check="password" value={confirmPassword} onChange={event => setConfirmPassword(event.target.value)} />
                            {error &&
                                <div className="msg-block" >
                                    <small className="error" >Password don't match</small>
                                </div>
                            }
                            Email: <input type="text" name="email" size="50" ng-model="email" required value={email} onChange={event => setEmail(event.target.value)} />
                            <input type="checkbox" id="agree" name="agree" required />
                            <label for="agree">I have read and agree to the <a href="/tos" target="_blank">{'Terms & Conditions'}</a></label>
                            <div>
                                <ReCAPTCHA
                                    sitekey="6LeAKwQTAAAAADQGSxeqaWehXOFJwuVIgWPEiQrX"
                                    onChange={(value) => setToken(value)}
                                />
                            </div>
                            <input onClick={onSignup} type="submit" value="Sign up" ng-disabled="isProcessing" />
                        </form>
                        {fetching &&
                            <div className="loader" style={{ display: 'block' }}>
                                <img id="loading-image" src={loading} alt="Loading..." />
                            </div>
                        }
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Page