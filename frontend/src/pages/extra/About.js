import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import About from 'containers/extra/about'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <About />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page