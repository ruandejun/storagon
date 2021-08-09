function CreateEnum(filterList) {
    var enumDict = {};
    for (var i in filterList) {
        enumDict[filterList[i]] = i;
    }
    return enumDict;
}

export const FlagFilter = ['ok', 'warning', 'error', 'critical'];
export const Flag = CreateEnum(FlagFilter);
export const AccountTypeFilter = ['user', 'affiliate', 'reseller', 'affiliatePPD'];
export const AccountType = CreateEnum(AccountTypeFilter);
export const BalanceTypeFilter = ['credit', 'point', 'paypal', 'webmoney', 'ppd credit'];
export const BalanceType = CreateEnum(BalanceTypeFilter);
export const AccountStatusFilter = ['normal', 'emailNotActivated', 'banned', 'temporary'];
export const AccountStatus = CreateEnum(AccountStatusFilter);
export const ApplyTypeFilter = ['Become Affiliate', 'Withdraw Money', 'Switch mode to affiliate PPD', 'Switch mode to affiliate PPS'];
export const ApplyType = CreateEnum(ApplyTypeFilter);
export const ApplyStatusFilter = ['Processing', 'Accepted', 'Rejected'];
export const ApplyStatus = CreateEnum(ApplyStatusFilter);
export const FolderTypeFilter = ['normal', 'recycle'];
export const FolderType = CreateEnum(FolderTypeFilter);
export const ServerStatusFilter = ['normal', 'offline', 'downloadOnly'];
export const ServerStatus = CreateEnum(ServerStatusFilter);
export const TransactionTypeFilter = ['agency', 'referer', 'website', 'rebill'];
export const TransactionType = CreateEnum(TransactionTypeFilter);
export const SessionTypeFilter = ['upload', 'download', 'bill', 'delete', 'report', 'inbox', 'move'];
export const SessionType = CreateEnum(SessionTypeFilter);
export const SessionStatusFilter = ['waiting', 'working', 'completed', 'failed'];
export const SessionStatus = CreateEnum(SessionStatusFilter);
export const OrderNumberFilter = ['first', 'second', 'third', 'fourth'];
export const OrderNumber = CreateEnum(OrderNumberFilter);
export const DowloadTypeFilter = ['none', 'torrent', 'browser', 'direct'];
export const DownloadType = CreateEnum(DowloadTypeFilter);

export function convertFilesize(bytes) {
    var units = [
        'bytes',
        'KB',
        'MB',
        'GB',
        'TB',
        'PB'
    ];
    if (isNaN(parseFloat(bytes)) || !isFinite(bytes)) {
        return '?';
    }
    if (bytes === 0)
        return 'Unlimited';
    var unit = 0;
    while (bytes >= 1024) {
        bytes /= 1024;
        unit++;
    }
    return bytes.toFixed(2) + ' ' + units[unit];
}