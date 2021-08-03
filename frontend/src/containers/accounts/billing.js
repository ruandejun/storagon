import React, { Fragment, useState, useEffect, useCallback, styl } from 'react'
import SideBar from 'components/SideBar'

const Page = ({ history }) => {

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <h5>Billing Information</h5>
                    <table role="grid" className="table fixed_layout">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Plan</th>
                                <th>Bill Amount</th>
                                <th>Date</th>
                                <th>Bill ID</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr ng-repeat="bill in bills">
                                <td>bill.pk</td>
                                <td>bill.fields.plan_id</td>
                                <td className="success">bill.fields.money_charged | amount</td>
                                <td>bill.fields.created_date | date</td>
                                <td>bill.fields.detail._id.$oid</td>
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