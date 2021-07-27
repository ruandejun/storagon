/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

function add_auth_ajax(req){
	var md5 = CryptoJS.algo.MD5.create();
	md5.update(SRK);
	if (req.type.match('GET|HEAD|DELETE|OPTIONS')){
		if (req.url.indexOf('?') < 0)
			req.url += '?';else
			req.url += '&';
		req.url += 'rd' + Math.random().toString().substring(2) + '=';
		md5.update(req.url);
	}else{
		if (typeof (req.data) === "string")
			md5.update(req.data);else
			md5.update(jQuery.param(req.data));
	}

	if (!req.headers)
		req.headers = {};
	req.headers[HEADER_TOKEN] = md5.finalize().toString(CryptoJS.enc.Hex);
	return req;
}

function setPremium(file_id_list, callback, errorCallback){
	var jsonSentData = [];
	for (var i in file_id_list){
		if ($("#gs_content_table tr td#" + file_id_list[i]).hasClass("premium")){
			jsonSentData.push({id:file_id_list[i], file_mode:0});
		}else{
			jsonSentData.push({id:file_id_list[i], file_mode:1});
		}
	}

	$.ajax(add_auth_ajax({
		url:'/api/file/userfile/', type:"PUT", data:JSON.stringify(jsonSentData), headers:{
			'Content-Type':'application/json; charset=UTF-8'
		}, dataType:"json", success:function(data, textStatus, jqXHR){
			callback(data, textStatus, jqXHR);
		}, error:function(jqXHR, textStatus, errorThrown){
			if (errorCallback) errorCallback(jqXHR, textStatus, errorThrown);else alert('error ' + jqXHR.status + ': ' + errorThrown);
		}
	}));
};

function getFileByName(name, callback, errorCallback){
	$.ajax(add_auth_ajax({
		type:"GET", url:serverURL + "/api/file/userfile/?file_name=" + name, dataType:"json", success:function(json){
			callback(json);
		}
	}));
}

function getFolderByName(name, callback, errorCallback){
	$.ajax(add_auth_ajax({
		type:"GET", url:serverURL + "/api/file/folder/?name=" + name, dataType:"json", success:function(json){
			callback(json);
		}
	}));
}

function invokeDesktopClient(invoke_type, invoke_data, callback, errorCallback){
	$.ajax(add_auth_ajax({
		type:"POST",
		url:serverURL + '/api/user/auth/invokeDesktopClient/',
		headers:{
			'Content-Type':'application/json; charset=UTF-8'
		},
		data:JSON.stringify({invoke_type:invoke_type, invoke_data:invoke_data}),
		dataType:"json",
		success:function(json){
			if (callback)callback(json);
		}
	}));
}

function createReport2(text, file_id, user_id, detail, callback, errorCallback){
	$.ajax(add_auth_ajax({
		type:"POST",
		url:serverURL + '/api/mongo/sessionView/createReport/',
		headers:{
			'Content-Type':'application/json; charset=UTF-8'
		},
		data:JSON.stringify({
			'text': text,
			'fid': file_id,
			'sid': user_id,
			'detail': detail
		}),
		dataType:"json",
		success:function(json){
			if (callback)callback(json);
		}
	}));
}