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

    const userBilling = useSelector((state) => state.account.billing)
    const bills = userBilling ? userBilling : []

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
                            {bills.map(bill => {
                                return (
                                    <tr>
                                        <td>{bill.pk}</td>
                                        <td>{bill.fields.plan_id}</td>
                                        <td className="success">{bill.fields.money_charged}</td>
                                        <td>{bill.fields.created_date}</td>
                                        <td>{bill.fields.detail._id}</td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                </div>

                <SideBar />
            </div>
        </div>
    )
}

export default Page