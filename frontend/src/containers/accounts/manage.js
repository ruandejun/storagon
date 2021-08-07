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
                    <div className="text-center clearfix">
                        <div className="panel callout">
                            <h5>Your Current Balance: $creditBalance | amount <span className="success"> ( Available: $availableBalance | amount )</span></h5>
                            <h5>Your affiliate URL: http://storagon.com/signup?referer=username</h5>
                        </div>
                    </div>
                    <ul className="tabs" data-tab="" id="affiliate-tab">
                        <li className="tab-title active"><a href="#affWebsite" aria-selected="true" tabindex="0">Affiliate Websites</a></li>
                        <li className="tab-title"><a href="#accountBalance" aria-selected="false" tabindex="-1">Account Balance</a></li>
                        <li className="tab-title"><a href="#listReferrer" aria-selected="false" tabindex="-1">List Referrer</a></li>
                        <li className="tab-title"><a href="#changeAffMode" aria-selected="false" tabindex="-1">Change Mode</a></li>
                        <li className="tab-title"><a href="#withdraw" aria-selected="false" tabindex="-1">Withdraw Money</a></li>
                    </ul>
                    <div className="tabs-content">
                        <div className="content active" id="affWebsite" aria-hidden="false">
                            <h4 className="session-title">Affiliate Website</h4>
                            <a className="button small right addAffWebsite" ng-click="addAffWebsite()">Add more website</a>
                            <hr />
                            <table role="grid" className="table fixed_layout">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Website address</th>
                                        <th>Added at</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr ng-repeat="(key, value) in affWebsiteData">
                                        <td>key</td>
                                        <td>value.fields.website_domain</td>
                                        <td>value.fields.created_date | date</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div className="content" id="accountBalance" aria-hidden="true" tabindex="-1">
                            <h4 className="session-title">Account Balance</h4>
                            <a className="button small right addAffWebsite" ng-click="addAccount()">Add more account</a>
                            <hr />
                            <table role="grid" className="table fixed_layout">
                                <thead>
                                    <tr>
                                        <th>Account ID</th>
                                        <th>Amount</th>
                                        <th>Balance type</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr ng-repeat="(key, value) in accountBalance">
                                        <td>value.account_id</td>
                                        <td>(value.balance_type === 0 || value.balance_type === 4) ? '$' : ''value.amount | amountt(value.balance_type === 1) ? ' point' : ''</td>
                                        <td>value.balance_type | enumBalanceType</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div className="content" id="listReferrer" aria-hidden="true" tabindex="-1">
                            <h4 className="session-title">List Referrer</h4>
                            <hr />
                            <table role="grid" className="table fixed_layout">
                                <thead>
                                    <tr>
                                        <th>Your Referrer</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr ng-repeat="(key, value) in referrer">
                                        <td>value</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div className="content" id="changeAffMode" aria-hidden="true" tabindex="-1">
                            <h4 className="session-title">Change Affiliate Mode</h4>
                            <hr />
                            <form name="affiliate-form" id="affiliate-form" ng-submit="processPPDForm()">
                                <div className="panel">
                                    <h4 className="text-center">Terms of Service for Affiliate</h4>
                                    <p>You are legally responsible for all of your uploaded data on our server</p>
                                    <p>We reserve the right to delete your files without the need to consult if we receive any feedback that your file copyright infringement or violation of law in your country and in the world</p>
                                    <p>We may also delete your files automatically if there are no downloads arising from that file within 45 days. For uploader who purchased premium plans, the limitation is 90 days</p>
                                    <p>We will not pay for your bills if you have actions that violate the rules seriously when using our services joining the affiliate program</p>
                                    <p>What we offer</p>
                                    <p>
                                        <a className="button small info" id="pps" ng-click="displayProg($event)">Pay Per Sale</a>
                                        <a className="button small info" id="ppd" ng-click="displayProg($event)">Pay Per Download</a>
                                    </p>
                                    <table className="table" role="grid" ng-show="pps">
                                        <tbody>
                                            <tr>
                                                <th>Affiliate Program</th>
                                                <td>Agency transaction</td>
                                                <td>Referrer Transaction</td>
                                                <td>Website Transaction</td>
                                            </tr>
                                            <tr>
                                                <th>Payment</th>
                                                <td>60% of your bills</td>
                                                <td>10% of your referrer's agency program</td>
                                                <td>5% of bills originated from your websites</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                    <table className="table" role="grid" ng-show="ppd">
                                        <tbody>
                                            <tr>
                                                <th>Size / Group*</th>
                                                <th>1 - 50 MB</th>
                                                <th>50 - 100 MB</th>
                                                <th>100 - 250 MB</th>
                                                <th>250 - 500 MB</th>
                                                <th>500 - 1000 MB</th>
                                                <th> 1000 MB</th>
                                            </tr>
                                            <tr>
                                                <th>I</th>
                                                <td>$3.00</td>
                                                <td>$5.00</td>
                                                <td>$7.00</td>
                                                <td>$10.00</td>
                                                <td>$20.00</td>
                                                <td>$40.00</td>
                                            </tr>
                                            <tr>
                                                <th>II</th>
                                                <td>$1.00</td>
                                                <td>$3.00</td>
                                                <td>$5.00</td>
                                                <td>$6.00</td>
                                                <td>$7.00</td>
                                                <td>$10.00</td>
                                            </tr>
                                            <tr>
                                                <th>III</th>
                                                <td>$1.00</td>
                                                <td>$1.00</td>
                                                <td>$1.50</td>
                                                <td>$2.00</td>
                                                <td>$2.50</td>
                                                <td>$3.00</td>
                                            </tr>
                                            <tr>
                                                <th>IV</th>
                                                <td>$0.50</td>
                                                <td>$0.50</td>
                                                <td>$0.50</td>
                                                <td>$0.50</td>
                                                <td>$0.50</td>
                                                <td>$0.50</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                    <p ng-show="ppd">*Country groups: </p>
                                    <ol type="I" ng-show="ppd">
                                        <li>Belgium, United States, Saudi Arabia, Poland, Netherlands, United Kingdom, France, Spain, Germany, Canada</li>
                                        <li>Japan, Kuwait, Monaco, Norway, New Zealand, Portugal, Qatar, Russian Federation, Sweden, Singapore, South Africa, Italy, Isle of Man, Andorra, United Arab Emirates, Austria, Australia, Switzerland, Cyprus, Czech Republic, Denmark, Finland, Ireland, Israel</li>
                                        <li>Luxembourg, Latvia, Mauritius, Malaysia, Oman, Slovenia, Turkey, Ukraine, Lithuania, Korea, Republic of, Argentina, Bulgaria, Brazil, Dominican Republic, Estonia, Greece, Hong Kong, Hungary</li>
                                        <li>All others</li>
                                    </ol>
                                </div>
                                <div className="large-12 columns">
                                    <label><h5>Choose Your Program</h5></label>
                                    <input type="radio" ng-model="Mode" name="mode" value="pps" id="pps_mode" /><label for="pps_mode">I want to join the PPS Program</label>
                                    <input type="radio" ng-model="Mode" name="mode" value="ppd" id="ppd_mode" /><label for="ppd_mode">I want to join the PPD Program</label>
                                </div>
                                <button type="submit" className="button expand">Change Mode</button>
                            </form>
                            <div data-alert="" className="alert-box success" ng-show="success">
                                message
                                <a href="" className="close">×</a>
                            </div>
                            <div data-alert="" className="alert-box alert" ng-show="error">
                                message
                                <a href="" className="close">×</a>
                            </div>
                            <div className="loader">
                                <img id="loading-image" src="/static/assets/frontend/images/ajax-spinner.gif" alt="Loading..." />
                            </div>
                        </div>
                        <div className="content" id="withdraw" aria-hidden="true" tabindex="-1">
                            <h4 className="session-title">Withdraw Money</h4>
                            <hr />
                            <form name="withdraw-form" id="withdraw-form" ng-submit="processWithdrawForm()">
                                <div className="panel">
                                    <h4 className="text-center">Terms of Service for Withdraw Money</h4>
                                    <p>You are legally responsible for all of your uploaded data on our server</p>
                                    <p>We reserve the right to delete your files without the need to consult if we receive any feedback that your file copyright infringement or violation of law in your country and in the world</p>
                                </div>
                                <div className="large-12 columns">
                                    <h5>Information for withdrawing</h5>
                                    <div className="row collapse">
                                        <label for="withdraw_amount">Withdraw Amount ($):</label>
                                        <div className="small-2 large-1 columns">
                                            <span className="prefix" style={{marginTop: 8, height: 45, paddingTop: 6}}>$</span>
                                        </div>
                                        <div className="small-10 large-11 columns">
                                            <input type="text" name="withdraw_amount" id="withdraw_amount" tabindex="2" placeholder="Please input in dollar" ng-model="withdraw_amount" required />
                                        </div>
                                    </div>
                                    <p>
                                        <label for="deposit_balance_id">Deposit Balance:</label>
                                        <select type="text" name="deposit_balance_id" id="deposit_balance_id" tabindex="3" ng-model="deposit_balance_id" ng-options="v.name for v in deposit_balance_type.values track by v.id" required>
                                            <option value="">- Choose Deposit Balance -</option>
                                        </select>
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
                                    <div className="loader">
                                        <img id="loading-image" src="/static/assets/frontend/images/ajax-spinner.gif" alt="Loading..." />
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>

                <SideBar />
            </div>
        </div>
    )
}

export default Page