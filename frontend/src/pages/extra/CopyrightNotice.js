import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import CopyrightNotice from 'containers/extra/copyright_notice'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <CopyrightNotice />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page