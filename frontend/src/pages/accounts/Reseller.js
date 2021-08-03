import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Reseller from 'containers/accounts/reseller'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Reseller />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page