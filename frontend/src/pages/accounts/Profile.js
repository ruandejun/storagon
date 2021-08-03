import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Profile from 'containers/accounts/profile'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Profile />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page