import React, { useState } from 'react'

const Footer = ({ }) => {
    const [showAffiliate, setShowAffiliate] = useState(true)
    const [showReseller, setShowReseller] = useState(true)

    return (
        <div className="large-2 pull-10 columns">
            <p><img className="th" src='http://placehold.it/128x128' /></p>
            <ul className="side-nav">
                <li><a href="account">Overview</a></li>
                <li>
                    <a data-options="is_hover:true; align:right" data-dropdown="drop1">My Account</a>
                    <ul id="drop1" className="f-dropdown" data-dropdown-content>
                        <li><a href="billing">Billing history</a></li>
                        <li className="divider"></li>
                        <li><a href="redeem">Redeem</a></li>
                        <li className="divider"></li>
                        <li><a href="profile">Edit Profile</a></li>
                    </ul>
                </li>
                <li><a href="inbox">Inbox</a></li>
                <li><a href="report">Report</a></li>
                {showAffiliate &&
                    <li>
                        <a data-options="is_hover:true; align:right" data-dropdown="drop3">Affiliate</a>
                        <ul id="drop3" className="f-dropdown" data-dropdown-content>
                            <li><a href="/manage">Dashboard</a></li>
                            <li className="divider"></li>
                            <li><a href="statistic">Statistic</a></li>
                            <li className="divider"></li>
                            <li><a href="/transaction">Transactions</a></li>
                            <li className="divider"></li>
                            <li><a href="/request-history">Request History</a></li>
                            <li className="divider"></li>
                            <li><a href="/affiliate-tool" target="_blank">Affiliate Tools</a></li>
                        </ul>
                    </li>
                }
                {showReseller &&
                    <li><a href="reseller">Reseller</a></li>
                }
            </ul>
        </div>
    )
}

export default Footer