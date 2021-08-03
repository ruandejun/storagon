import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Inbox from 'containers/accounts/inbox'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Inbox />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page