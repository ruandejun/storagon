import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Copyright from 'containers/extra/copyright'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Copyright />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page