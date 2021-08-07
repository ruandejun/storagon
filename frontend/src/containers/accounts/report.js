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

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <div className="clearfix">
                        <h5 className="left">Report</h5>
                        <button className="button tiny right" id="report" data-reveal-id="modal-report">
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
                            <tr ng-repeat="report in reports">
                                <td>report.text</td>
                                <td className="{{(report.status| enumSessionStatus: report.status === 'completed') ? 'success' : 'danger'}}">report.status | enumSessionStatus</td>
                                <td>(report.data.detail === "") ? report.data.file_link : report.data.detail</td>
                                <td>report.created | date</td>
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