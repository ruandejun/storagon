import React, { Fragment, useState, useEffect } from 'react'
import Footer from 'components/Footer'
import Header from 'components/Header'
import Register from 'containers/sessions/register'
// import {
//     useGoogleReCaptcha,
//     GoogleReCaptchaProvider
// } from 'react-google-recaptcha-v3'

const Page = ({ history }) => {

    return (
        <Fragment>
            <Header />
            <div className="content">
                <div id="main">
                    <div autoscroll="">
                        {/* <GoogleReCaptchaProvider reCaptchaKey="6Lfp9dUbAAAAAJFo7tgCpkq9geBt2hGaU8w6Mv7n">
                            <Register />
                        </GoogleReCaptchaProvider> */}
                        <Register />
                    </div>
                </div>
            </div>
            <Footer />
        </Fragment>
    )
}

export default Page