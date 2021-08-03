import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Takedown from 'containers/extra/takedown'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Takedown />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page