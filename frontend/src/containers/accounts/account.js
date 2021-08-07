import React, { useEffect, useState } from 'react'
import SideBar from 'components/SideBar'
import { useDispatch, useSelector } from 'react-redux'

import actions from './redux/action'
import authActions from 'containers/sessions/redux/action'

import { AccountStatusFilter, AccountTypeFilter } from 'actions/constants'
import moment from 'moment'
import { fetchApi } from 'actions/api'

const { getPlan, getBalance, getStorage } = actions
const { getProfile } = authActions

const Page = ({ }) => {
    const dispatch = useDispatch()
    const user = useSelector((state) => state.auth.currentUser)
    const userPlan = useSelector((state) => state.account.plan)
    const userBalance = useSelector((state) => state.account.balance)
    const userStorage = useSelector((state) => state.account.storage)
    const [isProcessingResendActivationEmail, setIsProcessingResendActivationEmail] = useState(false)

    useEffect(() => {
        dispatch(getPlan())
        dispatch(getBalance())
        dispatch(getStorage())
        dispatch(getProfile())

        return () => { }
    }, [])

    const applyAffiliate = () => {

    }

    const resendActivationEmail = async() => {
        setIsProcessingResendActivationEmail(true)
        const response = await fetchApi('post', 'clapi/user/resendActivationEmail/', {})
        console.log({response})
        setIsProcessingResendActivationEmail(false)
        // if(response){
            alert('Successful! Please check your email to confirm')

        // } else {
        //     alert('Failed! Please check your email again!')
        // }
    }

    const accountType = user ? AccountTypeFilter[user.profile.fields.account_type] : ''
    const accountStatus = user ? AccountStatusFilter[user.profile.fields.account_status] : ''

    const user_plan_id = user ? user.profile.fields.plan_id : 0
    const monthly_bandwidth = userPlan ? userPlan.planConfigDict[user_plan_id].download_bandwidth : 1
    const download_speed = userPlan ? userPlan.planConfigDict[user_plan_id].download_speed : 0
    const download_wait = (user_plan_id === 0) ? '30 seconds' : 'No wait'
    const access_premium_files = (user_plan_id === 0) ? 'No' : 'Yes'
    const access_premium_tools = (user_plan_id === 0) ? 'No' : 'Yes'
    const premiumStatus = (user_plan_id > 0) ? 'Premium' : 'User'
    const planExpired = user ? user.profile.fields.plan_expired : null
    const storageSpace = user ? user.profile.fields.storage_space : ''
    const email = user ? user.profile.fields.email : ''

    const storageUsed = userStorage ? userStorage.storage_used : 0
    const bandwidthUsed = userStorage ? userStorage.download_bandwidth : 0
    const folder = userStorage ? userStorage.folder_count : 0
    const file = userStorage ? userStorage.file_count : 0

    const pointBalance = userBalance ? userBalance[1].fields.amount : 0

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <div className="row padding-bottom-10">
                        <div className="large-4 columns">
                            <h5>Account details</h5>
                            <div className="row collapse">
                                <table role="grid" width="100%">
                                    <tbody>
                                        <tr>
                                            <td>Username</td>
                                            <td>{user ? user.username : ''}</td>
                                        </tr>
                                        {accountStatus === 'emailNotActivated' &&
                                            <tr className="active-account">
                                                <td></td>
                                                <td><button onClick={resendActivationEmail} disabled={isProcessingResendActivationEmail} className="tiny">Resend activation email</button></td>
                                            </tr>
                                        }
                                        <tr>
                                            <td>Email</td>
                                            <td>{email}</td>
                                        </tr>
                                        <tr>
                                            <td>Status</td>
                                            <td>{accountStatus}</td>
                                        </tr>
                                        <tr>
                                            <td>Account Type</td>
                                            <td>{accountType}</td>
                                        </tr>
                                        {accountType !== 'affiliate' && accountType !== 'affiliatePPD' && accountStatus !== 'emailNotActivated' &&
                                            <tr className="apply-affiliate">
                                                <td></td>
                                                <td><button onClick={applyAffiliate} className="tiny"> Apply to become Affiliate</button></td>
                                            </tr>
                                        }
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div className="large-8 columns">
                            <h5>Account Limitations</h5>
                            <div className="row collapse">
                                <table role="grid" width="100%">
                                    <thead>
                                        <tr>
                                            <th width="200">FEATURES</th>
                                            <th width="200">LIMITS</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>Monthly Bandwidth</td>
                                            <td> {monthly_bandwidth} </td>
                                        </tr>
                                        <tr>
                                            <td>Download Speed</td>
                                            <td>{(download_speed == 10485760) ? "Unlimited" : (download_speed + " / s")}</td>
                                        </tr>
                                        <tr>
                                            <td>Download Wait</td>
                                            <td>{download_wait}</td>
                                        </tr>
                                        <tr>
                                            <td>Access to Premium files</td>
                                            <td>{access_premium_files}</td>
                                        </tr>
                                        <tr>
                                            <td>Access to Premium tools</td>
                                            <td>{access_premium_tools}</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    <hr />
                    <div className="row padding-bottom-30">
                        <div className="large-6 columns">
                            <h5>Used space: {storageUsed} of {storageSpace}</h5>
                            <div className="progress small success round">
                                <span className="meter" style={{width: (storageUsed / storageSpace) + '%' }}
                                ></span>
                            </div>
                            <p>You have total of {folder} folders with {file} files inside.</p>
                        </div>
                        <div className="large-6 columns">
                            <h5>Used bandwidth: {bandwidthUsed} of {monthly_bandwidth}</h5>
                            <div className="progress small round">
                                <span className="meter" style={{width: (bandwidthUsed / monthly_bandwidth) + '%'}}
                                ></span>
                            </div>
                        </div>
                    </div>
                    <hr />

                    <div className="row padding-bottom-30">
                        <ul className="small-block-grid-1 large-block-grid-2 medium-block-grid-2 domainfeatures">
                            <li>
                                <div className="row">
                                    <div className="small-12 large-3 medium-3 columns">
                                        <div className="circle">
                                            <i className="fa fa-trophy"></i>
                                        </div>
                                    </div>
                                    <div className="small-12 large-9 medium-9 columns">
                                        <h3>Premium Status: {premiumStatus.toUpperCase()}</h3>
                                        <p>Plan expired in: {moment(planExpired).format()}.</p>
                                        <a href="/premium" className="tiny button">Extend your premium</a>
                                    </div>
                                </div>
                            </li>

                            <li>
                                <div className="row">
                                    <div className="small-12 large-3 medium-3 columns">
                                        <div className="circle">
                                            <i className="fa fa-dollar"></i>
                                        </div>
                                    </div>
                                    <div className="small-12 large-9 medium-9 columns">
                                        <h3>Point: {pointBalance}</h3>
                                        <p>You can use this point to exchange to premium.</p>
                                        <a className="tiny button">Exchange your Premium</a>
                                    </div>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>
                <SideBar />
            </div>
        </div>
    )
}

export default Page