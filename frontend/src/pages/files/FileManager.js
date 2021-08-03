import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import FileManager from 'containers/files/FileManager'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        <FileManager />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page