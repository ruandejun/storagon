import React, { Fragment, useState, useEffect, useCallback, styl } from 'react'
import SideBar from 'components/SideBar'

const Page = ({ accountType, accountStatus }) => {

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
                                            <td>username</td>
                                        </tr>
                                        {accountStatus === 'emailNotActivated' &&
                                            <tr className="active-account">
                                                <td></td>
                                                <td><button ng-click="resendActivationEmail()" ng-disabled="isProcessingResendActivationEmail" className="tiny">Resend activation email</button></td>
                                            </tr>
                                        }
                                        <tr>
                                            <td>Email</td>
                                            <td>email</td>
                                        </tr>
                                        <tr>
                                            <td>Status</td>
                                            <td>accountStatus</td>
                                        </tr>
                                        <tr>
                                            <td>Account Type</td>
                                            <td>accountType</td>
                                        </tr>
                                        {accountType !== 'affiliate' && accountType !== 'affiliatePPD' && accountStatus !== 'emailNotActivated' &&
                                            <tr className="apply-affiliate">
                                                <td></td>
                                                <td><button ng-click="applyAffiliate()" className="tiny"> Apply to become Affiliate</button></td>
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
                                            <td> monthly_bandwidth | filesize </td>
                                        </tr>
                                        <tr>
                                            <td>Download Speed</td>
                                            <td>(download_speed = 10485760) ? "Unlimited" : ((download_speed | filesize) + " / s")</td>
                                        </tr>
                                        <tr>
                                            <td>Download Wait</td>
                                            <td>download_wait</td>
                                        </tr>
                                        <tr>
                                            <td>Access to Premium files</td>
                                            <td>access_premium_files</td>
                                        </tr>
                                        <tr>
                                            <td>Access to Premium tools</td>
                                            <td>access_premium_tools</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    <hr />
                    <div className="row padding-bottom-30">
                        <div className="large-6 columns">
                            <h5>Used space: storageUsed | filesize of storageSpace | filesize</h5>
                            <div className="progress small success round">
                                <span className="meter" 
                                    // style="width: { storageUsed / storageSpace | percentage };"
                                    ></span>
                            </div>
                            <p>You have total of folder | number folders with file | number files inside.</p>
                        </div>
                        <div className="large-6 columns">
                            <h5>Used bandwidth: bandwidthUsed | filesize of monthly_bandwidth | filesize</h5>
                            <div className="progress small round">
                                <span className="meter" 
                                    // style="width: { bandwidthUsed / monthly_bandwidth | percentage };"
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
                                        <h3>Premium Status: premiumStatus | uppercase</h3>
                                        <p>Plan expired in: planExpired | date.</p>
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
                                        <h3>Point: pointBalance</h3>
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