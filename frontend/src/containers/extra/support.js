import React from 'react'

const Page = ({ history }) => {

    return (
        <div>
            <div className="sub-header alt-3">
                <div className="message">
                    <div className="row">
                        <div className="small-12 columns">
                            <div className="message-intro">
                                <span className="message-line"></span>
                                <p>Support</p>
                                <span className="message-line"></span>
                            </div>
                            <h1>HOW CAN WE HELP?</h1>
                        </div>
                    </div>
                </div>
            </div>

            <div className="support-subheader">
                <div className="row">
                    <div className="small-12 columns">
                        <h2>WE SUPPORT OUR CUSTOMERS ACROSS CHANNELS</h2>
                        <div className="spacing-top-50"></div>
                        <div className="row collapse supportchannels" data-equalizer>
                            <div className="small-12 large-4 large-offset-1 medium-4 medium-offset-1 columns" data-equalizer-watch>
                                <div data-wow-delay="0.3s" className="timeline-content wow fadeInLeft">
                                    <h3>Traditional Email Support</h3>
                                    <p>Please ask for support by send an email to us with header of email prefix <b>[Require Support]</b>. One of our supporters will contact you via email ASAP.</p>
                                    <a href="mailto:support@storagon.com" className="small radius email button">SEND A SUPPORT E-MAIL</a>
                                </div>
                            </div>

                            <div className="large-1 large-offset-1 medium-1 medium-offset-1 hide-for-small line columns" data-equalizer-watch>
                                <div className="roundimg wow fadeInUp"><img src="/static/assets/frontend/images/icons/support_icon_1.png" alt="" /></div>
                            </div>

                            <div className="small-12 large-4 large-offset-1 medium-4 medium-offset-1 columns" data-equalizer-watch>
                                <div data-wow-delay="0.3s" className="timeline-content wow fadeInRight"><img src="/static/assets/frontend/images/email-mockup.png" alt="" className="imgpaddingright" /></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Page