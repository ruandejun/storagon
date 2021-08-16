import { takeEvery, put, call, fork } from 'redux-saga/effects'
import actions from './action'
import { fetchApi, fetchApiLogin } from "actions/api"
import { SessionType, SessionStatus } from 'actions/constants'
import moment from 'moment'

export function* getPlan() {
    let response = yield call(fetchApi, 'get', 'clapi/userstats/getPlanAndPaygateInfo/')
    console.log({ plan: response })

    if (response) {
        yield put({
            type: actions.GET_PLAN_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.GET_PLAN_FAIL
        })
    }
}

export function* getStorage() {
    let response = yield call(fetchApi, 'get', 'clapi/userstats/getUserStorage/')
    console.log({ storage: response })

    if (response) {
        yield put({
            type: actions.GET_STORAGE_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.GET_STORAGE_FAIL
        })
    }
}


export function* getBalance() {
    let response = yield call(fetchApi, 'get', 'clapi/user/getUserBalance/')
    console.log({ balance: response })

    if (response) {
        yield put({
            type: actions.GET_BALANCE_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.GET_BALANCE_FAIL
        })
    }
}

export function* getBilling({ from_date, to_date }) {
    let response = yield call(fetchApi, 'get', 'clapi/userstats/listBill/', { from_date, to_date })
    console.log({ billing: response })

    if (response) {
        yield put({
            type: actions.GET_BILLING_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.GET_BILLING_FAIL
        })
    }
}

export function* getExchange() {
    let response = yield call(fetchApi, 'get', 'clapi/userstats/getExchangePointRateInfo/')
    console.log({ exchange: response })

    if (response) {
        yield put({
            type: actions.GET_EXCHANGE_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.GET_EXCHANGE_FAIL
        })
    }
}

export function* getInbox({ from_date }) {
    let response = yield call(fetchApi, 'get', 'api/mongo/session/', { type: SessionType.inbox, from_date })
    console.log({ inbox: response })

    if (response) {
        yield put({
            type: actions.GET_INBOX_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.GET_INBOX_FAIL
        })
    }
}

export function* getReport({ from_date }) {
    let response = yield call(fetchApi, 'get', 'api/mongo/session/', { type: SessionType.report, from_date })
    console.log({ report: response })

    if (response) {
        yield put({
            type: actions.GET_REPORT_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.GET_REPORT_FAIL
        })
    }
}

export function* getTransaction({ from_date, to_date, transaction_type }) {
    let response = yield call(fetchApi, 'get', 'clapi/userstats/listTransaction/', { from_date, to_date, transaction_type })
    console.log({ [transaction_type]: response })

    if (response) {
        yield put({
            type: actions.GET_TRANSACTION_SUCCESS,
            data: response,
            transaction_type
        })
    } else {
        yield put({
            type: actions.GET_TRANSACTION_FAIL
        })
    }
}


export function* getStatistic({ from_date, to_date }) {
    let response = yield call(fetchApi, 'get', 'api/statistics/aff/transactionStatistics/', { from_date, to_date })
    console.log({ statistic: response })

    if (response && from_date && to_date) {
        var transactionList = {}
        let toDate = moment(to_date)
        let fromDate = moment(from_date)

        while (!fromDate.isAfter(toDate)) {
            transactionList[fromDate.toISOString().slice(0, 10)] = {}
            transactionList[fromDate.toISOString().slice(0, 10)]['bill'] = [0, 0]
            transactionList[fromDate.toISOString().slice(0, 10)]['ppd'] = [0, 0]
            transactionList[fromDate.toISOString().slice(0, 10)]['rebill'] = [0, 0]
            transactionList[fromDate.toISOString().slice(0, 10)]['refererPPD'] = [0, 0]
            transactionList[fromDate.toISOString().slice(0, 10)]['website'] = [0, 0]
            transactionList[fromDate.toISOString().slice(0, 10)]['referer'] = [0, 0]
            transactionList[fromDate.toISOString().slice(0, 10)]['downloadRaw'] = [0, 0]
            transactionList[fromDate.toISOString().slice(0, 10)]['totalOverall'] = 0
            fromDate = fromDate.add(1, 'days')
        }

        transactionList['Total'] = { 'bill': [0, 0], 'ppd': [0, 0], 'rebill': [0, 0], 'refererPPD': [0, 0], 'website': [0, 0], 'referer': [0, 0], 'downloadRaw': [0, 0], 'totalOverall': 0 }

        for (var i in response) {
            for (var j in response[i]) {
                if (i === "downloadRaw") {
                    var date = response[i][j]['_id']['year'] + "-" + ("0" + response[i][j]['_id']['month']).slice(-2) + "-" + ("0" + response[i][j]['_id']['day']).slice(-2)
                }
                else {
                    var date = response[i][j][0];
                }
                if (transactionList.hasOwnProperty(date)) {
                    transactionList[date][i][0] = (Array.isArray(response[i][j]) && i !== "ppd") ? response[i][j][1] : response[i][j]['count']
                    transactionList[date][i][1] = (Array.isArray(response[i][j])) ? response[i][j][2] : transactionList[date][i][1]
                    transactionList['Total'][i][0] = (Array.isArray(response[i][j])) ? (transactionList['Total'][i][0] + response[i][j][1]) : (transactionList['Total'][i][0] + response[i][j]['count'])
                    transactionList['Total'][i][1] = (Array.isArray(response[i][j])) ? (transactionList['Total'][i][1] + response[i][j][2]) : transactionList['Total'][i][1]
                    if (i === "ppd" || i === "refererPPD") {
                        transactionList[date]['totalOverall'] = (Array.isArray(response[i][j])) ? (transactionList[date]['totalOverall'] + (Math.round((transactionList[date][i][1] / 100000) * 1000) / 1000)) : transactionList[date]['totalOverall']
                    }
                    else {
                        transactionList[date]['totalOverall'] = (Array.isArray(response[i][j])) ? (transactionList[date]['totalOverall'] + (Math.round((transactionList[date][i][1] / 100) * 1000) / 1000)) : transactionList[date]['totalOverall']
                    }
                }
            }
        }
        for (date in transactionList) {
            if (transactionList.hasOwnProperty(date)) {
                if (date != 'Total')
                    transactionList['Total']['totalOverall'] += transactionList[date]['totalOverall']
            }
        }

        yield put({
            type: actions.GET_STATISTIC_SUCCESS,
            data: transactionList
        })
    } else {
        yield put({
            type: actions.GET_STATISTIC_FAIL
        })
    }
}

export function* getDownloadSession({ from_date, to_date, page, page_size, oid }) {
    let response = yield call(fetchApi, 'get', 'api/mongo/session/', { type: SessionType.download, status: SessionStatus.completed, from_date, to_date, page, page_size, oid })
    console.log({ downloadSession: response })

    if (response) {
        yield put({
            type: actions.GET_DOWNLOAD_SESSION_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.GET_DOWNLOAD_SESSION_FAIL
        })
    }
}

export function* getPremiumKey({ offset, limit }) {
    let response = yield call(fetchApi, 'get', 'clapi/premium/getListPremiumKey/', { offset, limit })
    console.log({ premiumKey: response })

    if (response) {
        yield put({
            type: actions.GET_PREMIUM_SUCCESS,
            data: response
        })
    } else {
        yield put({
            type: actions.GET_PREMIUM_FAIL
        })
    }
}

export default function* rootSaga() {
    yield [
        yield takeEvery(actions.GET_PLAN, getPlan),
        yield takeEvery(actions.GET_STORAGE, getStorage),
        yield takeEvery(actions.GET_BALANCE, getBalance),
        yield takeEvery(actions.GET_BILLING, getBilling),
        yield takeEvery(actions.GET_EXCHANGE, getExchange),
        yield takeEvery(actions.GET_INBOX, getInbox),
        yield takeEvery(actions.GET_REPORT, getReport),
        yield takeEvery(actions.GET_TRANSACTION, getTransaction),
        yield takeEvery(actions.GET_STATISTIC, getStatistic),
        yield takeEvery(actions.GET_DOWNLOAD_SESSION, getDownloadSession),
        yield takeEvery(actions.GET_PREMIUM, getPremiumKey),
    ]
}

