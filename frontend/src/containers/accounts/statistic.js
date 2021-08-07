import React, { useEffect, useState } from 'react'
import SideBar from 'components/SideBar'
import { useSelector, useDispatch } from 'react-redux'
import moment from 'moment'

import actions from './redux/action'
import Token from 'actions/token'

const { getStatistic, getDownloadSession } = actions

const Page = ({ }) => {
    const dispatch = useDispatch()
    const user = useSelector(state => state.auth.currentUser)
    const userStatistic = useSelector(state => state.account.statistic)
    const userDownloadSession = useSelector(state => state.account.downloadSessions)
    const [fromDate, setFromDate] = useState(moment().subtract(7, 'days').format('YYYY-MM-DD'))
    const [toDate, setToDate] = useState(moment().format('YYYY-MM-DD'))
    const [type, setType] = useState('overview')
    const [perpage, setPerpage] = useState(25)

    useEffect(() => {
        getData(type, fromDate, toDate)

        return () => { }
    }, [])

    const getData = (view_type, from_date, to_date, page_size=perpage) => {
        if (view_type == 'overview') {
            dispatch(getStatistic(from_date, to_date))
        } else if (view_type == 'downloadSessions') {
            if (page_size === 0) {
                dispatch(getDownloadSession(from_date, to_date, null, null, user ? user.id : 0))
            } else {
                dispatch(getDownloadSession(from_date, to_date, 1, page_size, user ? user.id : 0))
            }

        }
    }

    const changeType = (view_type) => {
        setType(view_type)

        getData(view_type, fromDate, toDate)
    }

    const onChangeToDate = (event) => {
        setToDate(event.target.value)

        getData(type, fromDate, event.target.value)
    }

    const onChangeFromDate = (event) => {
        setFromDate(event.target.value)

        getData(type, event.target.value, toDate)
    }

    const onChangePerpage = (event) => {
        setPerpage(parseInt(event.target.value))

        getData(type, fromDate, toDate, parseInt(event.target.value))
    }

    const transactionStatsitic = userStatistic ? userStatistic : {}
    const downloadCounts = userDownloadSession && userDownloadSession.results ? userDownloadSession.results : []

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <ul className="tabs" data-tab="">
                        <li className={`tab-title${type == 'overview' ? ' active' : ''}`}><a onClick={() => changeType('overview')} aria-selected="true" tabIndex={type == 'overview' ? '0' : '-1'}>Overview</a></li>
                        <li className={`tab-title${type == 'downloadSessions' ? ' active' : ''}`}><a onClick={() => changeType('downloadSessions')} aria-selected="false" tabIndex={type == 'downloadSessions' ? '0' : '-1'}>Download Sessions</a></li>
                        <li className={`tab-title${type == 'downloadCountChart' ? ' active' : ''}`}><a onClick={() => changeType('downloadCountChart')} aria-selected="false" tabIndex={type == 'downloadCountChart' ? '0' : '-1'}>Download Count Chart</a></li>
                        <li className={`tab-title${type == 'myOriginalUser' ? ' active' : ''}`}><a onClick={() => changeType('myOriginalUser')} aria-selected="false" tabIndex={type == 'myOriginalUser' ? '0' : '-1'}>My Original User</a></li>
                    </ul>
                    <div className="tabs-content">
                        {type == 'overview' &&
                            <div className="content active" id="overview" aria-hidden="false">
                                <h4 className="session-title">Overview</h4>
                                <div className="input-append date right">
                                    <label>To</label>
                                    <input className="span2 toDate" size="16" type="text" value={toDate} onChange={onChangeToDate} />
                                </div>
                                <div className="input-append date right">
                                    <label>From</label>
                                    <input className="span2 fromDate" size="16" type="text" value={fromDate} onChange={onChangeFromDate} />
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
                                        {Object.keys(transactionStatsitic).map((key) => {
                                            const value = transactionStatsitic[key]
                                            return (
                                                <tr key={key}>
                                                    <td>{key}</td>
                                                    <td>{value.ppd[0] + value.downloadRaw[0]} / ${value.ppd[1]}</td>
                                                    <td>{value.bill[0]} / {value.bill[1]}</td>
                                                    <td>{value.rebill[0]} / {value.rebill[1]}</td>
                                                    <td>{value.website[0]} / {value.website[1]}</td>
                                                    <td>{value.referer[0]} / {value.referer[1]}</td>
                                                    <td>{value.refererPPD[0]} / {value.refererPPD[1]}</td>
                                                    <td>{value.totalOverall}</td>
                                                </tr>
                                            )
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        }
                        {type == 'downloadSessions' &&
                            <div className="content active" id="downloadSessions" aria-hidden="true">
                                <h4 className="session-title">Download Sessions</h4>
                                <div className="input-append date right">
                                    <label>To</label>
                                    <input className="span2 toDate" size="16" type="text" value={toDate} onChange={onChangeToDate} />
                                </div>
                                <div className="input-append date right">
                                    <label>From</label>
                                    <input className="span2 fromDate" size="16" type="text" value={fromDate} onChange={onChangeFromDate} />
                                </div>
                                <select id="download-count-perpage" className="right" value={perpage} onChange={onChangePerpage}>
                                    <option value={25} >25 Items</option>
                                    <option value={50} >50 Items</option>
                                    <option value={0} >Show All</option>
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
                                        {downloadCounts.map((downloadCount) => {
                                            return (
                                                <tr>
                                                    <td data-tooltip aria-haspopup="true" className="has-tip" title="{downloadCount.data.website_url}">{downloadCount.data.file_name}</td>
                                                    <td>{downloadCount.data.iso_code}</td>
                                                    <td>{downloadCount.data.file_size}</td>
                                                    <td className={(downloadCount.status && downloadCount.status === 'completed') ? 'success' : 'danger'}>{downloadCount.status}</td>
                                                    <td>{downloadCount.created}</td>
                                                </tr>
                                            )
                                        })}

                                    </tbody>
                                </table>
                                <ul className='pagination right' id='session_pagination' role='menubar' aria-label='Pagination'></ul>
                            </div>
                        }
                        {type == 'downloadCountChart' &&
                            <div className="content active" id="downloadCountChart" aria-hidden="true" >
                                <div className="input-append date right">
                                    <label>To</label>
                                    <input className="span2 toDate" size="16" type="text" value={toDate} onChange={onChangeToDate} />
                                </div>
                                <div className="input-append date right">
                                    <label>From</label>
                                    <input className="span2 fromDate" size="16" type="text" value={fromDate} onChange={onChangeFromDate} />
                                </div>
                                <div id="linechartDownload" className="highchart"></div>
                            </div>
                        }
                        {type == 'myOriginalUser' &&
                            <div className="content active" id="myOriginalUser" aria-hidden="true">
                                <div className="input-append date right">
                                    <label>To</label>
                                    <input className="span2 toDate" size="16" type="text" value={toDate} onChange={onChangeToDate} />
                                </div>
                                <div className="input-append date right">
                                    <label>From</label>
                                    <input className="span2 fromDate" size="16" type="text" value={fromDate} onChange={onChangeFromDate} />
                                </div>
                                <div id="linechartOriginalUser" className="highchart"></div>
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