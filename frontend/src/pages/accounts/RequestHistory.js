import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import RequestHistory from 'containers/accounts/request_history'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <RequestHistory />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page