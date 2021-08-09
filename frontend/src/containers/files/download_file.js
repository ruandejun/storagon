import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { fetchApi } from 'actions/api'
import { convertFilesize, DownloadType } from 'actions/constants'

const Page = () => {

    const [fileName, setFileName] = useState('')
    const [fileSize, setFileSize] = useState(0)
    const { file_id, file_hash } = useParams()
    const [counter, setCounter] = useState(5)

    useEffect(() => {
        setTimeout(() => {
            if (counter > 0) {
                setCounter(counter - 1)
            }
        }, 1000)
    }, [counter])

    useEffect(() => {
        if (file_id, file_hash) {
            fetchApi('get', 'clapi/file/getFile/', { file_id, file_hash: file_hash })
                .then((data) => {
                    try {
                        setFileSize(data.file_size)
                        setFileName(data.file_name)
                    } catch (error) {

                    }
                    console.log({ fileSearch: data })
                })
                .catch((error) => {
                    console.log({ error })
                })
        }


        return () => { }
    }, [])

    const normalDownload = () => {
        fetchApi('post', 'clapi/session/createDownloadSession/', { userFile_id: file_id, download_type: DownloadType.direct })
            .then((data) => {
                console.log({ data })
                if (data && data.download_link) {
                    window.open(data.download_link)
                }
            })
            .catch((error) => {
                console.log({ error })
                alert('Cannot open downlink')
            })
    }

    const torrentDownload = () => {
        fetchApi('post', 'clapi/session/createDownloadSession/', { userFile_id: file_id, download_type: DownloadType.torrent })
            .then((data) => {
                if (data && data.download_link) {
                    window.open(data.download_link)
                }
            })
            .catch((error) => {
                console.log({ error })
            })
    }

    return (
        <div>
            <div className="download-container">
                <div className="text-center">
                    <h3>File Information</h3>
                    <p>Name: <strong>{fileName}</strong></p>
                    <p>Size: <strong>{convertFilesize(fileSize)}</strong></p>
                </div>
                <div className="vertical-padding-top"></div>
                <div className="download-content">
                    <div className="text-center countdown">
                        <h1>
                            <span className="hours">00</span>:
                            <span className="minutes">00</span>:
                            <span className="seconds">{counter.toLocaleString('en-US', { minimumIntegerDigits: 2, useGrouping: false })}</span>
                        </h1>
                    </div>
                    <div className="text-center">
                        <a className="text-center" download="{file_name}"></a>
                    </div>
                    <div className="text-center">
                        {counter === 0 && <h3>Please choose your download type</h3>}
                    </div>
                    <div className="vertical-padding-top"></div>
                    {counter === 0 &&
                        <div className="text-center">
                            <a onClick={normalDownload} className="btnd btn-download" title="Download and decrypt file using browser">Download</a>
                            <a onClick={torrentDownload} className="btnd btn-torrent" title="Download encrypted file with torrent">Download torrent</a>
                        </div>
                    }
                    <div className="vertical-padding-top"></div>
                </div>
            </div>
        </div>
    )
}

export default Page