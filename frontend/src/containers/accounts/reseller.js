import React, { Fragment, useState, useEffect, useCallback, styl } from 'react'
import SideBar from 'components/SideBar'

const Page = ({ history }) => {

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <h4 className="left">Your Current Credit Balance creditBalance | currency</h4>
                    <span className="right"><a data-reveal-id="planModal" className="button tiny">Purchase Premium Key</a></span>
                    <hr />
                    <div className="row">
                        <div className="large-12 columns">
                            <h5>Premium Key List</h5>
                        </div>
                    </div>
                    <table role="grid" className="table fixed_layout">
                        <thead>
                            <tr>
                                <th>Premium Code</th>
                                <th>Created</th>
                                <th>UID</th>
                                <th>Activated</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr ng-repeat="credit in credits">
                                <td>credit.fields.code</td>
                                <td>credit.fields.created_date | date</td>
                                <td>credit.fields.activated_user</td>
                                <td>credit.fields.activated_date | date</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <SideBar />
            </div>
        </div>
    )
}

export default Page