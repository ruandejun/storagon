# -*- coding: utf-8 -*-
from aop.api.base import BaseApi

class AlibabaCpsGetCpsRecommendOfferListParam(BaseApi):
    """获取个性化推荐的cps商品(含推广链接)

    References
    ----------
    https://open.1688.com/api/api.htm?ns=com.alibaba.p4p&n=alibaba.cps.getCpsRecommendOfferList&v=1&cat=union

    """

    def __init__(self, domain=None):
        BaseApi.__init__(self, domain)
        self.access_token = None
        self.loginId = None
        self.mediaId = None
        self.mediaZoneId = None
        self.ext = None
        self.pageNo = None
        self.pageSize = None

    def get_api_uri(self):
        return '1/com.alibaba.p4p/alibaba.cps.getCpsRecommendOfferList'

    def get_required_params(self):
        return ['loginId', 'mediaId', 'mediaZoneId', 'ext', 'pageNo', 'pageSize']

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
