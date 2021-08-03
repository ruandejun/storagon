import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Report from 'containers/accounts/report'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Report />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page