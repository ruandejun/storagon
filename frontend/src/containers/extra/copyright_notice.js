import React from 'react'
import loading from '../../assets/images/ajax-spinner.gif'

const Page = ({ history }) => {

    return (
        <div>
            <div className="sub-header alt-3">
                <div className="message">
                    <div className="row">
                        <div className="small-12 columns">
                            <div className="message-intro">
                                <span className="message-line"></span>
                                <p>Copyright Notice</p>
                                <span className="message-line"></span>
                            </div>
                            <h1>Fillin this form below to notice copyright infringes</h1>
                        </div>
                    </div>
                </div>
            </div>

            <div className="padding-top-30 padding-bottom-30 aboutus-subheader">
                <div className="row">
                    <div className="small-12 columns">
                        <div id="cprnotice">
                            <div data-alert className="alert-box alert radius">
                                This notification is a serious legal document - please be careful to be accurate in your copyright infringement claims. You may wish to first consult with an attorney to determine whether the content you are reporting is in fact infringing and not protected by fair use, license, or other legal basis.
                                <a className="close">&times;</a>
                            </div>
                            <form id="profile_form" novalidate="novalidate">
                                <div className="row">
                                    <div className="large-12 columns">
                                        <div className="loader">
                                            <img id="loading-image" src={loading} alt="Loading..." />
                                        </div>
                                        <p>
                                            <label for="detail">Please select detail of notice:</label>
                                            <select name="detail" id="detail" tabindex="2">
                                                <option value="0">Select</option>
                                                <option value="1">Infringes on my personal copyright.</option>
                                                <option value="2">Infringes on the copyright of someone I am authorized to represent.
                                                </option>
                                            </select>
                                        </p>
                                        <p>
                                            <label for="takedown_type">Please select takedown type:</label>
                                            <select name="takedown_type" id="takedown_type" tabindex="3">
                                                <option value="0">Select</option>
                                                <option value="1">Disable one link ("URL") per file - the file(s) will remain the user's account
                                                </option>
                                                <option value="2">Disable multiple URL's per file - the file(s) will remain the user's account
                                                </option>
                                                <option value="3">Remove all underlying file(s) of the supplied URL(s) - there is no user who is permitted to store this under any circumstance worldwide
                                                </option>
                                                <option value="4">Other</option>
                                            </select>
                                        </p>
                                        <p>
                                            <label for="infringing_url">URL of infringing content:</label>
                                            <input type="text" name="infringing_url" id="infringing_url" tabindex="4" placeholder="https://storagon.com/..." />
                                        </p>
                                        <p>
                                            <label for="document_url">URL of documents to prove copyrighted work claimed to have been infringed:</label>
                                            <input type="text" name="document_url" id="document_url" tabindex="4" placeholder="https://" />
                                        </p>
                                        <p>
                                            <input id="agree-checkbox" type="checkbox" required /><label for="agree-checkbox">I hereby state that I have a good faith belief that
                                                the sharing of copyrighted material at the location above is not authorized by the copyright
                                                owner, its agent, or the law (e.g., as a fair use)</label>
                                        </p>
                                        <button type="submit" className="button">Submit</button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Page