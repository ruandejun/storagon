import actions from './action'
import { TransactionTypeFilter } from 'actions/constants'

const initState = {
    storage: null,
    balance: null,
    plan: null,
    billing: [],
    exchange: null,
    inbox: [],
    reports: [],
    website: null,
    referer: null,
    agency: null,
    statistic: null,
    downloadSessions: null,
    premiumKeys: []
};

export default function appReducer(state = initState, action) {
    switch (action.type) {
        case actions.GET_STORAGE_SUCCESS:
            return { ...state, storage: action.data };
        case actions.GET_BALANCE_SUCCESS:
            return { ...state, balance: action.data };
        case actions.GET_PLAN_SUCCESS:
            return { ...state, plan: action.data };
        case actions.GET_BILLING_SUCCESS:
            return { ...state, billing: action.data };
        case actions.GET_EXCHANGE_SUCCESS:
            return { ...state, exchange: action.data };
        case actions.GET_INBOX_SUCCESS:
            return { ...state, inbox: action.data };
        case actions.GET_REPORT_SUCCESS:
            return { ...state, reports: action.data };
        case actions.GET_TRANSACTION_SUCCESS:
            return { ...state, [TransactionTypeFilter[action.transaction_type]]: action.data };
        case actions.GET_STATISTIC_SUCCESS:
            return { ...state, statistic: action.data };
        case actions.GET_DOWNLOAD_SESSION_SUCCESS:
            return { ...state, downloadSessions: action.data };
        case actions.GET_PREMIUM_SUCCESS:
            return { ...state, premiumKeys: action.data };
        default:
            return state
    }
}
