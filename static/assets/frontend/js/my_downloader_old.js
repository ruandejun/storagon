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
//var blob;
var chunk_size;
var file_download_link;
var firstChunk=true;
//var stored_file_name = 'tempfile';//Math.random().toString(36).substring(2);
var stored_file_name = file_name;

var start_date;
var cypherWorker = new Worker('/static/assets/frontend/js/worker.js');
var completed = false;
var download_completed = false;
var current_chunk_number = 0;
var total_chunk_number = 0;
var blob_builder = null;
var blob_array = null;
var disableDecryptDownload= false;

if(file_size > 50*1024*1024) chunk_size=10*1024*1024;
else chunk_size=1*1024*1024;

total_chunk_number = Math.floor(file_size/chunk_size);


function errorHandler(e){
	console.log("Error:"+ e.toString());
}

if(navigator.userAgent.indexOf('Chrome')==-1){//not Chrome
	if(file_size > 500*1024*1024){
		disableDecryptDownload = true;
		alert("Your browser doesn't support download and decrypt file over 500 MB. You might want to direct download encrypted file and use our tool to deccrypt.");
	}
	blob_builder = new Blob();
	blob_array = new Array(total_chunk_number-1);
}else{
	blob_builder = null;//not use blob_builder but use FileSystem API
	console.log("Clear temporary FileSystem: stored_file_name="+stored_file_name);
	window.webkitRequestFileSystem(window.TEMPORARY, file_size*2, function(fs) {
		fs.root.getFile(stored_file_name, {create: false}, function(fileEntry) {
			fileEntry.remove(function() {
			  console.log(stored_file_name+' file removed.');
			});
		});
	}, errorHandler);

}


function calculateSizeBlobArray(blobArray){
	var total_size=0;
	for(var i in blobArray){
		if(blobArray[i]==undefined)continue;
		total_size += blobArray[i].size;
	}
	return total_size;
}

function concatBlobBuilder(e){
	var blob = e.data.decrypted_blob;
	if(e.data.lastChunk){
		console.log('LastChunk2');

		blob_builder = new Blob(blob_array);

		var paddingLength = (blob_builder.size+ blob.size) - file_size;
		if(paddingLength>0 && paddingLength<=16){
			blob_builder = new Blob([blob_builder,blob.slice(0,-paddingLength)]);
			console.log("removed paddingLength="+paddingLength);
		}else{
			blob_builder = new Blob([blob_builder,blob]);
			console.log("paddingLength="+paddingLength);
		}


		console.log("LastChunk3");
		if(!completed) {
			$('#result_file').attr('href', URL.createObjectURL(blob_builder));
			$('#result_file').html("Decryption completed! Click me if your file is not saved automaticaly");
			$('#result_file')[0].click();
			completed=true;
		}
	}else {
		//blob_builder = new Blob([blob_builder,blob]);
		blob_array[e.data.chunkNumber-1]=blob;
		//downloadNextChunk();
	}
	console.log('Concat completed.');
	//console.log('File lenght='+ blob_builder.size);

	current_file_size = calculateSizeBlobArray(blob_array);
	console.log('File lenght='+ current_file_size);

	if(download_completed && !completed){
		progress = current_file_size/file_size;
		$('#result_file').html("Download completed. Waiting for Decryption(" + (progress * 100).toFixed(1) + "%)");
	}

	console.log('blob.size='+blob.size);
}
var saveDataReceivedFromWorker = function(e) {
	  if(e.data.cmd=='decrypt_aes') {
		  console.log("Received decrypt chunk_number="+e.data.chunkNumber);
		  //blob = e.data.decrypted_blob;
//                  console.log(blob);
		  if(blob_builder==null){
			  saveBlobTemporary(e.data.decrypted_blob, e.data.chunkNumber)
		  }
		  else{//not Chrome
			  concatBlobBuilder(e);
		  }
	  }
};

console.log('addEventListener')
cypherWorker.addEventListener('message', saveDataReceivedFromWorker, false);

// assumes wordArray is Big-Endian (because it comes from CryptoJS which is all BE)
// From: https://gist.github.com/creationix/07856504cf4d5cede5f9#file-encode-js
var buffer_u8_array = new Uint8Array(chunk_size/4 << 2);

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


function saveBlobTemporary(blob,chunkNumber){

	function successHandler(localstorage){
		//            console.log("Here1");

		var createFile = false;
		if (firstChunk){
			console.log("FirstChunk");//first chunk
			createFile = true;
			firstChunk = false;
		}

		localstorage.root.getFile(stored_file_name, {create:createFile, exclusive:true}, function(fileEntry){
			//                console.log("Here2");
			fileEntry.createWriter(function(fileWriter){
				//                    console.log("Here3");
				fileWriter.onwriteend = function(e){
					console.log('Write-append completed.');
					console.log('File lenght=' + fileWriter.length);
					console.log('blob.size=' + blob.size);
					if (fileWriter.length >= file_size){//lastchunk writed
						console.log('LastChunk3');
						if (!completed){
							$('#result_file').attr('href', fileEntry.toURL());
							$('#result_file').html("Decryption completed! Click me if your file is not saved automaticaly");
							$('#result_file')[0].click();
							completed = true;
						}
					}else{
						if(download_completed && !completed){
							progress = fileWriter.length/file_size;
							$('#result_file').html("Download completed. Waiting for Decryption(" + (progress * 100).toFixed(1) + "%)");
						}
						//downloadNextChunk();
					}
				};

				fileWriter.onerror = function(e){
					console.log('Write failed: ' + e.toString());
				};
				fileWriter.seek(fileWriter.length); // Start write position at EOF.

				if (fileWriter.length + blob.size >= file_size){//lastchunk wrting
					console.log('LastChunk2');
					var paddingLength = (fileWriter.length + blob.size) - file_size;
					if (paddingLength > 0 && paddingLength <= 16){
						fileWriter.write(blob.slice(0, -paddingLength));
						console.log("removed paddingLength=" + paddingLength);
					}else{
						fileWriter.write(blob);
						console.log("paddingLength=" + paddingLength);
					}

				}else{
					fileWriter.write(blob);
				}

			});
		});
	}

	window.webkitRequestFileSystem(window.TEMPORARY, file_size*2, successHandler);
}

function downloadNextChunk(){
	if(received_size>=file_size)return;

	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = handleResponse;
	xhr.addEventListener("progress", updateProgressXHR, false);

	xhr.open("GET", file_download_link);
	if(received_size+2*chunk_size>=file_size){
		xhr.setRequestHeader('Range', 'bytes='+(received_size)+'-');
		console.log("LastChunk");
	}else{
		xhr.setRequestHeader('Range', 'bytes='+(received_size)+'-'+(received_size+chunk_size-1));
	}

	xhr.responseType = 'arraybuffer';
	xhr.send();
}


function handleResponse(){
		if (this.readyState == 4){
			if (this.status == 206 || this.status == 200){//OK or partial responded

				current_chunk_number += 1;
				received_size += this.response.byteLength;
				console.log('received_size=' + received_size + '/' + file_size);

				if (received_size >= file_size){//last chunk received
					console.log('Received lastchunk=' + this.response.byteLength)
					download_completed = true;
					$('#result_file').html("Download completed. Waiting for Decryption...");
					cypherWorker.postMessage({
						'cmd':'decrypt_aes',
						'response':this.response,
						'chunkNumber':current_chunk_number,
						'lastChunk':true
					});

				}else{
					var duration = new Date() - start_date;
					var speed = received_size / duration;
					var progress = received_size / file_size;
					$('#result_file').html("Downloading at " + speed.toFixed(2) + " KB/s (" + (progress * 100).toFixed(1) + "%)");//(1000 bytes/s)

					cypherWorker.postMessage({
						'cmd':'decrypt_aes',
						'response':this.response,
						'chunkNumber':current_chunk_number,
						'lastChunk':false
					});


					downloadNextChunk(); //enable concurrent downloading/decrypting

				}
			}else{
				console.log("Failed to download chunk with error: "+this.statusText);
				max_retry_failed--;
				if(max_retry_failed>0)downloadNextChunk();
			}
		}
}

function updateProgressXHR(oEvent){

	var duration = new Date() - start_date;
	var speed= (received_size+oEvent.loaded) / duration;
	var progress = (received_size+oEvent.loaded ) / file_size;

	$('#result_file').html("Downloading at "+speed.toFixed(2) + " KB/s ("+(progress*100).toFixed(1)+"%)");//(1000 bytes/s)
}


function getEncodedKey(){
	var encodedKey = document.URL.split('#')[1]
	if(encodedKey){
		console.log('Found encodedKey='+encodedKey);
		return encodedKey;
	}
	if(!encodedKey || encodedKey.length!=32){
		alert("FileKey is not detected or malformed, you are not able to decrypt this file!");
		return null;
	}
}

function decryptDownload(download_link){
	if(disableDecryptDownload)return;

	var encodedKey = getEncodedKey();

	cypherWorker.postMessage({
		  'cmd':'init_decrypt_aes',
		  'key': encodedKey,//'000102030405060708090a0b0c0d0e0f',
			'file_size':file_size,
		'chunk_size':chunk_size,
		'store_file_name':stored_file_name,
		'download_link':download_link
	  });

	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = handleResponse;

	xhr.addEventListener("progress", updateProgressXHR, false);

	file_download_link=download_link.slice(0,download_link.lastIndexOf('/'))+'/';

	console.log('file_download_link='+file_download_link);

	xhr.open("GET", file_download_link);
	if(received_size+2*chunk_size>=file_size){
		xhr.setRequestHeader('Range', 'bytes=0-');
		console.log("LastChunk");
	}
	else{
		xhr.setRequestHeader('Range', 'bytes=0-'+(chunk_size-1));
	}
	xhr.responseType = 'arraybuffer';
	xhr.send();
	start_date=new Date();

}