import React, {useEffect, useState} from 'react'
import { bounceInLeft, fadeInLeft, fadeInRight } from 'react-animations'
import styled, { keyframes } from 'styled-components'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCloud, faLock, faSync } from '@fortawesome/free-solid-svg-icons'

const bounceAnimation = keyframes`${bounceInLeft}`;
const fadeLeftAnimation = keyframes`${fadeInLeft}`;
const fadeRightAnimation = keyframes`${fadeInRight}`;

const BounceInLeft = styled.div`
  animation: 1s ${bounceAnimation};
`;

const FadeInLeft = styled.li`
  animation: 1s ${fadeLeftAnimation};
`;

const FadeInRight = styled.li`
  animation: 1s ${fadeRightAnimation};
`;

const Page = ({ history }) => {

    const [welcomeText, setWelcomeText] = useState(1)

    useEffect(() => {
        const interval = setInterval(() => {
            if (welcomeText == 1) {
                setWelcomeText(2)
            } else {
                setWelcomeText(1)
            }
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div>
            <div className="sub-header alt-3">
                <div className="message">
                    <div className="row">
                        <div className="small-12 columns">
                            <div className="message-intro">
                                <span className="message-line"></span>
                                <p>Secure Cloud Storage</p>
                                <span className="message-line"></span>
                            </div>
                            <h1><span>
                                {welcomeText == 1 &&
                                    <BounceInLeft>
                                        <span className="animated">{'YOUR FILES WHEREVER YOU ARE'}</span>
                                    </BounceInLeft>
                                }
                                {welcomeText == 2 &&
                                    <BounceInLeft>
                                        <span className="animated">{'100% SAFE AND SECURE'}</span>
                                    </BounceInLeft>
                                }
                            </span></h1>
                            <a href="/signup" className="small radius button">Get Started</a>
                        </div>
                    </div>
                </div>
            </div>
            <section className="features">
                <div className="row">
                    <div className="small-12 columns">
                        <h2>OUR FEATURES ARE UNBEATABLE</h2>
                        <ul className="small-block-grid-1 large-block-grid-3 medium-block-grid-3">
                            <FadeInLeft>
                                <i><FontAwesomeIcon icon={faCloud} /></i>
                                <h3>All your media, anywhere you go</h3>
                                <p>Storagon stores all your media and makes it available to you anytime you want it, anywhere you go, on any device you have. With Storagon your files are always with you.</p>
                            </FadeInLeft>

                            <FadeInLeft>
                            <i><FontAwesomeIcon icon={faSync} /></i>
                                <h3>Synchonize Your Files</h3>
                                <p>Quickly and easily drag individual files to your folder app on your computer. It's a simple way to sync files straight to all your devices.</p>
                            </FadeInLeft>

                            <FadeInRight>
                            <i><FontAwesomeIcon icon={faLock} /></i>
                                <h3>Complete Data Security</h3>
                                <p>Unlike with other cloud storage providers, your data is encrypted & decrypted during transfer by your client devices only and never by us.</p>
                            </FadeInRight>
                        </ul>
                    </div>
                </div>
            </section>
        </div>
    )
}

export default Page