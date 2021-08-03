import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Redeem from 'containers/accounts/redeem'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Redeem />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page