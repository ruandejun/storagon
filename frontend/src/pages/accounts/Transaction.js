import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Transaction from 'containers/accounts/transaction'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Transaction />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page