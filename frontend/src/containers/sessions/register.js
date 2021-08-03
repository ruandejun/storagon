import React, { Fragment, useState, useEffect, useCallback } from 'react'
import loading from '../../assets/images/ajax-spinner.gif'
// import {
//     useGoogleReCaptcha,
//     GoogleReCaptchaProvider
// } from 'react-google-recaptcha-v3'
import ReCAPTCHA from 'react-google-recaptcha'

const Page = ({ history }) => {
    const [error, setError] = useState(null)
    const [token, setToken] = useState(null)

    const onSignup = () => {
        console.log({ token })
    }

    return (
        <div className="login-container">
            <div className="row">
                <div className="small-12 large-7 large-centered medium-7 medium-centered columns">
                    <div className="login-form">
                        <form id="signup_form" name="signup_form">
                            Username: <input type="text" name="username" size="50" ng-model="username" required />
                            Password: <input type="password" name="password" id="password" size="20" ng-model="password" required />
                            Retype Password: <input type="password" name="retype_password" id="retype_password" size="20" ng-model="retype_password" required pw-check="password" />
                            {error &&
                                <div className="msg-block" >
                                    <small className="error" >Password don't match</small>
                                </div>
                            }
                            Email: <input type="text" name="email" size="50" ng-model="email" required />
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
                        <div className="loader">
                            <img id="loading-image" src={loading} alt="Loading..." />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Page