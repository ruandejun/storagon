# -*- coding: utf-8 -*-
from aop.api.base import BaseApi

class AlibabaCpsQueryRealtimeVisitorParam(BaseApi):
    """查询实时uv，muv接口

    References
    ----------
    https://open.1688.com/api/api.htm?ns=com.alibaba.p4p&n=alibaba.cps.queryRealtimeVisitor&v=1&cat=aop.union

    """

    def __init__(self, domain=None):
        BaseApi.__init__(self, domain)
        self.access_token = None
        self.mediaZoneId = None
        self.bizDate = None

    def get_api_uri(self):
        return '1/com.alibaba.p4p/alibaba.cps.queryRealtimeVisitor'

    def get_required_params(self):
        return ['mediaZoneId', 'bizDate']

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
