//User_ClientAPI
var StorageFileKeyPrefix = 'fileKey_';
//var HEADER_TOKEN='SIGNATURE_AUTHORIZATION';
var HEADER_TOKEN = 'Signature-Authorization';
//var serverURL = 'http://test.storagon.com:64000';
var serverURL = '';

/* Custom filter */
function filesize(bytes) {
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
  return bytes.toFixed(2) + ' ' + units[ unit ];
}

function duration(seconds) {
  var units = ['s', 'h', 'd', 'w', 'mo', 'y'];
  if (isNaN(parseFloat(seconds)) || !isFinite(seconds)) {
    return '?';
  }
  var unit = 0;
  if (seconds >= 3600) {
    seconds /= 3600;
    unit += 1;
  }
  //day
  if (seconds >= 24) {
    seconds /= 24;
    unit += 1;
  }
  //weeks
  if (seconds >= 7) {
    seconds /= 7;
    unit += 1;
  }
  //months
  if (seconds >= 4) {
    seconds /= 4;
    unit += 1;
  }
  //years
  if (seconds >= 12) {
    seconds /= 12;
    unit += 1;
  }
  return units[unit];
}

function currency(input, symbol, place) {
  if (isNaN(input)) {
    return input;
  } else {
    // Check if optional parameters are passed, if not, use the defaults
    var symbol = symbol || '$';
    var place = place === undefined ? true : place;

    // Perform the operation to set the symbol in the right location
    if (place === true) {
      return symbol + input.toFixed(2);
    } else {
      return input.toFixed(2) + symbol;
    }
  }
}

function CreateEnum(filterList) {
  var enumDict = {};
  for (var i in filterList) {
    enumDict[filterList[i]] = i;
  }
  return enumDict;
}

function add_auth_ajax(req) {
  var md5 = CryptoJS.algo.MD5.create();
  md5.update(SRK);
  if (req.type === 'GET') {
    if (req.url.indexOf('?') < 0)
      req.url += '?';
    else
      req.url += '&';
    req.url += 'rd' + Math.random().toString().substring(2) + '=';
    md5.update(req.url);
  }
  if (req.type === 'POST') {
    if (typeof (req.data) === "string")
      md5.update(req.data);
    else
      md5.update(jQuery.param(req.data));
  }

  if (!req.headers)
    req.headers = {};
  req.headers[HEADER_TOKEN] = md5.finalize().toString(CryptoJS.enc.Hex);
  return req;
}


var FlagFilter = ['ok', 'warning', 'error', 'critical'];
var Flag = CreateEnum(FlagFilter);
var AccountTypeFilter = ['user', 'affiliate', 'reseller', 'affiliatePPD'];
var AccountType = CreateEnum(AccountTypeFilter);
var BalanceTypeFilter = ['credit', 'point', 'paypal', 'webmoney', 'ppd credit'];
var BalanceType = CreateEnum(BalanceTypeFilter);
var AccountStatusFilter = ['normal', 'emailNotActivated', 'banned', 'temporary'];
var AccountStatus = CreateEnum(AccountStatusFilter);
var ApplyTypeFilter = ['Become Affiliate', 'Withdraw Money', 'Switch mode to affiliate PPD', 'Switch mode to affiliate PPS'];
var ApplyType = CreateEnum(ApplyTypeFilter);
var ApplyStatusFilter = ['Processing', 'Accepted', 'Rejected'];
var ApplyStatus = CreateEnum(ApplyStatusFilter);
var FolderTypeFilter = ['normal', 'recycle'];
var FolderType = CreateEnum(FolderTypeFilter);
var ServerStatusFilter = ['normal', 'offline', 'downloadOnly'];
var ServerStatus = CreateEnum(ServerStatusFilter);
var TransactionTypeFilter = ['agency', 'referer', 'website', 'rebill'];
var TransactionType = CreateEnum(TransactionTypeFilter);
var SessionTypeFilter = ['upload', 'download', 'bill', 'delete', 'report', 'inbox', 'move'];
var SessionType = CreateEnum(SessionTypeFilter);
var SessionStatusFilter = ['waiting', 'working', 'completed', 'failed'];
var SessionStatus = CreateEnum(SessionStatusFilter);
var OrderNumberFilter = ['first', 'second', 'third', 'fourth'];
var OrderNumber = CreateEnum(OrderNumberFilter);

function login(username, password, callback, errorCallback) {
  var req = {
    type: "POST",
    url: serverURL + '/clapi/user/login/',
    data: {
      'username': username,
      'password': password
    },
    success: function (data) {
      callback(data);
    },
    error: function (jqXHR, textStatus, errorThrown) {
      errorCallback();
    }
  };

  $.ajax(add_auth_ajax(req));
}

function logout(callback) {
  var client = $.ajax(add_auth_ajax({
    type: "POST",
    url: serverURL + '/clapi/user/logout/',
    data: {
    },
    success: function (data) {
      callback(data);
    }
  }));
}

function getUserInfo(callback) {
  $.getJSON(serverURL + "/clapi/user/getUserInfo/", function (data) {
    var profiles = jQuery.parseJSON(data.profiles);
    data['profile'] = profiles[0];
    callback(data);
  });
}
;

function getUserBalance(callback) {
  $.ajax(add_auth_ajax({
    type: "GET",
    url: serverURL + "/clapi/user/getUserBalance/",
    dataType: "json",
    success: function (json) {
      callback(json);
    }
  }));
}
;

function signup(username, password, email, captcha, callback, errorCallback) {
  var client = $.ajax(add_auth_ajax({
    type: "POST",
    url: serverURL + '/clapi/user/signup/',
    data: {
      'username': username,
      'password': password,
      'email': email,
      'g-recaptcha-response': captcha
    },
    success: function (data) {
      callback(data);
    },
    error: function (jqXHR, textStatus, errorThrown) {
      errorCallback();
    }
  }));
}
;

function createTemporaryUser(password, eumk, callback, errorCallback) {
  var client = $.ajax(add_auth_ajax({
    type: "POST",
    url: '/clapi/user/createTemporaryUser/',
    data: {
      'password': password,
      'eumk': eumk
    },
    success: function (data) {
      callback(JSON.parse(data));
    },
    error: function (jqXHR, textStatus, errorThrown) {
      errorCallback();
    }
  }));
}
;

function signupTemporaryUserAccount(username, password, new_username, email, callback, errorCallback) {
  var client = $.ajax(add_auth_ajax({
    type: "POST",
    url: '/clapi/user/signupTemporaryUserAccount/',
    data: {
      'username': username,
      'password': password,
      'new_username': new_username,
      'email': email
    },
    success: function (data) {
      callback(data);
    },
    error: function (jqXHR, textStatus, errorThrown) {
      errorCallback();
    }
  }));
}
;

//end of User_ClientAPI

function reverse(s) {
  return s.split("").reverse().join("");
}

//Session_ClientAPI
function createUploadSession(file_hash, file_size, file_name, folder_id, erfk, callback, errorCallback) {
  if (folder_id === "")
    folder_id = 0;
  var client = $.ajax(add_auth_ajax({
    url: serverURL + '/clapi/session/createUploadSession/',
    type: "POST",
    data: {
      'file_hash': file_hash,
      'file_size': file_size,
      'file_name': file_name,
      'folder_id': folder_id,
      'erfk': ''//reverse(Base64.encode(erfk)) //remember to change this to send reverse base64 to server
    },
    success: function (data, textStatus, jqXHR) {
      callback(JSON.parse(data));
    },
    error: function (jqXHR, textStatus, errorThrown) {
      if (errorCallback)
        errorCallback(jqXHR);
      else
        alert('error ' + jqXHR.status + ': ' + errorThrown);
    }
  }));
}


function createDownloadSession(POST, callback, errorCallback) {
  var client = $.ajax(add_auth_ajax({
    url: serverURL + '/clapi/session/createDownloadSession/',
    type: "POST",
    data: {
      'userFile_id': POST.file_id,
      'download_type': POST.download_type
    },
    success: function (data, textStatus, jqXHR) {
      callback(JSON.parse(data));
    },
    error: function (jqXHR, textStatus, errorThrown) {
      if (errorCallback) {
        errorCallback(jqXHR, textStatus, errorThrown);
      }
      else {
        alert('error ' + jqXHR.status + ': ' + errorThrown);
      }
    }
  }));
}
;

function createReport(text, file_id, user_id, detail, callback, errorCallback) {
  var client = $.ajax(add_auth_ajax({
    url: serverURL + '/clapi/session/createReport/',
    type: "POST",
    data: {
      'text': text,
      'fid': file_id,
      'sid': user_id,
      'detail': detail
    },
    success: function (data, textStatus, jqXHR) {
      callback(JSON.parse(data));
    },
    error: function (jqXHR, textStatus, errorThrown) {
      if (errorCallback)
        errorCallback();
      else
        alert('error ' + jqXHR.status + ': ' + errorThrown);
    }
  }));
}
;

//end of Session_ClientAPI

//encryption

var Base64 = {_keyStr: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=", encode: function (e) {
    var t = "";
    var n, r, i, s, o, u, a;
    var f = 0;
    e = Base64._utf8_encode(e);
    while (f < e.length) {
      n = e.charCodeAt(f++);
      r = e.charCodeAt(f++);
      i = e.charCodeAt(f++);
      s = n >> 2;
      o = (n & 3) << 4 | r >> 4;
      u = (r & 15) << 2 | i >> 6;
      a = i & 63;
      if (isNaN(r)) {
        u = a = 64;
      } else if (isNaN(i)) {
        a = 64;
      }
      t = t + this._keyStr.charAt(s) + this._keyStr.charAt(o) + this._keyStr.charAt(u) + this._keyStr.charAt(a);
    }
    return t;
  }, decode: function (e) {
    var t = "";
    var n, r, i;
    var s, o, u, a;
    var f = 0;
    e = e.replace(/[^A-Za-z0-9\+\/\=]/g, "");
    while (f < e.length) {
      s = this._keyStr.indexOf(e.charAt(f++));
      o = this._keyStr.indexOf(e.charAt(f++));
      u = this._keyStr.indexOf(e.charAt(f++));
      a = this._keyStr.indexOf(e.charAt(f++));
      n = s << 2 | o >> 4;
      r = (o & 15) << 4 | u >> 2;
      i = (u & 3) << 6 | a;
      t = t + String.fromCharCode(n);
      if (u !== 64) {
        t = t + String.fromCharCode(r);
      }
      if (a !== 64) {
        t = t + String.fromCharCode(i);
      }
    }
    t = Base64._utf8_decode(t);
    return t;
  }, _utf8_encode: function (e) {
    e = e.replace(/\r\n/g, "\n");
    var t = "";
    for (var n = 0; n < e.length; n++) {
      var r = e.charCodeAt(n);
      if (r < 128) {
        t += String.fromCharCode(r);
      } else if (r > 127 && r < 2048) {
        t += String.fromCharCode(r >> 6 | 192);
        t += String.fromCharCode(r & 63 | 128);
      } else {
        t += String.fromCharCode(r >> 12 | 224);
        t += String.fromCharCode(r >> 6 & 63 | 128);
        t += String.fromCharCode(r & 63 | 128);
      }
    }
    return t;
  }, _utf8_decode: function (e) {
    var t = "";
    var n = 0;
    var r = c1 = c2 = 0;
    while (n < e.length) {
      r = e.charCodeAt(n);
      if (r < 128) {
        t += String.fromCharCode(r);
        n++;
      } else if (r > 191 && r < 224) {
        c2 = e.charCodeAt(n + 1);
        t += String.fromCharCode((r & 31) << 6 | c2 & 63);
        n += 2;
      } else {
        c2 = e.charCodeAt(n + 1);
        c3 = e.charCodeAt(n + 2);
        t += String.fromCharCode((r & 15) << 12 | (c2 & 63) << 6 | c3 & 63);
        n += 3;
      }
    }
    return t;
  }
};

function hex2a(hexx) {
  var hex = hexx.toString();//force conversion
  var str = '';
  for (var i = 0; i < hex.length; i += 2)
    str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
  return str;
}
function a2hex(str) {
  var arr = [];
  for (var i = 0, l = str.length; i < l; i++) {
    var hex = Number(str.charCodeAt(i)).toString(16);
    arr.push(hex);
  }
  return arr.join('');
}

function generateEncryptionKey() {//32 byte hex <=> 32*4= 128bit key
  var genkey = "";
  var hex = "0123456789abcdef";

  for (i = 0; i < 32; i++) {
    genkey += hex.charAt(Math.floor(Math.random() * 16));
    //Initially this was charAt(chance.integer({min: 0, max: 15}));
  }
  return genkey;
}

//resumable

function applyResumableToInput(file, progress_id, upspeed_id, folder_id, randomID, callback, errorCallback) {
  var r = new Resumable({
        target: '/sf/upload/34124124124/',
        chunkSize: 1 * 1024 * 1024,
        simultaneousUploads: 1,
        maxFiles: 1
                //query:{upload_token:'my_token'}
  });
  // Resumable.js isn't supported, fall back on a different method
  if (!r.support)
        location.href = '/some-old-crappy-uploader';

  //r.assignBrowse(document.getElementById(inputID));
  //$('input#' + inputID).trigger('click');
  r.on('fileAdded', function (file) {
    //console.log("Chunk size = " + r.opts.chunkSize);
    var reader = new FileReader();
    var md5 = CryptoJS.algo.MD5.create();
    var counter = 0;
    var uploadProgressPanel = $('#upload-progress tbody');
    reader.onload = function (event) {
      md5.update(CryptoJS.lib.WordArray.create(event.target.result));//hash raw data
      md5.update(file.size.toString());//hash + file_size as string
      var file_hash = md5.finalize().toString(CryptoJS.enc.Hex);
      //console.log("file_hash=" + file_hash);

      //set chunk_size to 10mb for file over 50mb

      r.duplicated = false;

      createUploadSession(file_hash, file.size, file.fileName, folder_id, '', function (data) {
        //sucess callback
        //console.log(data);
        r.opts.target = data.upload_link;
        r.duplicated = data.duplicated;
        r.uniqueIdentifier = data.session_id;

        //set ready
        uploadProgressPanel.append(
            '<tr id=\'' + randomID + '\' class=\'initialize\'>' +
                '<td>' + file.fileName + '</td>' +
                '<td>' + filesize(file.size) + '</td>' +
                '<td class="progress">' +
                    '<div class="progress-bar progress-bar-success" ' +
                        'role="progressbar" aria-valuenow="0 aria-valuemin="0" ' +
                        'aria-valuemax="100" style="width: 0%" id="' + progress_id + '">' +
                        '<span class="sr-only">0% Complete (success)></span>' +
                    '</div>' +
                '</td>' +
                '<td id=\'' + upspeed_id + '\'></td>' +
                '<td>' +
                    '<a href=\'javascript:void(0)\' class=\'stop-progress\'>' +
                        '<span class=\'glyphicon glyphicon-pause\'></i></span>' + '</a>' +
                    '<a href=\'javascript:void(0)\' class=\'resume-progress\'>' +
                        '<span class=\'glyphicon glyphicon-play\'></i></span>' +'</a>' +
                    '<a href=\'javascript:void(0)\' class=\'remove-progress text-danger\'>' +
                        '<span class=\'glyphicon glyphicon-remove\'></i></span>' + '</a>' +
                '</td>' +
            '</tr>');
        r.readyToUpload = true;

        if (!$("#panel").hasClass("active")) { // show upload panel
            $('#show-hide-panel').trigger("click");
        }
        r.upload();
        r.startDate = new Date();
        r.lastDate = new Date();
        r.lastProgress = 0.0;
        $('tbody tr#' + randomID).removeClass('initialize');
      },
              function (xhr) {
                //error callback
                  var response_text  = JSON.parse(xhr.responseText);
                  alert(response_text.error);
              });
    };

    reader.readAsArrayBuffer(new Blob([file.file.slice(0, 1024 * 1024), file.file.slice(-1024 * 1024)]));//read first one megabyte + last one megabyte

    r.opts.target = '/sf/upload/123123/';

    if (file.size > 50 * 1024 * 1024) { //if file_size > 50Mb change chunk_size to 10Mb
      r.opts.chunkSize = 10 * 1024 * 1024;
      //if file_size > 500Mb change chunk_size to 20Mb
      //if (file.size > 500 * 1024 * 1024) r.opts.chunkSize = 20 * 1024 * 1024;


      r.opts.forceChunkSize = true;
      console.log("Set chunk size to 10MB = " + r.getOpt('chunkSize'));
      file.bootstrap();
    }

    //$('#' + inputID).val(file.fileName);
  });

  r.on('fileSuccess', function (file, message) {
    callback(progress_id);
    delete resumableObjList[randomID];
    r = null;
  });

  r.on('fileError', function (file, message) {
    errorResponse = JSON.parse(message);
    if (errorResponse.error == "chunk is invalid") {
      //$('#' + upspeed_id).html("Request hanging, retry after 3s.");
      file.abort();
      setTimeout(function () {
        file.retry();
      }, 5000);
    } else {
      $('#' + upspeed_id).html("Upload failed due to " + message);
      errorCallback(file.fileName, message);
    }

  });

  r.on('cancel', function () {
    delete resumableObjList[randomID];
    r = null;
  });

  var progress = 0;
  r.on('progress', function (file, message) {
    if (r.progress() < progress)
      return;
    progress = r.progress();
    //$('#' + progress_id).animate({width: (progress * 100) + "%"}, 100);
    $('#' + progress_id).css("width", (progress * 100) + "%");
    var curDate = new Date();
    var curDuration = curDate - r.lastDate;
    var incProgress = progress - r.lastProgress;
    //update ui
    var fileSize = r.getSize();
    var curSpeed = (fileSize * incProgress) / curDuration;
    var avgSpeed = (fileSize * progress) / (curDate - r.startDate);

    if (curSpeed > 0 && curDuration > 1000) {
      //change last progress
      r.lastDate = curDate;
      r.lastProgress = progress;
    }

    var correctSpeed = avgSpeed;
    if (curSpeed < avgSpeed * 1.2 && curSpeed > avgSpeed * 0.3)
      correctSpeed = curSpeed;
    if (curSpeed >= 0 && curSpeed <= avgSpeed * 0.3)
      correctSpeed = (avgSpeed + curSpeed) / 2;

    $('#' + upspeed_id).html(correctSpeed.toFixed(2) + " KB/s (" + (progress * 100).toFixed(1) + "%)");
  });

  r.appendFilesFromFileList([file]);

  return r;
}

//File_ClientAPI

function moveFile(file_id_list, folder_id, callback, errorCallback) {
  var postString = 'folder_id=' + folder_id;

  for (var i in file_id_list) {
    postString += '&file_id=' + file_id_list[i];
  }

  var client = $.ajax(add_auth_ajax({
    url: '/clapi/file/moveFile/',
    type: "POST",
    data: postString,
    success: function (data, textStatus, jqXHR) {
      callback();
    },
    error: function (jqXHR, textStatus, errorThrown) {
      if (errorCallback)
        errorCallback();
      else
        alert('error ' + jqXHR.status + ': ' + errorThrown);
    }
  }));
}
;

function deleteFile(file_id_list, callback, errorCallback) {
  var postString = '';
  for (var i in file_id_list) {
    postString += '&file_id=' + file_id_list[i];
  }
  postString = postString.substring(1);

  var client = $.ajax(add_auth_ajax({
    url: '/clapi/file/deleteFile/',
    type: "POST",
    data: postString,
    success: function (data, textStatus, jqXHR) {
      callback();
    },
    error: function (jqXHR, textStatus, errorThrown) {
      if (errorCallback)
        errorCallback();
      else
        alert('error ' + jqXHR.status + ': ' + errorThrown);
    }
  }));
}
;

function newFolder(folder_name, folder_id, callback, errorCallback) {
  var client = $.ajax(add_auth_ajax({
    url: '/clapi/file/newFolder/',
    type: "POST",
    data: {
      'folder_name': folder_name,
      'folder_id': folder_id
    },
    success: function (data, textStatus, jqXHR) {
      callback();
    },
    error: function (jqXHR, textStatus, errorThrown) {
      if (errorCallback)
        errorCallback();
      else
        alert('error ' + jqXHR.status + ': ' + errorThrown);
    }
  }));
}
;

function moveFolder(folder_id_list, to_folder_id, callback, errorCallback) {
  var postString = 'to_folder_id=' + to_folder_id;

  for (var i in folder_id_list) {
    postString += '&folder_id=' + folder_id_list[i];
  }

  var client = $.ajax(add_auth_ajax({
    url: '/clapi/file/moveFolder/',
    type: "POST",
    data: postString,
    success: function (data, textStatus, jqXHR) {
      callback();
    },
    error: function (jqXHR, textStatus, errorThrown) {
      if (errorCallback)
        errorCallback();
      else
        alert('error ' + jqXHR.status + ': ' + errorThrown);
    }
  }));
}
;


function deleteFolder(folder_id_list, callback, errorCallback) {
  var postString = '';
  for (var i in folder_id_list) {
    postString += '&folder_id=' + folder_id_list[i];
  }
  postString = postString.substring(1);

  var client = $.ajax(add_auth_ajax({
    url: '/clapi/file/deleteFolder/',
    type: "POST",
    data: postString,
    success: function (data, textStatus, jqXHR) {
      callback();
    },
    error: function (jqXHR, textStatus, errorThrown) {
      if (errorCallback)
        errorCallback();
      else
        alert('error ' + jqXHR.status + ': ' + errorThrown);
    }
  }));
}
;

function listFileAndFolder(folder_id, offset, limit, callback) {
  if(parseInt(limit) !== 0){
    var url = serverURL + "/clapi/file/listFileAndFolder/?folder_id=" + folder_id + "&file_offset=" + offset + "&file_limit=" + limit;
  }
  else{
    var url = serverURL + "/clapi/file/listFileAndFolder/?folder_id=" + folder_id;
  }
  
  $.ajax(add_auth_ajax({
    type: "GET",
    url: url,
    dataType: "json",
    success: function (json) {
      json['fileList'] = jQuery.parseJSON(json.fileList);
      json['folderList'] = jQuery.parseJSON(json.folderList);
      callback(json);
    }
  }));
}
;

function editFolder(folder_id, name, callback, errorCallback) {
  var client = $.ajax(add_auth_ajax({
    url: '/clapi/file/editFolder/',
    type: "POST",
    data: {
      'name': name,
      'folder_id': folder_id
    },
    success: function (data, textStatus, jqXHR) {
      callback();
    },
    error: function (jqXHR, textStatus, errorThrown) {
      if (errorCallback)
        errorCallback();
      else
        alert('error ' + jqXHR.status + ': ' + textStatus);
    }
  }));
}
;

function editFile(file_id, file_name, callback, errorCallback) {
  var client = $.ajax(add_auth_ajax({
    url: '/clapi/file/editFile/',
    type: "POST",
    data: {
      'file_name': file_name,
      'file_id': file_id
    },
    success: function (data, textStatus, jqXHR) {
      callback();
    },
    error: function (jqXHR, textStatus, errorThrown) {
      if (errorCallback)
        errorCallback();
      else
        alert('error ' + jqXHR.status + ': ' + errorThrown);
    }
  }));
}
;

function getLink(file_id_list, callback) {
                        console.log("test download")
  var postString = '';
  for (var i in file_id_list) {
    postString += '&file_id=' + file_id_list[i];
  }

  $.ajax(add_auth_ajax({
    type: "GET",
    url: "/api/file/userfile/?get_download_link=y" + postString,
    dataType: "json",
    success: function (data) {
      callback(data);
    }
  }));
}
;

function getPlanAndPaygateInfo(callback, errorCallback) {
  $.ajax(add_auth_ajax({
    type: "GET",
    url: "/clapi/userstats/getPlanAndPaygateInfo/",
    dataType: "json",
    success: function (json) {
      callback(json);
    }
  }));
}
;

function buyPremiumDirectProcess(plan_id, paygate_id, card_number,
        card_name, card_expiry, card_cvc, first_name, last_name,
        email, phone_number, address, country, state, city, zipcode,
        callback, errorCallback) {
  $.ajax(add_auth_ajax({
    type: "POST",
    url: '/buypremium/' + plan_id + '/' + paygate_id + '/',
    dataType: "json",
    data: $.param({
      card_number: card_number,
      card_name: card_name,
      card_expiry: card_expiry,
      card_cvc: card_cvc,
      first_name: first_name,
      last_name: last_name,
      email: email,
      phone_number: phone_number,
      address: address,
      country: country,
      state: state,
      city: city,
      zipcode: zipcode
    }),
    success: function (json) {
      callback(json);
    },
    error: function (jqXHR) {
      if (errorCallback)
        errorCallback(jqXHR);
      else
        defaultErrorCallBack('buyPremiumDirectProcess', data, status);
    }
  }));
}
;

var SRK = '7yn^8pwp+yzd2l4ki6+v9kp(h)rzs$9gxu4ao^_p+9x_5+1*6o';
