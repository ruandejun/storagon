import React, { useEffect } from 'react'
import SideBar from 'components/SideBar'
import { useSelector, useDispatch } from 'react-redux'

import actions from './redux/action'

const { getPremiumKey } = actions

const Page = ({ }) => {
    const dispatch = useDispatch()
    const userPremium = useSelector(state => state.account.premiumKeys)
    const userBalance = useSelector(state => state.account.balance)

    useEffect(() => {
        dispatch(getPremiumKey())

        return () => { }
    }, [])

    console.log({userPremium, userBalance})
    let creditBalance = 0
    if(userBalance && userBalance.length > 0){
        userBalance.map((item) => {
            creditBalance += item.fields.amount
        })
    }

    const credits = userPremium && userPremium.length > 0 ? userPremium : []

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <h4 className="left">Your Current Credit Balance {creditBalance}</h4>
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
                            {credits.map((credit) => {
                                return (
                                    <tr>
                                        <td>{credit.fields.code}</td>
                                        <td>{credit.fields.created_date}</td>
                                        <td>{credit.fields.activated_user}</td>
                                        <td>{credit.fields.activated_date}</td>
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