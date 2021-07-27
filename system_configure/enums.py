#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  enums
#  
#
#  Created by TVA on 4/21/15.
#  Copyright (c) 2015 storagon. All rights reserved.
#


class EnumBase:

	@classmethod
	def ChoiceList(cls):
		if not hasattr(cls, '_ChoiceList()'):
			cls._ChoiceList = [(getattr(cls, att), att) for att in dir(cls) if att[0]!='_' and type(getattr(cls, att)) is int]
			cls._ChoiceList.sort()
		return cls._ChoiceList;

	@classmethod
	def AllLabelList(cls):
		return [label for value, label in cls.ChoiceList()];

	@classmethod
	def AllValueList(cls):
		return [value for value, label in cls.ChoiceList()];