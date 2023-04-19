# -*- coding: utf-8 -*-
from aop.api.base import BaseApi

class AlibabaCpsQueryTradeInfoSumParam(BaseApi):
    """查询订单的汇总信息

    References
    ----------
    https://open.1688.com/api/api.htm?ns=com.alibaba.p4p&n=alibaba.cps.queryTradeInfoSum&v=1&cat=union

    """

    def __init__(self, domain=None):
        BaseApi.__init__(self, domain)
        self.access_token = None
        self.mediaZoneId = None
        self.startDate = None
        self.endDate = None

    def get_api_uri(self):
        return '1/com.alibaba.p4p/alibaba.cps.queryTradeInfoSum'

    def get_required_params(self):
        return ['mediaZoneId', 'startDate', 'endDate']

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
