import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Billing from 'containers/accounts/billing'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Billing />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page