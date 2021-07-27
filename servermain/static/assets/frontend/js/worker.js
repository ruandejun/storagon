/**
 * Created by TVA on 1/3/15.
 */

importScripts('/static/assets/frontend/js/cryptojs/aes.js',
			  '/static/assets/frontend/js/cryptojs/mode-ctr-min.js',
			  //'/static/assets/frontend/js/cryptojs/pad-nopadding-min.js',
			  '/static/assets/frontend/js/cryptojs/lib-typedarrays-min.js'
              );


/*
wordArray: { words: [..], sigBytes: words.length * 4 }
*/

// assumes wordArray is Big-Endian (because it comes from CryptoJS which is all BE)
// From: https://gist.github.com/creationix/07856504cf4d5cede5f9#file-encode-js
function convertWordArrayToUint8Array(wordArray,arrayBuffer) {
	var len = wordArray.words.length, offset = 0, word, i

	var u8_array;
	if(arrayBuffer!=null)u8_array=arrayBuffer;
	else u8_array = new Uint8Array(len << 2);

	for (i=0; i<len; i++) {
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
var aesEncryptor=null;// = CryptoJS.algo.AES.createEncryptor(key, { 'iv': iv });
var aesDecryptor=null;

var reader;
var chunkNumber;
var lastChunk;

var file_size;
var download_link;
//var chunk_size = 1024*1024;
var firstChunk=true;
var chunk_array_buffer;



function encryptAES(rawArrayBuffer){
	var encrypted_blob=rawArrayBuffer;

	//Correct counter CTR
	counter = 1+chunk_size/16*(chunkNumber-1);
	modeCounter = [0,0,0,counter];
	//console.log(modeCounter);
    if(aesEncryptor==null){
		//actually init encryptor
		hexCounter = counter.toString(16);
		prefix='';
		for(var i=0;i<32-hexCounter.length;i++)prefix+='0';
		hexCounter=prefix+hexCounter;
		//console.log(hexCounter);
		iv = CryptoJS.enc.Hex.parse(hexCounter);
		aesEncryptor = CryptoJS.algo.AES.createEncryptor(key, {mode: CryptoJS.mode.CTR, 'iv': iv }); // padding: CryptoJS.pad.NoPadding,
	}
	//aesEncryptor._mode._counter = modeCounter;

	var data = aesEncryptor.process(CryptoJS.lib.WordArray.create(encrypted_blob));
	console.log(aesEncryptor._mode._counter);

	if(firstChunk && !lastChunk){
		encrypted_blob = new Blob([convertWordArrayToUint8Array(data)]);
		firstChunk=false;
	}else{
		if(lastChunk){
		  console.log("LastChunk3");
		  encrypted_blob = new Blob([convertWordArrayToUint8Array(data), convertWordArrayToUint8Array(aesEncryptor.finalize()) ]);
		}
		else encrypted_blob = new Blob([convertWordArrayToUint8Array(data, chunk_array_buffer)]);
	}

	//encrypted_blob = new Blob([rawArrayBuffer]);
	//console.log('aes encrypted blob size:'+encrypted_blob.size);
	self.postMessage({
		 'cmd':'encrypt_aes',
		 'encrypted_blob':encrypted_blob,
			'lastChunk' : lastChunk,
			'chunkNumber': chunkNumber
	 });
	encrypted_blob = null;
}

self.addEventListener('message', function(e) {


    var cmd= e.data.cmd;
	console.log("worker: cmd="+cmd);

	if(cmd=='init_decrypt_aes') {
		file_size = e.data.file_size;
		chunk_size = e.data.chunk_size;

		download_link = e.data.download_link;
		stored_file_name = e.data.stored_file_name;
		console.log("Init AES Decryptor with key="+e.data.key);

		key = CryptoJS.enc.Hex.parse(e.data.key);
		//aesDecryptor = CryptoJS.algo.AES.createDecryptor(key, {mode: CryptoJS.mode.CTR, 'iv': iv });// padding: CryptoJS.pad.NoPadding,
		aesDecryptor=null;

		chunk_array_buffer = new Uint8Array(chunk_size);
		//console.log('chunk_array_buffer='+chunk_array_buffer.length);
	}

	if(cmd=='decrypt_aes'){
		chunkNumber = e.data.chunkNumber;
		lastChunk = e.data.lastChunk;

		var decrypted_blob;

		//Correct counter CTR
		counter = 1+chunk_size/16*(chunkNumber-1);
		if(chunkNumber>1)counter--; //fix bug decryping first chunk lack of 1 block
		modeCounter = [0,0,0,counter];
		console.log(modeCounter);

		if(aesDecryptor==null){
			//actually init encryptor
			hexCounter = counter.toString(16);
			prefix='';
			for(var i=0;i<32-hexCounter.length;i++)prefix+='0';
			hexCounter=prefix+hexCounter;
			//console.log(hexCounter);
			iv = CryptoJS.enc.Hex.parse(hexCounter);
			aesDecryptor = CryptoJS.algo.AES.createDecryptor(key, {mode: CryptoJS.mode.CTR, 'iv': iv });// padding: CryptoJS.pad.NoPadding,
			//if(chunkNumber!=1)aesDecryptor.process(CryptoJS.lib.WordArray.create(e.data.response));//decrypt twice to fix bug lack of 1 block in first decrypted chunk
		}
		aesDecryptor._mode._counter = modeCounter;

		var data = aesDecryptor.process(CryptoJS.lib.WordArray.create(e.data.response));
		console.log(aesDecryptor._mode._counter);

		if(firstChunk && !lastChunk){
			decrypted_blob = new Blob([convertWordArrayToUint8Array(data)]);
			firstChunk=false;
		}else {
			if (lastChunk){
				console.log("LastChunk2");
				decrypted_blob = new Blob([convertWordArrayToUint8Array(data), convertWordArrayToUint8Array(aesDecryptor.finalize())]);
			}
			else decrypted_blob = new Blob([convertWordArrayToUint8Array(data,chunk_array_buffer)]);//
		}


		self.postMessage({
			 'cmd':'decrypt_aes',
			 'decrypted_blob':decrypted_blob,
			'lastChunk' : lastChunk,
			'chunkNumber': chunkNumber
		});
		decrypted_blob=null;
		data=null;

	}

	if(cmd=='init_encrypt_aes') {
		file_size = e.data.file_size;
		chunk_size = e.data.chunk_size;

		console.log("Init AES Encryptor with key="+e.data.key);
		key = CryptoJS.enc.Hex.parse(e.data.key);
		//aesEncryptor = CryptoJS.algo.AES.createEncryptor(key, {mode: CryptoJS.mode.CTR, 'iv': iv }); // padding: CryptoJS.pad.NoPadding,
		aesEncryptor=null;

		chunk_array_buffer = new Uint8Array(chunk_size );


		//reader = new FileReaderSync();


	}

    if(cmd=='encrypt_aes') {

		//console.log('encrypting aes of size:'+blob.size);
		chunkNumber = e.data.chunkNumber;
		lastChunk = e.data.lastChunk;
		reader = new FileReaderSync();
		//reader = new FileReader();
		//
		//reader.onload = function(e) {
        //  console.log("Reader sucesss:" + e.target.result);
        //  	reader = null;
			//encryptAES(e.target.result);
        //};
		//
		//reader.onerror = function(stuff) {
        //  console.log("reader error:"+ stuff);
        //  console.log(stuff.getMessage())
        //};
		//
        //reader.readAsArrayBuffer(e.data.blob);

		encryptAES(reader.readAsArrayBuffer(e.data.blob));
		reader=null;
    }

}, false);