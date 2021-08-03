import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Manage from 'containers/accounts/manage'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Manage />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page