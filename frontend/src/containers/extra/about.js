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
                                <p>Storagon</p>
                                <span className="message-line"></span>
                            </div>
                            <h1>Privacy Company</h1>
                        </div>
                    </div>
                </div>
            </div>

            <div className="padding-top-30 padding-bottom-30 aboutus-subheader">
                <div className="row">
                    <div className="small-12 columns">
                        <h2>About us</h2>
                        <p>When we launched Storagon early 2015, global mass surveillance by rogue governments under the pretext of fighting terrorism
                            was still a wild conjecture and its proponents were often touted as conspiracy theorists.
                            Anything short of <i>security by design</i> ("we cannot gain access to your data without you being able to find out"),
                            for which strong end-to-end encryption is an essential prerequisite, now seems grossly insufficient.</p>
                        <p>Storagon was architected around the simple fact that cryptography, for it to be accepted and used, must not interfere with usability.
                            Storagon is fully accessible without prior software installs and remains the only cloud storage provider with browser-based high-performance end-to-end encryption.
                            The only visible signs of the crypto layer operating under Storagon's hood are the entropy collection during signup, the lack of a password reset feature and the novel (and browser-specific) ways file transfers are conducted.
                            Today, millions of business and personal users rely on Storagon to securely and reliably store and serve petabytes of data and we believe that this success is the result of Storagon's low barrier to entry to a more secure cloud.</p>
                        <p>We are constantly hiring. If you are an outstanding software engineer and would like to join our global team, please do not hesitate to submit your CV to <a href="mailto:jobs@storagon.com">jobs@storagon.com</a></p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Page