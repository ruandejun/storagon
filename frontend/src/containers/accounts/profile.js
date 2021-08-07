import React, {useEffect} from 'react'
import SideBar from 'components/SideBar'
import { useSelector, useDispatch } from 'react-redux'

import actions from './redux/action'

const { getBilling } = actions

const Page = ({ }) => {
    const dispatch = useDispatch()

    useEffect(() => {
        dispatch(getBilling())

        return () => { }
    }, [])

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <div id="profile">
                        <form id="profile_form" novalidate="novalidate" ng-submit="processForm()">
                            <div className="row">
                                <div className="large-8 columns">
                                    <div className="loader">
                                        <img id="loading-image" src="/static/assets/frontend/images/ajax-spinner.gif" alt="Loading..." />
                                    </div>
                                    <h5>Personal Information</h5>
                                    <p>
                                        <label for="full_name">Full Name:</label>
                                        <input type="text" name="full_name" id="full_name" tabindex="2" placeholder="Full Name" ng-model="full_name" required />
                                    </p>
                                    <p>
                                        <label for="address">Address:</label>
                                        <input type="text" name="address" id="address" tabindex="3" placeholder="Address" ng-model="address" required />
                                    </p>
                                    <p>
                                        <label for="email">Email:</label>
                                        <input type="text" name="email" id="email" tabindex="4" placeholder="Email" ng-model="email" required />
                                    </p>
                                    <hr />
                                    <h5>Change Password</h5>
                                    <p>
                                        <label for="account-password">Current Password:</label>
                                        <input type="password" name="account-password" id="account-password" tabindex="4" ng-model="old_password" />
                                    </p>
                                    <p>
                                        <label for="account-new-password">New Password:</label>
                                        <input type="password" name="account-new-password" id="account-new-password" tabindex="5" ng-model="password" />
                                    </p>
                                    <p>
                                        <label for="account-confirm-password">Confirm New Password:</label>
                                        <input type="password" name="account-confirm-password" id="account-confirm-password" tabindex="6" ng-model="password2" />
                                    </p>
                                    <button type="submit" className="button expand">Submit</button>
                                    <div data-alert="" className="alert-box success" ng-show="success">
                                        message
                                        <a href="" className="close">×</a>
                                    </div>
                                    <div data-alert="" className="alert-box alert" ng-show="error">
                                        message
                                        <a href="" className="close">×</a>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>

                <SideBar />
            </div>
        </div>
    )
}

export default Page