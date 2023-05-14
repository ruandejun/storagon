#!/usr/bin/python
# -*- coding: utf-8 -*-
#



from django.conf.urls import url
from .Commission_Api import *

urlpatterns = [
	url(r'^get_commission/', get_commission, name='get_commission'),
	url(r'^get_link_mobile/', get_link_mobile, name='get_link_mobile'),
	url(r'^get_link_pc/', get_link_pc, name='get_link_pc'),
	url(r'^get_list_taobao_order_commission/', get_list_taobao_order_commission, name='get_list_taobao_order_commission'),
	url(r'^get_list_1688_order_commission/', get_list_1688_order_commission, name='get_list_1688_order_commission'),
	url(r'^get_1688_commission_statistics/', get_1688_commission_statistics, name='get_1688_commission_statistics'),
	url(r'^get_taobao_commission_statistics/', get_taobao_commission_statistics, name='get_taobao_commission_statistics'),
	url(r'^get_all_commission/', get_all_commission, name='get_all_commission'),
	url(r'^get_commission_information/', get_commission_information, name='get_commission_information'),
	url(r'^get_item_selections/', get_item_selections, name='get_item_selections'),
	url(r'^get_item_quantity_sale/', get_item_quantity_sale, name='get_item_quantity_sale'),
	url(r'^get_item_flash_sale/', get_item_flash_sale, name='get_item_flash_sale'),
	url(r'^get_item_ifashions/', get_item_ifashions, name='get_item_ifashions'),
]