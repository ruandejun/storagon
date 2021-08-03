import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Account from 'containers/accounts/account'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Account />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page