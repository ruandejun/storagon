import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Privacy from 'containers/extra/privacy'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Privacy />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page