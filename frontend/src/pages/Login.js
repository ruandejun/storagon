import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Login from 'containers/sessions/login'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Login />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page