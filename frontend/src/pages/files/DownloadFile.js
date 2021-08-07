import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import DownloadFile from 'containers/files/download_file'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <DownloadFile />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page