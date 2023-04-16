# -*- coding: utf-8 -*-
from aop.api.base import BaseApi

class AlibabaCpsGenClickUrlParam(BaseApi):
    """批量生成联盟推广url点击信息

    References
    ----------
    https://open.1688.com/api/api.htm?ns=com.alibaba.p4p&n=alibaba.cps.genClickUrl&v=1&cat=union

    """

    def __init__(self, domain=None):
        BaseApi.__init__(self, domain)
        self.access_token = None
        self.type = None
        self.mediaId = None
        self.mediaZoneId = None
        self.objectValueList = None
        self.ext = None

    def get_api_uri(self):
        return '1/com.alibaba.p4p/alibaba.cps.genClickUrl'

    def get_required_params(self):
        return ['type', 'mediaId', 'mediaZoneId', 'objectValueList', 'ext']

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
