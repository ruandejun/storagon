/**
 * Created by TVA on 1/3/15.
 */

importScripts('/static/assets/frontend/js/cryptojs/aes.js', '/static/assets/frontend/js/cryptojs/mode-ctr-min.js', //'/static/assets/frontend/js/cryptojs/pad-nopadding-min.js',
	'/static/assets/frontend/js/cryptojs/lib-typedarrays-min.js');


/*
 wordArray: { words: [..], sigBytes: words.length * 4 }
 */

// assumes wordArray is Big-Endian (because it comes from CryptoJS which is all BE)
// From: https://gist.github.com/creationix/07856504cf4d5cede5f9#file-encode-js
function convertWordArrayToUint8Array(wordArray, arrayBuffer){
	var len = wordArray.words.length, offset = 0, word, i

	var u8_array;
	if (arrayBuffer != null)u8_array = arrayBuffer;else u8_array = new Uint8Array(len << 2);

	for (i = 0; i < len; i++){
		word = wordArray.words[i];
		u8_array[offset++] = word >> 24;
		u8_array[offset++] = (word >> 16) & 0xff;
		u8_array[offset++] = (word >> 8) & 0xff;
		u8_array[offset++] = word & 0xff;
	}
	return u8_array;
}


var key; //CryptoJS.enc.Hex.parse(e.data.key);
var iv = CryptoJS.enc.Hex.parse('00000000000000000000000000000001');
var aesEncryptor = null;// = CryptoJS.algo.AES.createEncryptor(key, { 'iv': iv });
var aesDecryptor = null;

var reader;
var chunkNumber;
var lastChunk;

var file_size;
var download_link;
//var chunk_size = 1024*1024;
var firstChunk = true;
var chunk_array_buffer;

var xhr = new XMLHttpRequest();
var formData = new FormData();
var target;
var retries = 0;

// Done (either done, failed or retry)
var doneHandler = function(e){
	console.log('response=' + xhr.responseText);
	if (xhr.status == 200){
		if (xhr.responseText.substring(0, 7) == 'file_id'){
			//complete upload
			var file_id = xhr.responseText.substring(8);
			console.log("Upload completed with file_id=" + file_id);
			self.postMessage({
				cmd: 'upload_completed',
				file_id: file_id,
				lastChunk: lastChunk,
				chunkNumber: chunkNumber
			});
		}else{
			//$.resumableObj.uploadNextChunk();
			self.postMessage({
				cmd:'upload_next_chunk',
				lastChunk:lastChunk,
				chunkNumber:chunkNumber
			});
		}
	}else{
		console.log("should retry");
		retries++;
		if(retries>=10)return;
		xhr.open('POST', target);
		xhr.send(formData);
	}
};
xhr.addEventListener('load', doneHandler, false);
xhr.addEventListener('error', doneHandler, false);

xhr.upload.addEventListener('progress', function(e){
	console.log('Progress:'+ e.loaded+'/'+ e.total);
}, false);

function sendEncryptedBlob(encrypted_blob,query,customQuery,headers,withCredentials,target){
	// Set up request and listen for event



	for(k in customQuery){
		query[k] = customQuery[k];
	}

	formData = new FormData();

	for(fieldName in query){
		formData.append(fieldName,query[fieldName]);
	}

	formData.append("file", encrypted_blob);


	xhr.open('POST', target);
	xhr.timeout = 0;
	xhr.withCredentials = withCredentials;

	// Add data from header options
	for(k in headers){
		xhr.setRequestHeader(k, headers[k]);
	}
	xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

	//console.log(data)
	//console.log(xhr);
	encrypted_blob = null;

	xhr.send(formData);
	formData=null;
}

function encryptAES(rawArrayBuffer){


	//Correct counter CTR
	var counter = 1 + chunk_size / 16 * (chunkNumber - 1);
	var modeCounter = [0, 0, 0, counter];
	//console.log(modeCounter);
	if (aesEncryptor == null){
		//actually init encryptor
		var hexCounter = counter.toString(16);
		prefix = '';
		for (var i = 0; i < 32 - hexCounter.length; i++)prefix += '0';
		hexCounter = prefix + hexCounter;
		//console.log(hexCounter);
		iv = CryptoJS.enc.Hex.parse(hexCounter);
		aesEncryptor = CryptoJS.algo.AES.createEncryptor(key, {mode:CryptoJS.mode.CTR, 'iv':iv}); // padding: CryptoJS.pad.NoPadding,
	}
	aesEncryptor._mode._counter = modeCounter;
	counter = null;
	modeCounter = null;
	hexCounter = null;

	var data = aesEncryptor.process(CryptoJS.lib.WordArray.create(rawArrayBuffer));
	//console.log(aesEncryptor._mode._counter);

	var encrypted_blob;

	if (firstChunk && !lastChunk){
		encrypted_blob = new Blob([convertWordArrayToUint8Array(data)]);
		firstChunk = false;
	}else{
		if (lastChunk){
			console.log("LastChunk3");
			encrypted_blob = new Blob([convertWordArrayToUint8Array(data), convertWordArrayToUint8Array(aesEncryptor.finalize())]);
		}else encrypted_blob = new Blob([convertWordArrayToUint8Array(data, chunk_array_buffer)]);
	}

	encrypted_blob = new Blob([rawArrayBuffer]);
	console.log('aes encrypted blob size:' + encrypted_blob.size);


	//self.postMessage({
	//	cmd:'encrypt_aes', 'encrypted_blob':encrypted_blob, //encrypted_buffer: rawArrayBuffer,
	//	lastChunk:lastChunk, chunkNumber:chunkNumber
	//});
	data = null;
	return encrypted_blob;

}

self.addEventListener('message', function(e){
	var cmd = e.data.cmd;
	console.log("worker: cmd=" + cmd);

	if (cmd == 'init_encrypt_aes'){
		file_size = e.data.file_size;
		chunk_size = e.data.chunk_size;

		console.log("Init AES Encryptor with key=" + e.data.key);
		key = CryptoJS.enc.Hex.parse(e.data.key);
		//aesEncryptor = CryptoJS.algo.AES.createEncryptor(key, {mode: CryptoJS.mode.CTR, 'iv': iv }); // padding: CryptoJS.pad.NoPadding,
		aesEncryptor = null;

		chunk_array_buffer = new Uint8Array(chunk_size);
		reader = new FileReaderSync();

	}

	if (cmd == 'encrypt_aes'){

		//console.log('encrypting aes of size:'+blob.size);
		chunkNumber = e.data.chunkNumber;
		lastChunk = e.data.lastChunk;

		target = e.data.target;

		var rawArrayBuffer = reader.readAsArrayBuffer(e.data.blob);

		var encrypted_blob = encryptAES(rawArrayBuffer); //
		//e.data.blob = null;
		//rawArrayBuffer = null;
		delete rawArrayBuffer;

		sendEncryptedBlob(encrypted_blob, e.data.query, e.data.customQuery, e.data.headers, e.data.withCredentials, e.data.target);
		//self.postMessage({
		// cmd: 'encrypt_aes',
		// 'encrypted_blob':e.data.blob,
		// //encrypted_buffer: rawArrayBuffer,
		// lastChunk : lastChunk,
		// chunkNumber: chunkNumber
		//}//,[rawArrayBuffer]
		//);
		//if (rawArrayBuffer.byteLength>0) {
		//  console.log('Transferables are not supported in your browser!');
		//} else {
		//  console.log('Transferables are supported');
		//}

		//reader = null;

	}

}, false);