/** JavaScript on WebKit
 *
 *  my_downloader.js
 *
 *
 *  Created by TVA on 3/28/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */


//file_size > 50mb

var max_retry_failed = 10;
var received_size = 0;

var chunk_size;
var file_download_link;
var firstChunk=true;
var stored_file_name = file_id+'_'+file_name;

var start_date;

var completed = false;
var download_completed = false;
var current_chunk_number = 0;
var total_chunk_number = 0;
var blob_builder = null;
var blob_array = null;
var disableDecryptDownload= false;
var encodedKey;
String.prototype.toHHMMSS = function () {
    var sec_num = parseInt(this, 10); // don't forget the second param
    var hours   = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    var seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    var time    = hours+':'+minutes+':'+seconds;
    return time;
};

if(file_size > 50*1024*1024){
	chunk_size=10*1024*1024;
}
else chunk_size=1*1024*1024;


total_chunk_number = Math.floor(file_size/chunk_size);

var FileSystemType = window.PERSISTENT;
var FileSystemSpace = file_size*3;
if(FileSystemSpace < 6*1024*1024*1024) {
	FileSystemType = window.TEMPORARY;
	FileSystemSpace=6*1024*1024*1024;
}

function errorHandler(e){
	console.log("Error:"+ e.toString());
    console.log(e);
    if(typeof(e) == 'object' && 'name' in e)
    switch (e.name) {
        case "NotFoundError":
          // The File or Blob could not be found at the time the read was processed.
          break;
        case "SecurityError":
          $('#modal-error p.modal-body').html("Security Error! If you are using browser in incognito" +
          " mode, you can only download encrypted file directly then use our app to decrypt it. " +
          "You can download decrypt tool by clicking this link: " +
          "<a href='http://storagon.com/download/storagon_tool/storagon_client_setup.rar'>Decrypt tool</a> (For Window).<br/>" +
          "If you still want to download decrypted file by browser, please switch your browser to normal mode.");
          $('#modal-error a.close').html("Close");
          $('#modal-error').foundation('reveal', 'open');
          $('#freedl').hide();
          break;
        case "AbortError":
          // The read operation was aborted, typically with a call to abort().
          break;
        case "NotReadableError":
          // The File or Blob cannot be read, typically due due to permission problems that occur after a reference to a File or Blob has been acquired (concurrent lock with another application).
          break;
        case "EncodingError":
          // The length of the data URL for a File or Blob is too long.
          break;
      }
}
console.log(navigator.userAgent.indexOf('Chrome') === -1)
if(navigator.userAgent.indexOf('Chrome') === -1){//not Chrome
  console.log("test")
	if(file_size > 500*1024*1024){
		disableDecryptDownload = true;        
	}
	blob_builder = new Blob();
	if(total_chunk_number>1)blob_array = new Array(total_chunk_number-1);
	else blob_array = new Array(1);
}else{
	blob_builder = null;//not use blob_builder but use FileSystem API
	console.log("Init temporary FileSystem: stored_file_name="+stored_file_name);

	window.webkitStorageInfo.requestQuota(FileSystemType, FileSystemSpace, function(grantedBytes) {
		disableDecryptDownload = false;
		console.log("requestQuota success with total storage="+grantedBytes);
		clearFileSystemStorage();
	}, function(e) {
		disableDecryptDownload = true;
		$('#modal-error p.modal-body').html("You need to enable our website to store file in your machine in order to download this file due to its big size. Please reload page (F5) and choose Allow.");
		$('#modal-error a.close').html("Close");
		$('#modal-error').foundation('reveal', 'open');

		switch (e.code) {
			case FileError.QUOTA_EXCEEDED_ERR:
			  msg = 'QUOTA_EXCEEDED_ERR';
			  break;
			case FileError.NOT_FOUND_ERR:
			  msg = 'NOT_FOUND_ERR';
			  break;
			case FileError.SECURITY_ERR:
			  msg = 'SECURITY_ERR';
			  break;
			case FileError.INVALID_MODIFICATION_ERR:
			  msg = 'INVALID_MODIFICATION_ERR';
			  break;
			case FileError.INVALID_STATE_ERR:
			  msg = 'INVALID_STATE_ERR';
			  break;
			default:
			  msg = 'Unknown Error';
			  break;
		};
		console.log("Error when requestQuota", msg);
	});

}

function clearFileSystemStorage(){
	window.webkitRequestFileSystem(FileSystemType, FileSystemSpace, function(fs){
		fs.root.getFile(stored_file_name, {create:false}, function(fileEntry){
			fileEntry.remove(function(){
				console.log(stored_file_name + ' file removed.');
			});
		});
	}, errorHandler);

	navigator.webkitPersistentStorage.queryUsageAndQuota(function(storage_used, storage_left){
		console.log("Storage used=" + storage_used + " left=" + storage_left);
		if(storage_left < file_size*2.2){
			console.log('Initiate clear filesystem storage');
			window.webkitRequestFileSystem(FileSystemType, FileSystemSpace, function(fs){
				var dirReader = fs.root.createReader();
				var entries = [];

				// Call the reader.readEntries() until no more results are returned.
				var readEntries = function() {
					dirReader.readEntries (function(results) {
						if (!results.length) {
							console.log('Clear all file in root');
							removeAllFileEntries(fs, entries.sort());
						}else {
							entries = entries.concat(toArray(results));
							readEntries();
						}
					}, errorHandler);
				};
				readEntries(); // Start reading dirs.
			}, errorHandler);
		}
	});
}



function toArray(list) {
  return Array.prototype.slice.call(list || [], 0);
}

function removeAllFileEntries(fs, entryList){
	for(var i in entryList){
		var fileEntry = entryList[i];
		if(fileEntry.isFile){
			fileEntry.remove(function(){
				console.log(fileEntry.name + ' removed.');
			});
		}
	}
}


function calculateSizeBlobArray(blobArray){
	var total_size=0;
	for(var i in blobArray){
		if(blobArray[i] === undefined)continue;
		total_size += blobArray[i].size;
	}
	return total_size;
}

function concatBlobBuilder(encrypted_blob, chunkNumber) {

	var reader = new FileReader();
	reader.readAsArrayBuffer(encrypted_blob);

	reader.onerror = function (e) {
		console.log("Error read chunk number: " + chunkNumber);
	};
	reader.onloadend = function (e) {
		//console.log("Reading data="+this.result);

		var blob = decrypt_arrayBuffer(this.result, chunkNumber);

		if (chunkNumber == total_chunk_number) {
			console.log('LastChunk2');

			blob_builder = new Blob(blob_array);

			var paddingLength = (blob_builder.size + blob.size) - file_size;
			if (paddingLength > 0 && paddingLength <= 16) {
				blob_builder = new Blob([blob_builder, blob.slice(0, -paddingLength)]);
				console.log("removed paddingLength=" + paddingLength);
			} else {
				blob_builder = new Blob([blob_builder, blob]);
				console.log("paddingLength=" + paddingLength);
			}


			console.log("LastChunk3");
			if (!completed) {
				$('#result_file').attr('href', URL.createObjectURL(blob_builder));
				$('#result_file').html("Decryption completed! Click me if your file is not saved automaticaly");
				$('#result_file')[0].click();

				completed = true;
			}
		} else {
			//blob_builder = new Blob([blob_builder,blob]);
			blob_array[chunkNumber - 1] = blob;
			//downloadNextChunk();
		}
		console.log('Concat completed.');
		//console.log('File lenght='+ blob_builder.size);

		current_file_size = calculateSizeBlobArray(blob_array);
		console.log('File lenght=' + current_file_size);

		if (download_completed && !completed) {
			progress = current_file_size / file_size;
			$('#result_file').html("Download completed. Waiting for Decryption(" + (progress * 100).toFixed(1) + "%)");
		}

		console.log('blob.size=' + blob.size);

	}
}
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




function readAndAppendFile(chunk_index, fileEntry, localstorage){
	localstorage.root.getFile(stored_file_name+'_part_'+chunk_index, {exclusive:true}, function(fileChunkEntry){
		console.log('Open file for concating: '+stored_file_name+'_part_'+chunk_index);
		fileChunkEntry.file(function(fileChunk) {
			var reader = new FileReader();

			//reader.readAsArrayBuffer(fileChunk);
            //
			//reader.onerror = function(e) {
			//	console.log("Error read chunk: "+stored_file_name+'_part_'+chunk_index);
			//};
			//reader.onloadend = function(e) {
				//console.log("Reading data="+this.result);

				//var chunk_blob = decrypt_arrayBuffer(this.result,chunk_index);
				var chunk_blob = fileChunk

				fileEntry.createWriter(function(fileWriter){

					fileWriter.seek(fileWriter.length); // Start write position at EOF.

					if(fileWriter.length+chunk_blob.size >= file_size){
						console.log('LastChunk: RemovePadding check when file length='+fileWriter.length+' last chunk_blob='+chunk_blob.size);
						var paddingLength = (fileWriter.length + chunk_blob.size) - file_size;
						if (paddingLength > 0 && paddingLength <= 16){//
							fileWriter.write(chunk_blob.slice(0, -paddingLength));
							console.log("removed paddingLength=" + paddingLength);
						}else{
							fileWriter.write(chunk_blob);
							console.log("paddingLength=" + paddingLength);
						}
					}else{
						fileWriter.write(chunk_blob);
					}

					fileWriter.onwriteend = function(e){
						console.log('Write-append completed with chunk_index='+chunk_index);
						//fileChunkEntry.remove(function(){
						//	console.log(fileChunkEntry.name + ' removed.');
						//});
						$('#result_file').html("Download completed. Waiting for Decryption(" + (chunk_index*100.0/total_chunk_number).toFixed(1) + "%)");
						if (chunk_index < total_chunk_number){
							readAndAppendFile(chunk_index+1, fileEntry, localstorage);
						}else{
							//completed
                            loader.setProgress(1);
							$('#result_file').attr('href', fileEntry.toURL());
							$('#result_file')[0].click();
							$('#result_file').html("Decryption completed! Click me if your file is not saved automaticaly");
						}
					};
					//end file writing
				});
			//};
		});
	},function(e){
      console.log("Error "+e+" open file: "+stored_file_name+'_part_'+chunk_index);
    }
	);
}
function concatFileEntry(){
	window.webkitRequestFileSystem(FileSystemType, FileSystemSpace, function (localstorage){
		localstorage.root.getFile(stored_file_name, {create:true, exclusive:false}, function(fileEntry){

			var chunk_index = 1;
			//for(chunk_index=1;chunk_index<=total_chunk_number;chunk_index++){

			readAndAppendFile(chunk_index, fileEntry, localstorage);

		});

	},function(e){
      console.log("Error "+e+" open file: "+stored_file_name);
    }
	);
}
function saveBlobTemporary(downloaded_array_buffer,chunkNumber){

	var blob = decrypt_arrayBuffer(downloaded_array_buffer, chunkNumber);

	function successHandler(localstorage) {

		//localstorage.root.getFile(stored_file_name, {create:createFile, exclusive:true}, function(fileEntry){
		localstorage.root.getFile(stored_file_name + '_part_' + chunkNumber, {
				create: true,
				exclusive: false
			}, function (fileEntry) {
				console.log("Open file for writing chunk: " + stored_file_name + '_part_' + chunkNumber);
				fileEntry.createWriter(function (fileWriter) {
					//                    console.log("Here3");
					fileWriter.onwriteend = function (e) {
						//console.log('Write-append completed.');
						console.log('File length=' + fileWriter.length);
						console.log('blob.size=' + blob.size);
						if (chunkNumber >= total_chunk_number) {//lastchunk writed
							console.log('LastChunk: All Chunk Received');
							concatFileEntry();
							if (!completed) {
								completed = true;
							}
						} else {
							if (download_completed && !completed) {
								progress = chunkNumber * 1.00 / total_chunk_number;
								$('#result_file').html("Download completed. Waiting for Decryption(" + (progress * 100).toFixed(1) + "%)");
								$('#result_file').show();
							}
							//downloadNextChunk();
						}
					};

					fileWriter.onerror = function (e) {
						console.log('Write failed: ' + e.toString());
					};

					fileWriter.write(blob);

				});
			}, function (e) {
				console.log("Error " + e + " open file: " + stored_file_name + '_part_' + chunkNumber);
			}
		);
	}

	window.webkitRequestFileSystem(FileSystemType, FileSystemSpace, successHandler);

}

function downloadNextChunkIfChunkNotAlreadyExist(){
	var chunk_index=current_chunk_number+1;

	window.webkitRequestFileSystem(FileSystemType, FileSystemSpace, function (localstorage){
		localstorage.root.getFile(stored_file_name+'_part_'+chunk_index, {exclusive:true}, function(fileChunkEntry){
			//geting fileChunkSize
			fileChunkEntry.getMetadata(function(metadata) {
				console.log("fileChunk of chunk_index="+chunk_index+" exist with fileChunkSize="+metadata.size);
				downloadNext=true;

				if(chunk_index === total_chunk_number){
					if(metadata.size > chunk_size)downloadNext=false //last chunk, check > chunk_size only
				}

				if(chunk_index >= 1 && chunk_index < total_chunk_number){
					if(metadata.size === chunk_size) downloadNext = false;
				}

				if(downloadNext === false){
					current_chunk_number++;
					received_size+=metadata.size;
					console.log("chunk_number=" + current_chunk_number + " already exist");
					console.log('received_size=' + received_size + '/' + file_size);
					if (current_chunk_number === total_chunk_number){//lastchunk received
						console.log('LastChunk: All Chunk Received');
						concatFileEntry();
					}else{//keep going
						downloadNextChunkIfChunkNotAlreadyExist();
					}
				}else{
					downloadNextChunk();
				}

			});

		},function(e){
				console.log("chunk_index=" + chunk_index + " not exist");
				downloadNextChunk();
			}
		);
	});
}


function downloadNextChunk(){  
	if(received_size >= file_size) return;
	console.log("Downloading chunk_number="+(current_chunk_number+1));
	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = handleResponse;
	xhr.addEventListener("progress", updateProgressXHR, false);

	xhr.open("GET", file_download_link);
	if(received_size+2*chunk_size >= file_size){
		xhr.setRequestHeader('Range', 'bytes='+(received_size)+'-');
		console.log("LastChunk");
	}else{
		xhr.setRequestHeader('Range', 'bytes='+(received_size)+'-'+(received_size+chunk_size-1));
	}

	xhr.responseType = 'arraybuffer';
	//xhr.responseType = 'blob';
	xhr.send();
}


function handleResponse(){
		if (this.readyState === 4){
			if (this.status === 206 || this.status === 200){//OK or partial responded

				current_chunk_number += 1;
				//responseLength = this.response.size; //blob
				responseLength = this.response.byteLength; //array buffer

				received_size += responseLength;
				console.log('received_size=' + received_size + '/' + file_size);

				if (received_size >= file_size){//last chunk received
					console.log('Received lastchunk=' + responseLength);
					download_completed = true;
					$('#result_file').html("Download completed. Waiting for Decryption...");
					$('#result_file').show();

					if(blob_builder === null){
						saveBlobTemporary(this.response, current_chunk_number);
					}
					else{//not Chrome
						concatBlobBuilder(this.response, current_chunk_number);
					}

				}else{
					var duration = new Date() - start_date;
					var speed = received_size / duration;
					var progress = received_size / file_size;
//					$('#result_file').html("Downloading at " + speed.toFixed(2) + " KB/s (" + (progress * 100).toFixed(1) + "%)");//(1000 bytes/s)
					loader.setValue(speed.toFixed(2) + " KB/s");
    				loader.setProgress(progress);

                    if(blob_builder === null){
						saveBlobTemporary(this.response, current_chunk_number);
						downloadNextChunkIfChunkNotAlreadyExist();
                    }					
					else{//not Chrome
						concatBlobBuilder(this.response, current_chunk_number);
                    	downloadNextChunk();
                    }

				}
			}else{
				console.log("Failed to download chunk with error: "+this.statusText);
				max_retry_failed--;
				if(max_retry_failed>0){
					downloadNextChunk();
				}
			}
		}
}

function updateProgressXHR(oEvent){
	var duration = new Date() - start_date;
	var speed= (received_size+oEvent.loaded) / duration;
	var progress = (received_size+oEvent.loaded ) / file_size;
    var timeLeft = (((file_size - received_size)/1024) / speed).toFixed(0).toHHMMSS();
    
    $('#result_file').html("Time start: " + (duration/1000).toString().toHHMMSS() + ". Elapsed time: "+timeLeft);
    loader.setValue(speed.toFixed(2) + " KB/s");
    loader.setProgress(progress);
}


function getEncodedKey(){
	if(encodedKey){
		console.log('Found encodedKey='+encodedKey);
		return encodedKey;
	}
	if(!encodedKey || encodedKey.length !== 32){
        $('#modal-error p.modal-body').html("FileKey is not detected or malformed, you are not able to decrypt this file!");
        $('#modal-error a.close').html("Close");
        $('#modal-error').foundation('reveal', 'open');		
		return null;
	}
}

var encodedKey = null;
var aesDecryptor = null;

function decryptDownload(download_link){
	if(disableDecryptDownload)return;

	encodedKey = getEncodedKey();

	chunk_array_buffer = new Uint8Array(chunk_size);
	//var key = CryptoJS.enc.Hex.parse(encodedKey);
	//var iv = CryptoJS.enc.Hex.parse('00000000000000000000000000000001');
	//console.log("Init AES Decryptor with key="+encodedKey);
	//aesDecryptor = CryptoJS.algo.AES.createDecryptor(key, {mode: CryptoJS.mode.CTR, 'iv': iv });// padding: CryptoJS.pad.NoPadding,

	file_download_link=download_link.slice(0,download_link.lastIndexOf('/'))+'/';

	console.log('file_download_link='+file_download_link);
	console.log('total_chunk_number='+total_chunk_number);

	if(blob_builder === null) {
		downloadNextChunk();
		//downloadNextChunkIfChunkNotAlreadyExist()
	}else{
		downloadNextChunk(); //Alway download first chunk to avoid bug in resume decrypting
	}

	start_date=new Date();

}

var chunk_array_buffer = null;

function decrypt_arrayBuffer(arrayBuffer,chunk_number){
	console.log("decrypting chunk_number="+chunk_number+" arrayBuffer.byteLength="+arrayBuffer.byteLength);

	//Correct counter CTR
	counter = 1+chunk_size/16*(chunk_number-1);
	if(chunk_number>1)counter--; //fix bug decryping first chunk lack of 1 block
	modeCounter = [0,0,0,counter];
	console.log(modeCounter);

	if(aesDecryptor==null){
		//actually init encryptor
		console.log("Init AES128 Decryptor with key="+encodedKey);
		key = CryptoJS.enc.Hex.parse(encodedKey);

		hexCounter = counter.toString(16);
		prefix='';
		for(var i=0;i<32-hexCounter.length;i++)prefix+='0';
		hexCounter=prefix+hexCounter;
		//console.log(hexCounter);
		iv = CryptoJS.enc.Hex.parse(hexCounter);
		aesDecryptor = CryptoJS.algo.AES.createDecryptor(key, {mode: CryptoJS.mode.CTR, 'iv': iv });// padding: CryptoJS.pad.NoPadding,
	}
	aesDecryptor._mode._counter = modeCounter;

	var data = aesDecryptor.process(CryptoJS.lib.WordArray.create(arrayBuffer));
	console.log(aesDecryptor._mode._counter);

	if (chunk_number==total_chunk_number){
		console.log("LastChunk2");
		decrypted_blob = new Blob([convertWordArrayToUint8Array(data), convertWordArrayToUint8Array(aesDecryptor.finalize())]);
		//decrypted_blob = new Blob([convertWordArrayToUint8Array(data)]);
	}
	else decrypted_blob = new Blob([convertWordArrayToUint8Array(data,chunk_array_buffer)]);//

	return decrypted_blob;
}

function convertHexToByteArray(hexString){
	var ba = new Array(hexString.length);
	for(var i=0;i<hexString.length;i++ ){
		c=hexString[i];
		switch (c){
			case '0': ba[i]=0;break;
			case '1': ba[i]=1;break;
			case '2': ba[i]=2;break;
			case '3': ba[i]=3;break;
			case '4': ba[i]=4;break;
			case '5': ba[i]=5;break;
			case '6': ba[i]=6;break;
			case '7': ba[i]=7;break;
			case '8': ba[i]=8;break;
			case '9': ba[i]=9;break;
			case 'A': ba[i]=10;break;
			case 'B': ba[i]=11;break;
			case 'C': ba[i]=12;break;
			case 'D': ba[i]=13;break;
			case 'E': ba[i]=14;break;
			case 'F': ba[i]=15;break;
			case 'a': ba[i]=10;break;
			case 'b': ba[i]=11;break;
			case 'c': ba[i]=12;break;
			case 'd': ba[i]=13;break;
			case 'e': ba[i]=14;break;
			case 'f': ba[i]=15;break;
		}
	}
	return ba;
}