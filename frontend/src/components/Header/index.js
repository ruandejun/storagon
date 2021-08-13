import moment from 'moment'
import React, { Fragment, useEffect, useRef, useState } from 'react'
import Token from '../../actions/token'
import logo_icon from '../../assets/images/logo.png'
import {useDispatch} from 'react-redux'

import actions from 'containers/sessions/redux/action'

const {logOut} = actions

const Header = ({history}) => {
    const user = Token.getUser()
    const dispatch = useDispatch()
    
    let is_authenticated = false
    if(user && user.profile && user.profile.fields && user.profile.fields.plan_expired){
        console.log({user})
        // if(moment(user.profile.fields.plan_expired).isAfter(moment())){
            is_authenticated = true
        // }
    }

    const logout = () => {
        dispatch(logOut())
    }

    return (
        <header>
            <div className="top">
                <div className="row">
                    <div className="header-logo">
                        <div className="logo">
                            <a href="/" title=""><img src={logo_icon} alt="" title="" /></a>
                        </div>
                    </div>
                    <div className="header-action">
                        <nav className="desktop-menu">
                            <ul className="sf-menu">
                                {!is_authenticated &&
                                    <li>
                                        <a href="/" target="_blank">Home</a>
                                    </li>
                                }
                                {is_authenticated &&
                                    <li className="has-dropdown">
                                        <a href="/account" target="_blank">Account</a>
                                        <ul className="dropdown">
                                            <li><a href="/account" target="_blank">Overview</a></li>
                                            <li><a href="/profile" target="_blank">Profile</a></li>
                                            <li><a href="/billing" target="_blank">Billing history</a></li>
                                            <li><a href="/statistic" target="_blank">Statistic</a></li>
                                            <li><a href="/inbox" target="_blank">Inbox</a></li>
                                            <li><a href="/report" target="_blank">Report</a></li>
                                            <li><a href="/redeem" target="_blank">Redeem</a></li>
                                        </ul>
                                    </li>
                                }
                                {is_authenticated &&
                                    <li>
                                        <a href="/fm2" target="_blank">File Manager</a>
                                    </li>
                                }
                                {!is_authenticated &&
                                    <li>
                                        <a href="/login" id="login-button">Login</a>
                                    </li>
                                }
                                {!is_authenticated &&
                                    <li>
                                        <a href="/signup" id="signup-button">Register</a>
                                    </li>
                                }
                                <li>
                                    <a href="/premium" target="_blank">Premium</a>
                                </li>
                                <li>
                                    <a href="/download-tool" target="_blank">Tool</a>
                                </li>
                                {is_authenticated &&
                                    <li>
                                        <a onClick={logout} target="_blank">Logout</a>
                                    </li>
                                }
                            </ul>
                        </nav>
                    </div>
                </div>
            </div>
        </header>
    )
}

export default Header