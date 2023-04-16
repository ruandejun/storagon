# -*- coding: utf-8 -*-
from aop.api.base import BaseApi

class AlibabaCpsWebUnionTradeBillListParam(BaseApi):
    """该接口后期会下线，仅老网盟用户使用，新接入不能使用该接口

新接入请使用以下接口
联盟账单列表查询alibaba.cps.tradeBillList


    References
    ----------
    https://open.1688.com/api/api.htm?ns=com.alibaba.p4p&n=alibaba.cps.webUnionTradeBillList&v=1&cat=union

    """

    def __init__(self, domain=None):
        BaseApi.__init__(self, domain)
        self.access_token = None
        self.webUnionKey = None
        self.queryOrderType = None
        self.queryTimeType = None
        self.queryStartTime = None
        self.queryEndTime = None
        self.orderState = None
        self.settleState = None
        self.rightsState = None
        self.pageNo = None
        self.pageSize = None

    def get_api_uri(self):
        return '1/com.alibaba.p4p/alibaba.cps.webUnionTradeBillList'

    def get_required_params(self):
        return ['webUnionKey', 'queryOrderType', 'queryTimeType', 'queryStartTime', 'queryEndTime', 'orderState', 'settleState', 'rightsState', 'pageNo', 'pageSize']

    def get_multipart_params(self):
        return []

    def need_sign(self):
        return True

    def need_timestamp(self):
        return False

    def need_auth(self):
        return True

    def need_https(self):
        return False

    def is_inner_api(self):
        return False
