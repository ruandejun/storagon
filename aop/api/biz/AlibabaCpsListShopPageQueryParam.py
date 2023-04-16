# -*- coding: utf-8 -*-
from aop.api.base import BaseApi

class AlibabaCpsListShopPageQueryParam(BaseApi):
    """获取联盟商家列表

    References
    ----------
    https://open.1688.com/api/api.htm?ns=com.alibaba.p4p&n=alibaba.cps.listShopPageQuery&v=1&cat=union

    """

    def __init__(self, domain=None):
        BaseApi.__init__(self, domain)
        self.access_token = None
        self.sellerId = None
        self.companyName = None
        self.categoryId = None
        self.defineTags = None
        self.filterRatioMin = None
        self.filterRatioMax = None
        self.sortField = None
        self.pageNo = None
        self.pageSize = None

    def get_api_uri(self):
        return '1/com.alibaba.p4p/alibaba.cps.listShopPageQuery'

    def get_required_params(self):
        return ['sellerId', 'companyName', 'categoryId', 'defineTags', 'filterRatioMin', 'filterRatioMax', 'sortField', 'pageNo', 'pageSize']

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
