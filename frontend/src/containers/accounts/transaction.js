import React, { useEffect, useState } from 'react'
import SideBar from 'components/SideBar'
import { useSelector, useDispatch } from 'react-redux'
import { TransactionType, TransactionTypeFilter } from 'actions/constants'
import moment from 'moment'

import actions from './redux/action'

const { getTransaction } = actions

const Page = ({ }) => {
    const dispatch = useDispatch()
    const [type, setType] = useState(TransactionType.agency)
    const websiteTransaction = useSelector(state => state.account.website)
    const refererTransaction = useSelector(state => state.account.referer)
    const agencyTransaction = useSelector(state => state.account.agency)
    const [fromDate, setFromDate] = useState(moment().subtract(7, 'days').format('YYYY-MM-DD'))
    const [toDate, setToDate] = useState(moment().format('YYYY-MM-DD'))

    useEffect(() => {
        dispatch(getTransaction(fromDate, toDate, type))

        return () => { }
    }, [])

    const changeType = (transaction_type) => {
        setType(transaction_type)
        dispatch(getTransaction(fromDate, toDate, transaction_type))
    }

    const onChangeToDate = (event) => {
        setToDate(event.target.value)

        dispatch(getTransaction(fromDate, event.target.value, type))
    }

    const onChangeFromDate = (event) => {
        setFromDate(event.target.value)

        dispatch(getTransaction(event.target.value, toDate, type))
    }

    const websites = websiteTransaction && websiteTransaction.transactionList ? JSON.parse(websiteTransaction.transactionList) : []
    const referers = refererTransaction && refererTransaction.transactionList ? JSON.parse(refererTransaction.transactionList) : []
    const agencys = agencyTransaction && agencyTransaction.transactionList ? JSON.parse(agencyTransaction.transactionList) : []

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <ul className="tabs" data-tab="" id="affiliate-tab">
                        <li className={`tab-title${type === TransactionType.agency ? ' active' : ''}`}><a onClick={() => changeType(TransactionType.agency)} aria-selected="true" tabindex="0">Agency Transaction</a></li>
                        <li className={`tab-title${type === TransactionType.referer ? ' active' : ''}`}><a onClick={() => changeType(TransactionType.referer)} aria-selected="false" tabindex="-1">Referer Transaction</a></li>
                        <li className={`tab-title${type === TransactionType.website ? ' active' : ''}`}><a onClick={() => changeType(TransactionType.website)} aria-selected="false" tabindex="-1">Website Transaction</a></li>
                    </ul>
                    <div className="tabs-content">
                        {type === TransactionType.agency &&
                            <div className="content active" id="agency" aria-hidden="false">
                                <h4 className="session-title">Agency Transaction ( 60% of your bills )</h4>
                                <div className="input-append date right">
                                    <label>To</label>
                                    <input className="span2 toDate" size="16" type="date" value={toDate} onChange={onChangeToDate} />
                                </div>
                                <div className="input-append date right">
                                    <label>From</label>
                                    <input className="span2 fromDate" size="16" type="date" value={fromDate} onChange={onChangeFromDate} />
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
                                        {agencys.map((item) => {
                                            return (
                                                <tr>
                                                    <td>key</td>
                                                    <td>$0</td>
                                                    <td>$value.fields.invoice_amount | amount</td>
                                                    <td>value.fields.data.userfile_id</td>
                                                    <td>value.fields.created_date | date</td>
                                                </tr>
                                            )
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        }
                        {type === TransactionType.referer &&
                            <div className="content active" id="referrer" aria-hidden="true" tabindex="-1">
                                <h4 className="session-title">Referrer Transaction ( 10% of your referrer's agency program )</h4>
                                <div className="input-append date right">
                                    <label>To</label>
                                    <input className="span2 toDate" size="16" type="date" value={toDate} onChange={onChangeToDate} />
                                </div>
                                <div className="input-append date right">
                                    <label>From</label>
                                    <input className="span2 fromDate" size="16" type="date" value={fromDate} onChange={onChangeFromDate} />
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
                                        {referers.map((item) => {
                                            return (
                                                <tr >
                                                    <td>key</td>
                                                    <td>$value.fields.amount | amount</td>
                                                    <td>$value.fields.invoice_amount | amount</td>
                                                    <td>value.fields.username</td>
                                                    <td>value.fields.created_date | date</td>
                                                </tr>
                                            )
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        }
                        {type === TransactionType.website &&
                            <div className="content active" id="website" aria-hidden="true" tabindex="-1">
                                <h4 className="session-title">Website Transaction ( 5% of bills originated from your websites )</h4>
                                <div className="input-append date right">
                                    <label>To</label>
                                    <input className="span2 toDate" size="16" type="date" value={toDate} onChange={onChangeToDate} />
                                </div>
                                <div className="input-append date right">
                                    <label>From</label>
                                    <input className="span2 fromDate" size="16" type="date" value={fromDate} onChange={onChangeFromDate} />
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
                                        {websites.map((item) => {
                                            return (
                                                <tr >
                                                    <td>key</td>
                                                    <td>$value.fields.amount | amount</td>
                                                    <td>$value.fields.invoice_amount | amount</td>
                                                    <td>value.fields.data.website_origin</td>
                                                    <td>value.fields.created_date | date</td>
                                                </tr>
                                            )
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        }
                    </div>
                </div>

                <SideBar />
            </div>
        </div>
    )
}

export default Page