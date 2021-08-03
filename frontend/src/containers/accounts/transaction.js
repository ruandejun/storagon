import React, { Fragment, useState, useEffect, useCallback, styl } from 'react'
import SideBar from 'components/SideBar'

const Page = ({ history }) => {

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <ul className="tabs" data-tab="" id="affiliate-tab">
                        <li className="tab-title active"><a href="#agency" aria-selected="true" tabindex="0">Agency Transaction</a></li>
                        <li className="tab-title"><a href="#referrer" aria-selected="false" tabindex="-1">Referer Transaction</a></li>
                        <li className="tab-title"><a href="#website" aria-selected="false" tabindex="-1">Website Transaction</a></li>
                    </ul>
                    <div className="tabs-content">
                        <div className="content active" id="agency" aria-hidden="false">
                            <h4 className="session-title">Agency Transaction ( 60% of your bills )</h4>
                            <div className="input-append date right">
                                <label>To</label>
                                <input className="span2 toDate" size="16" type="text" />
                            </div>
                            <div className="input-append date right">
                                <label>From</label>
                                <input className="span2 fromDate" size="16" type="text" />
                            </div>
                            <hr />
                            <table role="grid" className="table fixed_layout">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Transaction Amount</th>
                                        <th>Bill Amount</th>
                                        <th>User's File ID</th>
                                        <th>Created</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr ng-repeat="(key, value) in agencyData">
                                        <td>key</td>
                                        <td>$0</td>
                                        <td>$value.fields.invoice_amount | amount</td>
                                        <td>value.fields.data.userfile_id</td>
                                        <td>value.fields.created_date | date</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div className="content" id="referrer" aria-hidden="true" tabindex="-1">
                            <h4 className="session-title">Referrer Transaction ( 10% of your referrer's agency program )</h4>
                            <div className="input-append date right">
                                <label>To</label>
                                <input className="span2 toDate" size="16" type="text" />
                            </div>
                            <div className="input-append date right">
                                <label>From</label>
                                <input className="span2 fromDate" size="16" type="text" />
                            </div>
                            <hr />
                            <table role="grid" className="table fixed_layout">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Transaction Amount</th>
                                        <th>Bill Amount</th>
                                        <th>Referrer</th>
                                        <th>Created</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr ng-repeat="(key, value) in refererData">
                                        <td>key</td>
                                        <td>$value.fields.amount | amount</td>
                                        <td>$value.fields.invoice_amount | amount</td>
                                        <td>value.fields.username</td>
                                        <td>value.fields.created_date | date</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div className="content" id="website" aria-hidden="true" tabindex="-1">
                            <h4 className="session-title">Website Transaction ( 5% of bills originated from your websites )</h4>
                            <div className="input-append date right">
                                <label>To</label>
                                <input className="span2 toDate" size="16" type="text" />
                            </div>
                            <div className="input-append date right">
                                <label>From</label>
                                <input className="span2 fromDate" size="16" type="text" />
                            </div>
                            <hr />
                            <table role="grid" className="table fixed_layout">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Transaction Amount</th>
                                        <th>Bill Amount</th>
                                        <th>Website</th>
                                        <th>Created</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr ng-repeat="(key, value) in websiteData">
                                        <td>key</td>
                                        <td>$value.fields.amount | amount</td>
                                        <td>$value.fields.invoice_amount | amount</td>
                                        <td>value.fields.data.website_origin</td>
                                        <td>value.fields.created_date | date</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <SideBar />
            </div>
        </div>
    )
}

export default Page