import React, { Fragment, useState, useEffect, useCallback, styl } from 'react'
import SideBar from 'components/SideBar'

const Page = ({ history }) => {

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <ul className="tabs" data-tab="">
                        <li className="tab-title active"><a href="overview" aria-selected="true" tabindex="0">Overview</a></li>
                        <li className="tab-title"><a href="downloadSessions" aria-selected="false" tabindex="-1">Download Sessions</a></li>
                        <li className="tab-title"><a href="downloadCountChart" aria-selected="false" tabindex="-1">Download Count Chart</a></li>
                        <li className="tab-title"><a href="myOriginalUser" aria-selected="false" tabindex="-1">My Original User</a></li>
                    </ul>
                    <div className="tabs-content">
                        <div className="content active" id="overview" aria-hidden="false">
                            <h4 className="session-title">Overview</h4>
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
                                        <th>Date</th>
                                        <th>Downloads</th>
                                        <th>Premium Sales</th>
                                        <th>Re-bills</th>
                                        <th>Site Sales</th>
                                        <th>Referrals</th>
                                        <th>Referrals PPD</th>
                                        <th>Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr ng-repeat="(key, value) in transactionStatsitic">
                                        <td>key</td>
                                        <td>value.ppd[0] + value.downloadRaw[0] / $value.ppd[1] | amount</td>
                                        <td>value.bill[0] / $value.bill[1] | amount</td>
                                        <td>value.rebill[0] / $value.rebill[1] | amount</td>
                                        <td>value.website[0] / $value.website[1] | amount</td>
                                        <td>value.referer[0]/ $value.referer[1] | amount</td>
                                        <td>value.refererPPD[0] / $value.refererPPD[1] | amount</td>
                                        <td>$value.totalOverall</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div className="content" id="downloadSessions" aria-hidden="true" tabindex="-1">
                            <h4 className="session-title">Download Sessions</h4>
                            <div className="input-append date right">
                                <label>To</label>
                                <input className="span2 toDate" size="16" type="text" />
                            </div>
                            <div className="input-append date right">
                                <label>From</label>
                                <input className="span2 fromDate" size="16" type="text" />
                            </div>
                            <select id="download-count-perpage" className="right">
                                <option value="25" selected>25 Items</option>
                                <option value="50">50 Items</option>
                                <option value="0">Show All</option>
                            </select>
                            <input type="hidden" id="totalRecords" />
                            <hr />
                            <table role="grid" className="table fixed_layout">
                                <thead>
                                    <tr>
                                        <th width="40%">Name</th>
                                        <th>Country</th>
                                        <th>Size</th>
                                        <th>Status</th>
                                        <th>Created</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr ng-repeat="downloadCount in downloadCounts">
                                        <td data-tooltip aria-haspopup="true" className="has-tip" title="{downloadCount.data.website_url}">downloadCount.data.file_name</td>
                                        <td>downloadCount.data.iso_code</td>
                                        <td>downloadCount.data.file_size | filesize</td>
                                        <td className="{(downloadCount.status| enumSessionStatus: downloadCount.status === 'completed') ? 'success' : 'danger'}">downloadCount.status | enumSessionStatus</td>
                                        <td>downloadCount.created</td>
                                    </tr>
                                </tbody>
                            </table>
                            <ul class='pagination right' id='session_pagination' role='menubar' aria-label='Pagination'></ul>
                        </div>
                        <div className="content" id="downloadCountChart" aria-hidden="true" tabindex="-1">
                            <div className="input-append date right">
                                <label>To</label>
                                <input className="span2 toDate" size="16" type="text" />
                            </div>
                            <div className="input-append date right">
                                <label>From</label>
                                <input className="span2 fromDate" size="16" type="text" />
                            </div>
                            <div id="linechartDownload" className="highchart"></div>
                        </div>
                        <div className="content" id="myOriginalUser" aria-hidden="true" tabindex="-1">
                            <div className="input-append date right">
                                <label>To</label>
                                <input className="span2 toDate" size="16" type="text" />
                            </div>
                            <div className="input-append date right">
                                <label>From</label>
                                <input className="span2 fromDate" size="16" type="text" />
                            </div>
                            <div id="linechartOriginalUser" className="highchart"></div>
                        </div>
                    </div>
                </div>

                <SideBar />
            </div>
        </div>
    )
}

export default Page