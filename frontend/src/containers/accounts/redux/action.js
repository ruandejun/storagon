const actions = {
    GET_STORAGE: 'GET_STORAGE',
    GET_STORAGE_SUCCESS: 'GET_STORAGE_SUCCESS',
    GET_STORAGE_FAIL: 'GET_STORAGE_FAIL',
    GET_BALANCE: 'GET_BALANCE',
    GET_BALANCE_SUCCESS: 'GET_BALANCE_SUCCESS',
    GET_BALANCE_FAIL: 'GET_BALANCE_FAIL',
    GET_PLAN: 'GET_PLAN',
    GET_PLAN_SUCCESS: 'GET_PLAN_SUCCESS',
    GET_PLAN_FAIL: 'GET_PLAN_FAIL',
    GET_BILLING: 'GET_BILLING',
    GET_BILLING_SUCCESS: 'GET_BILLING_SUCCESS',
    GET_BILLING_FAIL: 'GET_BILLING_FAIL',
    GET_EXCHANGE: 'GET_EXCHANGE',
    GET_EXCHANGE_SUCCESS: 'GET_EXCHANGE_SUCCESS',
    GET_EXCHANGE_FAIL: 'GET_EXCHANGE_FAIL',
    GET_INBOX: 'GET_INBOX',
    GET_INBOX_SUCCESS: 'GET_INBOX_SUCCESS',
    GET_INBOX_FAIL: 'GET_INBOX_FAIL',
    GET_REPORT: 'GET_REPORT',
    GET_REPORT_SUCCESS: 'GET_REPORT_SUCCESS',
    GET_REPORT_FAIL: 'GET_REPORT_FAIL',
    GET_TRANSACTION: 'GET_TRANSACTION',
    GET_TRANSACTION_SUCCESS: 'GET_TRANSACTION_SUCCESS',
    GET_TRANSACTION_FAIL: 'GET_STATISTIC',
    GET_STATISTIC: 'GET_STATISTIC',
    GET_STATISTIC_SUCCESS: 'GET_STATISTIC_SUCCESS',
    GET_STATISTIC_FAIL: 'GET_STATISTIC_FAIL',
    GET_DOWNLOAD_SESSION: 'GET_DOWNLOAD_SESSION',
    GET_DOWNLOAD_SESSION_SUCCESS: 'GET_DOWNLOAD_SESSION_SUCCESS',
    GET_DOWNLOAD_SESSION_FAIL: 'GET_DOWNLOAD_SESSION_FAIL',
    GET_PREMIUM: 'GET_PREMIUM',
    GET_PREMIUM_SUCCESS: 'GET_PREMIUM_SUCCESS',
    GET_PREMIUM_FAIL: 'GET_PREMIUM_FAIL',
    INBOX_MESSAGE: 'INBOX_MESSAGE',
    INBOX_MESSAGE_SUCCESS: 'INBOX_MESSAGE_SUCCESS',
    INBOX_MESSAGE_FAIL: 'INBOX_MESSAGE_FAIL',
    inboMessage: (message, to_username) => {
      return {
        type: actions.INBOX_MESSAGE,
        message, to_username
      }
    },
    getPlan: () => {
      return {
        type: actions.GET_PLAN,
      }
    },
    getBalance: () => {
        return  {
          type: actions.GET_BALANCE,
        }
    },
    getStorage: () => {
      return {
        type: actions.GET_STORAGE
      }
    },
    getBilling: (from_date, to_date) => {
      return {
        type: actions.GET_BILLING,
        from_date, to_date
      }
    },
    getExchange: () => {
      return {
        type: actions.GET_EXCHANGE
      }
    },
    getInbox: (from_date) => {
      return {
        type: actions.GET_INBOX,
        from_date
      }
    },
    getReport: (from_date) => {
      return {
        type: actions.GET_REPORT,
        from_date
      }
    },
    getTransaction: (from_date, to_date, transaction_type) => {
      return {
        type: actions.GET_TRANSACTION,
        from_date, to_date, transaction_type
      }
    },
    getStatistic: (from_date, to_date) => {
      return {
        type: actions.GET_STATISTIC,
        from_date, to_date
      }
    },
    getDownloadSession: (from_date, to_date, page, page_size, oid) => {
      return {
        type: actions.GET_DOWNLOAD_SESSION,
        from_date, to_date, page, page_size, oid
      }
    },
    getPremiumKey: (offset, limit) => {
      return {
        type: actions.GET_PREMIUM,
        offset, limit
      }
    }
  };
  
  export default actions
  