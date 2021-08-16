import { Token } from './token'
import CryptoJS from 'crypto-js'
// const apiUrl = window.location.origin + '/api'
const apiUrl = window.location.origin === 'http://localhost:3000' ? 'http://localhost:8000' : `${window.location.origin}/api`
const SRK = '7yn^8pwp+yzd2l4ki6+v9kp(h)rzs$9gxu4ao^_p+9x_5+1*6o'

const fetchApi = async (method, path, params = {}, token) => {
    var md5 = CryptoJS.algo.MD5.create()
    md5.update(SRK)

    let finalPath = path
    let options = {
        method: method.toUpperCase(),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Authorization': `Token ${token || Token.getToken()}`,
            'Access-Control-Allow-Origin': '*'
        },
        credentials: 'same-origin'
    }

    console.log({ params })
    const data = Object.entries(params).map((v) => {
        if (v[1] != null && Array.isArray(v[1])) {
            return `${v[0]}=${v[1].join('&' + v[0] + '=')}`
        } else if (v[1] != null) {
            if (typeof v[1] === 'string') {
                return `${v[0]}=${v[1].replaceAll("'", '%27')}`
            } else {
                return `${v[0]}=${v[1]}`
            }
        }
    }).join('&')

    if (method.toUpperCase() === 'GET') {
        if (data && data.length > 0) {
            finalPath += '?' + data
        }
        md5.update(apiUrl + `/${finalPath}`)
    } else {
        options['body'] = data

        md5.update(data)
    }

    const signalture = md5.finalize().toString(CryptoJS.enc.Hex)
    console.log({ signalture, options, url: apiUrl + `/${finalPath}` })

    options['headers']['Signature-Authorization'] = signalture

    return await fetch(apiUrl + `/${finalPath}`, options).then(res => {

        return res.json()
    }).then(response => {
        console.log({ response })
        // if(response && response.error){
        //     alert(response.error)
        // }
        return response
    }).catch(err => {
        console.log({ err })
        console.info("__err__", err)
    })
}

const fetchApiJson = async (method, path, params = {}, token) => {
    var md5 = CryptoJS.algo.MD5.create()
    md5.update(SRK)

    let finalPath = path
    let options = {
        method: method.toUpperCase(),
        headers: {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': `Token ${token || Token.getToken()}`,
            'Access-Control-Allow-Origin': '*'
        },
        credentials: 'same-origin'
    }

    console.log({ params })
    const data = Object.entries(params).map((v) => {
        if (v[1] != null && Array.isArray(v[1])) {
            return `${v[0]}=${v[1].join('&' + v[0] + '=')}`
        } else if (v[1] != null) {
            if (typeof v[1] === 'string') {
                return `${v[0]}=${v[1].replaceAll("'", '%27')}`
            } else {
                return `${v[0]}=${v[1]}`
            }
        }
    }).join('&')

    if (method.toUpperCase() === 'GET') {
        if (data && data.length > 0) {
            finalPath += '?' + data
        }
        md5.update(apiUrl + `/${finalPath}`)
    } else {
        options['body'] =  JSON.stringify(params)

        md5.update(JSON.stringify(params))
    }

    const signalture = md5.finalize().toString(CryptoJS.enc.Hex)
    console.log({ signalture, options, url: apiUrl + `/${finalPath}` })

    options['headers']['Signature-Authorization'] = signalture

    return await fetch(apiUrl + `/${finalPath}`, options).then(res => {

        return res.json()
    }).then(response => {
        console.log({ response })
        if(response && response.error){
            alert(response.error)
        }
        return response
    }).catch(err => {
        console.log({ err })
        console.info("__err__", err)
    })
}

const fetchGetApi = async (method, path, params = {}, token) => {
    let finalPath = path
    let options = {
        method: method.toUpperCase(),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${token || Token.getToken()}`,
            'Access-Control-Allow-Origin': '*'
        }
    }

    options['body'] = JSON.stringify(params)

    // console.log({url: apiUrl + `/${finalPath}`, options})

    return await fetch(apiUrl + `/${finalPath}`, options).then(res => {
        console.log({ res })
        if (res.ok) {
            return res.json()
        }
        return res.text()
    }).then(response => {
        console.log({ response })
        return response
    }).catch(err => {
        console.log({ err })
        console.info("__err__", err)
    })
}

const fetchApiSignUp = async (method, path, params = {}) => {
    let finalPath = path
    let options = {
        method: method.toUpperCase(),
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            /*'Authorization': `Token ${Token.getToken()}`*/
        }
    }

    if (method.toUpperCase() === 'GET') {
        finalPath += '?' + Object.entries(params).map((v) => {
            if (v[1] != null && Array.isArray(v[1])) {
                return `${v[0]}=${v[1].join('&' + v[0] + '=')}`
            } else if (v[1] != null) {
                if (typeof v[1] === 'string') {
                    return `${v[0]}=${v[1].replaceAll("'", '%27')}`
                } else {
                    return `${v[0]}=${v[1]}`
                }
            }
        }).join('&')
    } else {
        options['body'] = JSON.stringify(params)
    }

    console.log(apiUrl + `/${finalPath}`, options)

    return await fetch(apiUrl + `/${finalPath}`, options).then(res => {
        return res.json()
    }).then(response => {
        return response
    }).catch(err => {
        console.info("__err__", err)
    })
}


const fetchApiLogin = async (method, path, params = {}) => {
    var md5 = CryptoJS.algo.MD5.create()
    md5.update(SRK)


    let finalPath = path
    let options = {
        method: method.toUpperCase(),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Access-Control-Allow-Origin': '*'
        },
        credentials: 'same-origin'
    }

    const data = Object.entries(params).map((v) => {
        if (Array.isArray(v[1])) {
            return `${v[0]}=${v[1].join(',')}`
        } else {
            return `${v[0]}=${v[1]}`
        }
    }).join('&')

    if (method.toUpperCase() === 'GET') {
        if (data && data.length > 0) {
            finalPath += '?' + data
        }

        md5.update(apiUrl + `/${finalPath}`)
    } else {
        options['body'] = data

        md5.update(data)
    }

    const signalture = md5.finalize().toString(CryptoJS.enc.Hex)
    console.log({ signalture })

    options['headers']['Signature-Authorization'] = signalture

    return await fetch(apiUrl + `/${finalPath}`, options).then(res => {
        return res.json()
    }).then(response => {
        return response
    }).catch(err => {
        console.info("__err__", err)
    })
}

const setToken = (token) => {
    localStorage.setItem('dt_token', token)
}

const isLoggedIn = () => {
    return !!localStorage.getItem('dt_token')
}

export {
    fetchApi,
    fetchApiLogin,
    setToken,
    isLoggedIn,
    fetchApiSignUp,
    fetchGetApi,
    fetchApiJson
}