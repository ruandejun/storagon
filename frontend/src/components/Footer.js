import React from 'react'

const Footer = ({ }) => {
    return (
        <footer>
            <div className="row">
                <div className="small-12 columns">
                    <div className="contacts">
                        <div className="row">
                            <div className="small-12 large-4 medium-4 columns">
                                <i className="fa fa-map-marker"></i>
                                SINGAPORE
                            </div>
                            <div className="small-12 large-4 medium-4 columns">
                                <a id="livechat"><i className="fa fa-comments"></i></a>
                                LIVE CHAT
                            </div>
                            <div className="small-12 large-4 medium-4 columns">
                                <a href="mailto:support@storagon.com"><i className="fa fa-envelope-o"></i></a>
                                E-MAIL US
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="row">
                <div className="small-12 columns">
                    <div className="footerlinks">

                        <div className="small-12 large-3 medium-3 columns border-right">
                            <h2>Company</h2>
                            <ul>
                                <li><a href="/about" target="_blank">About us</a></li>
                                <li><a href="/blog" target="_blank">Blog</a></li>
                                <li><a href="/devs" target="_blank">Developers</a></li>
                            </ul>
                        </div>

                        <div className="small-12 large-3 medium-3 columns border-right">
                            <h2>Tools</h2>
                            <ul>
                                <li><a href="">Sync Client</a></li>
                                <li><a href="">Mobile Apps</a></li>
                                <li><a href="/download-tool" target="_blank">Desktop Apps</a></li>
                            </ul>
                        </div>

                        <div className="small-12 large-3 medium-3 columns border-right">
                            <h2>Information</h2>
                            <ul>
                                <li><a href="/support" target="_blank">Support</a></li>
                                <li><a href="/takedown" target="_blank">Takedown Guidance</a></li>
                                <li><a href="/cprnotice" target="_blank">Copyright Notice</a></li>
                            </ul>
                        </div>

                        <div className="small-12 large-3 medium-3 columns">
                            <h2>Legal</h2>
                            <ul>
                                <li><a href="/tos" target="_blank">Terms of Service</a></li>
                                <li><a href="/privacy" target="_blank">Privacy Policy</a></li>
                                <li><a href="/copyright" target="_blank">Copyright</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <div className="social">
                <div className="row">
                    <div className="small-12 columns">
                        <ul className="small-block-grid-1 large-block-grid-5 medium-block-grid-5">
                            <li className="facebook"><a href="">FACEBOOK</a></li>
                            <li className="twitter"><a href="">TWITTER</a></li>
                            <li className="googleplus"><a href="">GOOGLE+</a></li>
                        </ul>
                    </div>
                </div>
            </div>
            <p className="copyright">© Copyright Storagon, all rights reserved. </p>
        </footer>
    )
}

export default Footer