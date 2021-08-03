import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Term from 'containers/extra/term'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <Term />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page