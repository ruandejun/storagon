import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Developer from 'containers/extra/developer'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Developer />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page