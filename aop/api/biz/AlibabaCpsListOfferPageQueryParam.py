# -*- coding: utf-8 -*-
from aop.api.base import BaseApi

class AlibabaCpsListOfferPageQueryParam(BaseApi):
    """获取联盟offer列表

    References
    ----------
    https://open.1688.com/api/api.htm?ns=com.alibaba.p4p&n=alibaba.cps.listOfferPageQuery&v=1&cat=union

    """

    def __init__(self, domain=None):
        BaseApi.__init__(self, domain)
        self.access_token = None
        self.categoryId = None
        self.feedInfo = None
        self.defineTags = None
        self.filterMinPrice = None
        self.filterMaxPrice = None
        self.filterQuantityBeginMin = None
        self.filterQuantityBeginMax = None
        self.filterSaleQuantityMin = None
        self.filterSaleQuantityMax = None
        self.filterRatioMin = None
        self.filterRatioMax = None
        self.sortField = None
        self.pageNo = None
        self.pageSize = None
        self.filterOldBuyerRatio = None

    def get_api_uri(self):
        return '1/com.alibaba.p4p/alibaba.cps.listOfferPageQuery'

    def get_required_params(self):
        return ['feedInfo', 'pageNo', 'pageSize']

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
