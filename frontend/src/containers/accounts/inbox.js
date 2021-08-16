import React, { useEffect, useState } from 'react'
import SideBar from 'components/SideBar'
import { useSelector, useDispatch } from 'react-redux'
import loading from '../../assets/images/loading.gif'

import actions from './redux/action'
import moment from 'moment'
import Modal from 'react-modal'
import { fetchApi } from 'actions/api'

const { getInbox } = actions

const Page = ({ }) => {
    const [openModal, setOpenModal] = useState(false)
    const [message, setMessage] = useState('')
    const [errorMessage, setErrorMessage] = useState('')
    const [toUsername, setToUsername] = useState('')
    const [fetching, setFetching] = useState(false)
    const dispatch = useDispatch()

    useEffect(() => {
        dispatch(getInbox('2014-01-01'))

        return () => { }
    }, [])

    const closeModal = () => {
        setOpenModal(false)
        setMessage('')
        setToUsername('')
    }

    const onOpenModal = () => {
        setOpenModal(true)
    }

    const sendMessage = (event) => {
        event.preventDefault()

        if (message.length == 0) {
            setErrorMessage('Message is required')
            return
        }
        if (toUsername.length == 0) {
            setErrorMessage('To username is required')
            return
        }

        setFetching(true)
        setErrorMessage('')
        fetchApi('post', 'clapi/session/sendInboxMessage/', { sid: 0, to_username: toUsername, text: message })
            .then((data) => {
                console.log({ data })
                setFetching(false)

                if(data && data.session_id){
                    closeModal()
                    dispatch(getInbox('2014-01-01'))
                } else if(data && data.error){
                    setErrorMessage(data.error)
                } else {
                    setErrorMessage('Failed to send message. Please try again')
                }
            })
            .catch((error) => {
                console.log({ error })
                setFetching(false)
                setErrorMessage('Failed to send message. Please try again')
            })
    }

    const userInbox = useSelector(state => state.account.inbox)
    const inboxs = userInbox && userInbox.results ? userInbox.results : []

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <div className="clearfix">
                        <h5 className="left">Message Inbox</h5>
                        <button onClick={onOpenModal} className="button tiny right" data-reveal-id="myModal">
                            Send Message
                        </button>
                        <div id="modal-inbox" className="reveal-modal tiny" data-reveal aria-labelledby="Inbox" aria-hidden="true" role="dialog">
                            <p className="modal-body"></p>
                            <p><a aria-label="Close" className="button success small pull-left close">OK</a></p>
                            <a className="close-reveal-modal" aria-label="Close">&#215;</a>
                        </div>
                    </div>
                    <table role="grid" className="table fixed_layout">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Sender</th>
                                <th>Content</th>
                                <th>Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            {inboxs.map((message) => {
                                return (
                                    <tr >
                                        <td>{message.sid}</td>
                                        <td>{message.data.sender_username}</td>
                                        <td>{message.text}</td>
                                        <td>{moment(message.created).format('hh:mm YYYY-MM-DD')}</td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                </div>

                <SideBar />
            </div>

            <Modal
                isOpen={openModal}
                onRequestClose={closeModal}
                style={customStyles}
            >
                <div className="row">
                    <div className="large-12 columns">
                        <form id="contactform">
                            <h4>Compose new message</h4>
                            <p>
                                <label for="name">To:*</label>
                                <input required type="text" name="name" id="name" tabindex="1" ng-model="to_username" value={toUsername} onChange={event => setToUsername(event.target.value)} />
                            </p>
                            <p>
                                <label for="message">Message:*</label>
                                <textarea required name="message" id="message" cols="12" rows="6" tabindex="3" ng-model="message" value={message} onChange={event => setMessage(event.target.value)}></textarea>
                            </p>
                            <button onClick={sendMessage} className="button radius small">Send</button>
                        </form>
                        {errorMessage && errorMessage.length > 0 &&
                            <div data-alert className="alert-box alert radius" ng-show="error">
                                {errorMessage}
                            </div>
                        }
                        {fetching &&
                            <div className="loader" style={{ display: 'block' }}>
                                <img id="loading-image" src={loading} alt="Loading..." />
                            </div>
                        }
                    </div>
                </div>
            </Modal>
        </div>
    )
}

export default Page

const customStyles = {
    content: {
        top: '50%',
        left: '50%',
        right: 'auto',
        bottom: 'auto',
        marginRight: '-50%',
        transform: 'translate(-50%, -50%)',
        width: '560px',
        backgroundColor: 'white'
    },
}