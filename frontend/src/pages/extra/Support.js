import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Support from 'containers/extra/support'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Support />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page