import Token from 'actions/token'
import React, { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'

const Footer = ({ }) => {
    const [accountMenu, setAccountMenu] = useState(false)
    const [affiliateMenu, setAffiliateMenu] = useState(false)
    let showAffiliate = false
    let showReseller = false
    const user = useSelector(state => state.auth.currentUser)

    if (user && user.profile && user.profile.fields && user.profile.fields.account_type) {
        if (user.profile.fields.account_type == 1 || user.profile.fields.account_type == 3) {
            showAffiliate = true
        } else if (user.profile.fields.account_type == 2) {
            showReseller = true;
        }
    }

    return (
        <div className="large-2 pull-10 columns">
            <p><img className="th" src='http://placehold.it/128x128' /></p>
            <ul className="side-nav">
                <li><a href="/account">Overview</a></li>
                <li>
                    <a onClick={() => setAccountMenu(!accountMenu)}>My Account</a>
                    {accountMenu &&
                        <ul className="hidden-list">
                            <li><a href="/billing">Billing history</a></li>
                            <li className="divider"></li>
                            <li><a href="/redeem">Redeem</a></li>
                            <li className="divider"></li>
                            <li><a href="/profile">Edit Profile</a></li>
                        </ul>
                    }
                </li>
                <li><a href="/inbox">Inbox</a></li>
                <li><a href="/report">Report</a></li>
                {showAffiliate &&
                    <li>
                        <a onClick={() => setAffiliateMenu(!affiliateMenu)}>Affiliate</a>
                        {affiliateMenu &&
                            <ul className="hidden-list">
                                <li><a href="/manage">Dashboard</a></li>
                                <li className="divider"></li>
                                <li><a href="/statistic">Statistic</a></li>
                                <li className="divider"></li>
                                <li><a href="/transaction">Transactions</a></li>
                                <li className="divider"></li>
                                <li><a href="/request-history">Request History</a></li>
                                <li className="divider"></li>
                                <li><a href="/affiliate-tool" target="_blank">Affiliate Tools</a></li>
                            </ul>
                        }
                    </li>
                }
                {showReseller &&
                    <li><a href="/reseller">Reseller</a></li>
                }
            </ul>
        </div>
    )
}

export default Footer