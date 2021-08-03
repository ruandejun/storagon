import React, { Fragment, useState, useEffect, useCallback, styl } from 'react'
import SideBar from 'components/SideBar'

const Page = ({ history }) => {

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
                            <tr ng-repeat="message in inboxMessages">
                                <td>message.sid</td>
                                <td>message.data.sender_username</td>
                                <td>message.text</td>
                                <td>message.created.$date | date</td>
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