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
                                <p>Copyright</p>
                                <span className="message-line"></span>
                            </div>
                            <h1>NOTICE OF ALLEGED INFRINGEMENT "NOTICE"</h1>
                        </div>
                    </div>
                </div>
            </div>

            <div className="padding-top-30 padding-bottom-30 aboutus-subheader">
                <div className="row">
                    <div className="small-12 columns">
                        <p>We respect the copyright of others and require that users of our services comply with the laws of copyright. You are strictly prohibited from using our services to infringe copyright. You may not upload, download, store, share, display, stream, distribute, e-mail, link to, transmit or otherwise make available any files, data, or content that infringes any copyright or other proprietary rights of any person or entity. We will respond to notices of alleged copyright infringement that comply with applicable law and are properly provided to us. If you believe that your content has been copied or used in a way that constitutes copyright infringement, please provide us with the following information:</p>
                        <ol>
                            <li>A physical or electronic signature of the copyright owner or a person authorized to act on their behalf</li>
                            <li>Identification of the copyrighted work claimed to have been infringed</li>
                            <li>Identification of the material that is claimed to be infringing or to be the subject of infringing activity and that is to be removed or access to which is to be disabled, and information reasonably sufficient to permit us to locate the material including for example the uniform resource locator(s) (URL)</li>
                            <li>Your contact information, including your address, telephone number, and an email address</li>
                            <li>A statement by you that you have a good faith belief that use of the material in the manner complained of is not authorized by the copyright owner, its agent, or the law</li>
                            <li>A statement that the information in the notification is accurate, and, under penalty of perjury (unless applicable law says otherwise), that you are authorized to act on behalf of the copyright owner</li>
                        </ol>
                        <a href="/cprnotice" className="small button alert radius">You may submit notice here</a>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Page