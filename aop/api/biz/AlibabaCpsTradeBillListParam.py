# -*- coding: utf-8 -*-
from aop.api.base import BaseApi

class AlibabaCpsTradeBillListParam(BaseApi):
    """联盟实时获取订单列表

    References
    ----------
    https://open.1688.com/api/api.htm?ns=com.alibaba.p4p&n=alibaba.cps.tradeBillList&v=1&cat=union

    """

    def __init__(self, domain=None):
        BaseApi.__init__(self, domain)
        self.access_token = None
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
        return '1/com.alibaba.p4p/alibaba.cps.tradeBillList'

    def get_required_params(self):
        return ['queryOrderType', 'queryTimeType', 'queryStartTime', 'queryEndTime', 'pageNo', 'pageSize']

    def get_multipart_params(self):
        return []

    def need_sign(self):
        return True

    def need_timestamp(self):
        return False

    def need_auth(self):
        return False

    def need_https(self):
        return False

    def is_inner_api(self):
        return False
