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
                    <h5>Request History</h5>
                    <table role="grid" className="table fixed_layout">
                        <thead>
                            <tr>
                                <th>Action</th>
                                <th>Status</th>
                                <th>Created date</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr ng-repeat="applyHistory in applyHistories">
                                <td>applyHistory.apply_type | enumApplyType</td>
                                <td className="{{ (applyHistory.apply_status === 0 || applyHistory.apply_status === 1) ? 'success' : 'danger' }}">applyHistory.apply_status | enumApplyStatus</td>
                                <td>applyHistory.created_date | date</td>
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