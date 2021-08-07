import React, { useEffect } from 'react'
import SideBar from 'components/SideBar'
import { useSelector, useDispatch } from 'react-redux'

import actions from './redux/action'
import moment from 'moment'

const { getInbox } = actions

const Page = ({ }) => {
    const dispatch = useDispatch()

    useEffect(() => {
        dispatch(getInbox('2014-01-01'))

        return () => { }
    }, [])

    const userInbox = useSelector(state => state.account.inbox)
    const inboxs = userInbox && userInbox.results ? userInbox.results : []

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <div className="clearfix">
                        <h5 className="left">Message Inbox</h5>
                        <button className="button tiny right" data-reveal-id="myModal">
                            Send Message
                        </button>
                        <div id="modal-inbox" className="reveal-modal tiny" data-reveal aria-labelledby="Inbox" aria-hidden="true" role="dialog">
                            <p className="modal-body"></p>
                            <p><a aria-label="Close" className="button success small pull-left close">OK</a></p>
                            <a className="close-reveal-modal" aria-label="Close">&#215;</a>
                        </div>
                    </div>
                    <table role="grid" className="table fixed_layout">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Sender</th>
                                <th>Content</th>
                                <th>Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            {inboxs.map((message) => {
                                return (
                                    <tr >
                                        <td>{message.sid}</td>
                                        <td>{message.data.sender_username}</td>
                                        <td>{message.text}</td>
                                        <td>{moment(message.created).format('hh:mm YYYY-MM-DD')}</td>
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