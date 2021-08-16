import React, { useEffect, useState } from 'react'
import SideBar from 'components/SideBar'
import { useSelector, useDispatch } from 'react-redux'
import loading from '../../assets/images/loading.gif'
import Modal from 'react-modal'

import actions from './redux/action'
import { SessionStatusFilter } from 'actions/constants'
import { fetchApi } from 'actions/api'
import moment from 'moment'

const { getReport } = actions

const Page = ({ }) => {
    const [openModal, setOpenModal] = useState(false)
    const [message, setMessage] = useState('')
    const [errorMessage, setErrorMessage] = useState('')
    const [reportType, setReportType] = useState('BUG')
    const [reportUrl, setReportUrl] = useState('')
    const [fetching, setFetching] = useState(false)
    const dispatch = useDispatch()
    const user = useSelector(state => state.auth.currentUser)

    const closeModal = () => {
        setOpenModal(false)
        setMessage('')
        setReportUrl('')
        setReportType('BUG')
    }

    const onOpenModal = () => {
        setOpenModal(true)
    }

    const sendReport = (event) => {
        event.preventDefault()

        if (message.length == 0) {
            setErrorMessage('Report message is required')
            return
        }
        if (reportType.length == 0) {
            setErrorMessage('Report type is required')
            return
        }

        let file_id = 0

        if (reportType == 'DCMA') {
            if (reportUrl.length == 0) {
                setErrorMessage('Report url is required')
                return
            }
            let url_path_array = reportUrl.split('/')
            file_id = url_path_array[2]
        }

        setFetching(true)
        setErrorMessage('')
        fetchApi('post', 'clapi/session/createReport/', { sid: user.user_id, text: reportType, detail: message, fid: file_id })
            .then((data) => {
                console.log({ data })
                setFetching(false)

                if (data && data.session_id) {
                    closeModal()
                    dispatch(getReport('2014-01-01'))
                } else if (data && data.error) {
                    setErrorMessage(data.error)
                } else {
                    setErrorMessage('Failed to send report. Please try again')
                }
            })
            .catch((error) => {
                console.log({ error })
                setFetching(false)
                setErrorMessage('Failed to send report. Please try again')
            })
    }

    useEffect(() => {
        dispatch(getReport('2014-01-01'))

        return () => { }
    }, [])

    const userReport = useSelector(state => state.account.reports)
    const reports = userReport && userReport.results ? userReport.results : []

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <div className="clearfix">
                        <h5 className="left">Report</h5>
                        <button onClick={onOpenModal} className="button tiny right" id="report" data-reveal-id="modal-report">
                            Create report
                        </button>
                    </div>
                    <table role="grid" className="table fixed_layout">
                        <thead>
                            <tr>
                                <th>Report Kind</th>
                                <th>Status</th>
                                <th>Detail</th>
                                <th>Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            {reports.map((report) => {
                                return (
                                    <tr key={report.id.toString()}>
                                        <td>{report.text}</td>
                                        <td className="{{(report.status| enumSessionStatus: report.status === 'completed') ? 'success' : 'danger'}}">{SessionStatusFilter[report.status]}</td>
                                        <td>{(report.data.detail === "") ? report.data.file_link : report.data.detail}</td>
                                        <td>{moment(report.created).format('hh:mm YYYY-MM-DD')}</td>
                                    </tr>
                                )
                            })}

                        </tbody>
                    </table>
                </div>

                <SideBar />
            </div>
            <Modal
                isOpen={openModal}
                onRequestClose={closeModal}
                style={customStyles}
            >
                <form name="report-form" id="report-form">
                    <label for="text">Report type*:</label>
                    <select id="text" ng-model="$parent.text" required="required" onChange={event => setReportType(event.target.value)}>
                        <option value="BUG" selected={reportType === 'BUG'}>BUG</option>
                        <option value="HELP" selected={reportType === 'HELP'}>HELP</option>
                        <option value="DMCA" selected={reportType === 'DMCA'}>DMCA</option>
                    </select>

                    {reportType === 'DMCA' &&
                        <label ng-show="text=='DMCA'" for="file_url">URL:*</label>
                    }
                    {reportType === 'DMCA' &&
                        <input id="file_url" ng-model="$parent.file_url" ng-show="text=='DMCA'" type="text" value={reportUrl} onChange={event => setReportUrl(event.target.value)} />
                    }

                    <label for="detail">Message:*</label>
                    <textarea name="detail" id="detail" cols="12" rows="6" tabindex="3" ng-model="$parent.detail" value={message} onChange={event => setMessage(event.target.value)}></textarea>

                    <div data-alert className="alert-box alert radius">
                        This report is a serious legal document - please be careful to be accurate in your report. You may wish to first notice that Storagon DO NOT take any responbility for your actions.
                    </div>
                    <button onClick={sendReport} type="submit" className="button small">Submit report</button>
                </form>
                {errorMessage && errorMessage.length > 0 &&
                    <div data-alert className="alert-box alert radius" ng-show="error">
                        {errorMessage}
                    </div>
                }
                {fetching &&
                    <div className="loader" style={{ display: 'block' }}>
                        <img id="loading-image" src={loading} alt="Loading..." />
                    </div>
                }
            </Modal>
        </div>
    )
}

export default Page

const customStyles = {
    content: {
        top: '50%',
        left: '50%',
        right: 'auto',
        bottom: 'auto',
        marginRight: '-50%',
        transform: 'translate(-50%, -50%)',
        width: '560px',
        backgroundColor: 'white'
    },
}