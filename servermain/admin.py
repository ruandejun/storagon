from django.contrib import admin
from storagon.enum import *
# Register your models here.
from storagon.tool import *
from models import User, UserProfile, UserFile, Folder, RealFile, ServerFile, Bill, AccountBalance, TransactionLog, Banlist, PremiumKey, UserApply, WebsiteAgency
from mongo_models import UserStorage, ServerFileStorage, Session
from controllers import UserController, ServerFileController, SessionController, FileController, BalanceController



# Register your models here.
# admin.site.register(UserProfile)
# admin.site.register(UserFile)
# admin.site.register(Folder)
# admin.site.register(RealFile)
# admin.site.register(ServerFile)
# admin.site.register(Bill)
# admin.site.register(AccountBalance)
# admin.site.register(TransactionLog)
# admin.site.register(SystemConfig)
admin.site.register(Banlist)
# admin.site.register(PremiumKey)
admin.site.register(WebsiteAgency)

from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.admin import UserAdmin
admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
	# list view
	search_fields = ['username', 'email']
	list_display = ('__unicode__', 'email', 'date_joined', 'last_login', 'is_active', 'is_staff')
	list_filter = ('date_joined', 'last_login', 'is_active', 'is_staff')
	ordering = ('date_joined', 'last_login', 'username')

	actions = ['login_using_this_user']

	def login_using_this_user(self, request, queryset):
		user = queryset.first();
		user.backend = 'django.contrib.auth.backends.ModelBackend'
		login(request, user)
		return HttpResponseRedirect('/#/account');
		# self.message_user(request, u"%s has been logged in sucessfully" % (user.username))
	login_using_this_user.short_description = u"Login this user"


@admin.register(UserProfile)
class CustomUserProfileAdmin(admin.ModelAdmin):

	def storage_used(self, object):
		storage = getObjectOrNone(UserStorage, user_id=object.id)
		if storage:
			return storage.storage_used
		return None

	def file_count(self, object):
		storage = getObjectOrNone(UserStorage, user_id=object.id)
		if storage:
			return storage.file_count
		return None

	def folder_count(self, object):
		storage = getObjectOrNone(UserStorage, user_id=object.id)
		if storage:
			return storage.folder_count
		return None

	def upload_bandwidth(self, object):
		storage = getObjectOrNone(UserStorage, user_id=object.id)
		if storage:
			return storage.upload_bandwidth
		return None

	def download_bandwidth(self, object):
		storage = getObjectOrNone(UserStorage, user_id=object.id)
		if storage:
			return storage.download_bandwidth
		return None

	def signup_ip_country(self, object):
		if object.signup_ip:
			try:
				response = settings.geo_reader.country(object.signup_ip);
			except:
				return 'Unknown'
			# return response.country.name
			return response.country.iso_code
		else:
			return 'Unidentified'

	# list view
	search_fields = ['user__username', 'full_name']
	list_display = ('__unicode__', 'signup_ip_country', 'referer2', 'plan_expired', 'storage_used', 'upload_bandwidth', 'download_bandwidth', 'file_count', 'folder_count', 'referer')
	list_filter = ('plan_id', 'plan_expired', 'referer2', 'referer')
	actions = ['recalculate_storage']

	def recalculate_storage(self, request, queryset):
		count = 0
		for userProfile in queryset:
			userStorage = UserController.calculateUserStorage(userProfile.user.id)
			if userStorage:
				count += 1

		self.message_user(request, u"%s UserStorage are successfully calculated" % (count))
	recalculate_storage.short_description = u"Recalculate selected user storages"

###### File and Folder


@admin.register(UserFile)
class CustomUserFileAdmin(admin.ModelAdmin):
	# list view
	search_fields = ['id', 'user__username', 'file_name']
	list_display = ('__unicode__', 'created_date', 'modified_date', 'user', 'folder', 'download_tag')
	list_filter = ('created_date', 'modified_date')
	# form view
	readonly_fields = ('user',)
	raw_id_fields = ('realFile', 'folder')
	# extra
	list_select_related = ('realFile', 'folder')
	# actions
	actions = ['copy_file']

	def copy_file(self, request, queryset):
		user_id, copy_to_folder_id = getParamsOr400(request, ('user_id', int), ('copy_to_folder_id', 0))

		try:
			user = User.objects.get(id=user_id)
			if copy_to_folder_id>0: copyToFolder = Folder.objects.get(id=copy_to_folder_id)
			else: copyToFolder=None
		except User.DoesNotExist:
			self.message_user(request, u"User DoesNotExist", level=messages.ERROR)
			return
		except Folder.DoesNotExist:
			self.message_user(request, u"Folder DoesNotExist", level=messages.ERROR)
			return

		try:
			result = FileController.copyFile(queryset, user, copyToFolder);
		except Exception as e:
			self.message_user(request, u"Unable to copy, error=%s"%(e), level=messages.ERROR)
		else:
			self.message_user(request, u"%s UserFile are successfully copied to new user manualy: %s" % (result, user))
		return
	copy_file.short_description = u"Copy selected UserFile for second owner"


@admin.register(Folder)
class CustomFolderAdmin(admin.ModelAdmin):
	# list view
	search_fields = ['id', 'user__username', 'name']
	list_display = ('__unicode__', 'created_date', 'user', 'parent_folder')
	# list_filter = ('dt','platform','account_type','status')
	# form view
	# readonly_fields = ('user',)
	raw_id_fields = ('parent_folder',)
	# extra
	# list_select_related = ('realFile', 'folder')


from django.contrib import messages


@admin.register(RealFile)
class CustomRealFileAdmin(admin.ModelAdmin):

	def userfile_count(self, object):
		return object.userfile_set.count()

	# list view
	search_fields = ['id', 'file_location', 'file_hash', 'file_size']
	list_display = ('__unicode__', 'file_size', 'created_date', 'userfile_count')
	list_filter = ('created_date', 'serverFile') #
	actions = ['make_move_session', 'delete_useless'] #, 'change_server_file',
	# form view
	readonly_fields = ('serverFile',)

	# remember to remove change_server_file action, and make serverFile readonly field

	def make_move_session(self, request, queryset):
		serverFile_id = getParamsOr400(request, ('serverFile_id', int))

		try:
			serverFile = ServerFile.objects.get(id=serverFile_id)
		except ServerFile.DoesNotExist:
			self.message_user(request, u"ServerFile DoesNotExist", level=messages.ERROR)
			return

		result = SessionController.createMoveSession(request.user, serverFile, queryset)

		if isinstance(result, int):
			self.message_user(request, u"%s RealFile are successfully marked to move to new server: %s" % (result, serverFile))
		else:
			self.message_user(request, result, level=messages.WARNING)

	make_move_session.short_description = u"Move selected RealFile to new server"

	def change_server_file(self, request, queryset):
		serverFile_id = getParamsOr400(request, ('serverFile_id', int))

		try:
			serverFile = ServerFile.objects.get(id=serverFile_id)
		except ServerFile.DoesNotExist:
			self.message_user(request, u"ServerFile DoesNotExist", level=messages.ERROR)
			return

		result = queryset.update(serverFile_id=serverFile_id)

		self.message_user(request, u"%s RealFile are successfully change serverFile manualy: %s" % (result, serverFile))

	def delete_useless(self, request, queryset):
		result=0;
		for realfile in queryset:
			if realfile.userfile_set.count()==0:
				realfile.delete();
				result+=1;

		self.message_user(request, u"%s RealFile are successfully deleted due to no userfile" % (result));

	delete_useless.short_description = u"Delete selected RealFile that have no userfile"


# Transaction


@admin.register(Bill)
class CustomBillAdmin(admin.ModelAdmin):

	def billSession_id(self, object):
		billSession = getObjectOrNone(Session, sid=object.id, type=SessionType.bill, status=SessionStatus.completed)
		if billSession:
			return billSession.id;
		else:
			return None;

	def money_gain(self, object):
		return object.money_charged - sum([trans.amount for trans in object.transactionlog_set.all()])

	# list view
	search_fields = ['user__username', 'detail']
	list_display = ('__unicode__','bill_status', 'money_charged', 'money_gain', 'user', 'plan_id', 'paygate_id','created_date', 'billSession_id', 'premiumkey')
	list_filter = ('plan_id', 'paygate_id','bill_status', 'money_charged', 'created_date')
	actions = ['mark_bill_as_fraud']
	# form view
	# readonly_fields = ('user',)

	def mark_bill_as_fraud(self, request, queryset):
		bill_count = 0
		transaction_count = 0;
		for bill in queryset:
			result= BalanceController.revertTransaction(bill.transactionlog_set.all(),detail='fraud')
			if result>0:
				bill_count += 1;
				transaction_count += result;
				bill.bill_status = BillStatus.fraud;
				bill.save();

		self.message_user(request, u"%s bill have been marked as fraud and %s transaction has been reverted successfuly" % (bill_count,transaction_count))
	mark_bill_as_fraud.short_description = u"Mark bill as fraud and revert all related transaction"

@admin.register(AccountBalance)
class CustomAccountBalanceAdmin(admin.ModelAdmin):
	# list view
	search_fields = ['user__username','account_id']
	list_display = ('__unicode__', 'amount','account_id')
	list_filter = ('balance_type',)
	# form view
	readonly_fields = ('user','amount')



@admin.register(PremiumKey)
class CustomPremiumKeyAdmin(admin.ModelAdmin):
	# list view
	search_fields = ['reseller__username', 'activated_user__username', 'code']
	list_display = ('__unicode__', 'plan_id', 'reseller', 'created_date', 'activated_date')
	list_filter = ('created_date', 'activated_date')
	# form view
	readonly_fields = ('activated_user', 'activated_date', 'bill')


@admin.register(TransactionLog)
class CustomTransactionLogAdmin(admin.ModelAdmin):

	def billSession_id(self, object):
		if object.invoice_bill is None: return None
		billSession = getObjectOrNone(Session, sid=object.invoice_bill.id, type=SessionType.bill, status=SessionStatus.completed)
		if billSession:
			return billSession.id;
		else:
			return None;

	# list view
	search_fields = ['balance__user__username']
	list_display = ('__unicode__', 'transaction_type', 'transaction_status', 'amount', 'created_date', 'balance', 'billSession_id', 'data')
	list_filter = ('transaction_type','transaction_status', 'amount', 'created_date')
	actions = ['initiate_manual_transaction']
	# form view
	# readonly_fields = ('invoice_bill','balance')

	def initiate_manual_transaction(self, request, queryset):
		count = 0
		for transactionLog in queryset:
			if transactionLog.transaction_status == TransactionStatus.manual and transactionLog.balance is not None and transactionLog.amount != 0:
				if BalanceController.chargeBalance(transactionLog.balance.id, transactionLog.amount):
					transactionLog.transaction_status = TransactionStatus.auto;
					transactionLog.save();
					count += 1

		self.message_user(request, u"%s transaction have been successfully initiated" % (count))
	initiate_manual_transaction.short_description = u"Initiate manual transaction"


@admin.register(ServerFile)
class CustomServerFileAdmin(admin.ModelAdmin):

	def storage_used(self, object):
		storage = getObjectOrNone(ServerFileStorage, serverFile_id=object.id)
		if storage:
			return storage.storage_used
		return None

	def file_count(self, object):
		storage = getObjectOrNone(ServerFileStorage, serverFile_id=object.id)
		if storage:
			return storage.file_count
		return None

	def download_bandwidth(self, object):
		storage = getObjectOrNone(ServerFileStorage, serverFile_id=object.id)
		if storage:
			return storage.download_bandwidth
		return None

	def upload_bandwidth(self, object):
		storage = getObjectOrNone(ServerFileStorage, serverFile_id=object.id)
		if storage:
			return storage.upload_bandwidth
		return None

	# list view
	search_fields = ['name', 'ip_address']
	list_display = ('__unicode__', 'storage_used', 'total_storage', 'server_status', 'file_count', 'download_bandwidth', 'upload_bandwidth')
	list_filter = ('server_status',)
	actions = ['recalculate_storage']

	def recalculate_storage(self, request, queryset):
		count = 0
		for serverFile in queryset:
			serverStorage = ServerFileController.calculateServerFileStorage(serverFile.id)
			if serverStorage:
				count += 1

		self.message_user(request, u"%s ServerStorage are successfully calculated" % (count))
	recalculate_storage.short_description = u"Recalculate selected server storages"


@admin.register(UserApply)
class CustomUserApplyAdmin(admin.ModelAdmin):
	# list view
	search_fields = ['user__username', 'website_address']
	list_display = ('__unicode__', 'created_date', 'apply_status', 'data')
	list_filter = ('apply_type', 'apply_status', 'created_date')
	actions = ['accept_application', 'reject_application']

	def accept_application(self, request, queryset):
		for userApply in queryset:
			userApply.apply_status = ApplyStatus.accepted
			userApply.save();
	accept_application.short_description = u"Accept selected applications"

	def reject_application(self, request, queryset):
		for userApply in queryset:
			userApply.apply_status = ApplyStatus.rejected
			userApply.save();
	reject_application.short_description = u"Reject selected applications"