# Define all enum here.
from system_configure.enums import EnumBase


class Flag(EnumBase):
	ok = 0
	warning = 1
	error = 2
	critical = 3


class AccountType(EnumBase):
	user = 0
	affiliate = 1
	reseller = 2
	affiliatePPD = 3

class LogicStep(EnumBase):
	pending = 0
	approved = 1
	processing = 2
	completed = 3
	failed = 4
	checked = 5

class AccountStatus(EnumBase):
	normal = 0
	emailNotActivated = 1
	banned = 2
	temporary = 3


class FolderType(EnumBase):
	normal = 0
	recycle = 1


class ServerStatus(EnumBase):
	normal = 0
	offline = 1
	downloadOnly = 2


class BillStatus(EnumBase):
	ok = 0
	cancel = 1
	fraud = 2


class TransactionType(EnumBase):
	agency = 0
	referer = 1
	website = 2
	pay = 3
	transfer = 4
	ppd = 5
	rebill = 6
	refererPPD = 7


class TransactionStatus(EnumBase):
	auto = 0
	manual = 1
	revert = 2


class BalanceType(EnumBase):
	credit = 0
	point = 1
	paypal = 2
	webmoney = 3
	ppd = 4


class SessionType(EnumBase):
	upload = 0
	download = 1
	bill = 2
	delete = 3
	report = 4
	inbox = 5
	move = 6


class DownloadType(EnumBase):
	torrent = 1
	browser = 2
	direct = 3


class SessionStatus(EnumBase):
	waiting = 0
	working = 1
	completed = 2
	failed = 3


class FileMode(EnumBase):
	normal = 0
	premiumOnly = 1
	private = 2


class ApplyType(EnumBase):
	becomeAffiliate = 0
	payAffiliate = 1
	becomeAffiliatePPD = 2
	becomeAffiliatePPS = 3


class ApplyStatus(EnumBase):
	processing = 0
	accepted = 1
	rejected = 2


class InvokeType(EnumBase):
	download = 1