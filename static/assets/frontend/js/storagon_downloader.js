/**
 * Created by dungdc40 on 8/13/15.
 */
/** JavaScript on WebKit
 *
 *  my_downloader.js
 *
 *
 *  Created by TVA on 3/28/15.
 *  Copyright (c) 2015 storagon. All rights reserved.
 */


//file_size > 50mb
var received_size = 0;

var chunk_size;
var file_download_link;
var firstChunk=true;
var stored_file_name = file_id+'_'+file_name;
var support_fs = false;
var worker = new Worker('/static/assets/frontend/js/storagon_worker.js');
var download_completed = false;
var total_chunk_number = 0;
var dl_chunk_arr = [];
var downloaded_chunk_arr = [];
var decrypt_chunk_arr = [];
var decrypted_chunk_arr = [];
var disableDecryptDownload= false;
var encodedKey;
var downloading_chunk =0;
if(file_size > 50*1024*1024){
	chunk_size=10*1024*1024;
}
else chunk_size=1*1024*1024;

total_chunk_number = Math.ceil(file_size/chunk_size);

var FileSystemType = window.PERSISTENT;
var FileSystemSpace = file_size*3;
if(FileSystemSpace < 6*1024*1024*1024) FileSystemSpace=6*1024*1024*1024;

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
}else{
    support_fs = true;
	console.log("Init temporary FileSystem: stored_file_name="+stored_file_name);

    //FileSystemType = window.PERSISTENT;
    //FileSystemSpace = 10*1024*1024*1024;
    window.webkitStorageInfo.requestQuota(FileSystemType, FileSystemSpace, function(grantedBytes) {
        console.log("requestQuota success");
        clearFileSystemStorage();
    }, function(e) {
        disableDecryptDownload = true;
        $('#modal-error p.modal-body').html("You need to enable our website to store file in your machine in order to download this file due to its big size. Please reload page (F5) and choose Allow.");
        $('#modal-error a.close').html("Close");
        $('#modal-error').foundation('reveal', 'open');
        console.log("Error when requestQuota", e);
    });


	if(!disableDecryptDownload){
		clearFileSystemStorage();
	}
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

function download_chunk(){
    while(downloading_chunk < 1){ // only download 1 chunk at a time
        if(dl_chunk_arr.length > 0) {
            var chunk_number = dl_chunk_arr.shift();
            worker.postMessage({
                'cmd': 'download_chunk',
                'chunkNumber': chunk_number
            });
            downloading_chunk++;
        }
        else break;
    }
}

function decrypt_chunk(){
    if(decrypt_chunk_arr.length > 0){
            var chunk_number = decrypt_chunk_arr.shift();
            worker.postMessage({
                'cmd': 'decrypt_chunk',
                'chunkNumber': chunk_number
            });
    }
}

function append_decrypted_chunk(chunk_number, time_try){
    if(decrypted_chunk_arr.length > 0){
        if(decrypted_chunk_arr[0] == chunk_number) {
            decrypted_chunk_arr.shift();
            worker.postMessage({
                'cmd': 'append_decrypted_chunk',
                'chunkNumber': chunk_number
            });
        }
        else{
            console.error('order of decrypted chunk not true');
            console.error('decrypted chunk: ' + chunk_number);
            console.error(decrypted_chunk_arr);
        }
    }
    else{
        // chunk haven't completely decrypted, wait until it complete to append it
        time_try--;
        if(time_try > 0) {
            setTimeout(function () {
                append_decrypted_chunk(chunk_number, time_try)
            }, 500);
        }
    }

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

function decryptDownload(download_link){
	if(disableDecryptDownload){
        alert("Your browser doesn't support decrypt download or the file is too big to decrypt. Please download the file" +
        "directly and use our tool to decrypt it");
        return;
    }

	var encodedKey = getEncodedKey();

	worker.postMessage({
		'cmd':'init_decrypt_aes',
		'key': encodedKey,//'000102030405060708090a0b0c0d0e0f',
		'file_size':file_size,
        'fs_type': FileSystemType,
        'fs_space': FileSystemSpace,
		'chunk_size':chunk_size,
        'total_chunk': total_chunk_number,
		'stored_file_name':stored_file_name,
		'file_download_link':download_link.slice(0,download_link.lastIndexOf('/'))+'/',
        'support_fs': support_fs
	  });

    // initilize chunk arrat to keep track download
    console.log('Total chunk:' + total_chunk_number);
    var i;
    for(i=1; i <= total_chunk_number; i++)
        dl_chunk_arr.push(i);

    console.log(dl_chunk_arr);
	file_download_link=download_link.slice(0,download_link.lastIndexOf('/'))+'/';
	console.log('file_download_link='+file_download_link);

    // download first chunk
	download_chunk(); //Alway download first chunk to avoid bug in resume decrypting
}

worker.addEventListener('message', function(e){
    var cmd= e.data.cmd;
    var progress;
    if(cmd == 'download_progress'){
        var speed = e.data.speed;
        progress = e.data.progress;
        var time_left = e.data.time_left;
        var time_start = e.data.time_start;
        $('#result_file').html("Time start: " + time_start + ". Elapsed time: "+time_left);
        loader.setValue(speed.toFixed(2) + " KB/s");
        loader.setProgress(progress);
    }
    else if(cmd == 'dl_chunk_complete'){
        var chunk_number = e.data.chunk_number;
        downloading_chunk--;
        // not last chunk
        downloaded_chunk_arr.push(chunk_number);
        if(downloaded_chunk_arr.length < total_chunk_number){
                download_chunk();
        }
        else if(downloaded_chunk_arr.length == total_chunk_number){ // last chunk
            console.log('Received lastchunk');
            loader.setProgress(1);
            $('#result_file').html("Download completed. Waiting for Decryption...");
            $('#result_file').show();
        }
    }
    else if(cmd == 'saved_lastchunk'){
        // initialize chunk arr for decrypt
        decrypt_chunk_arr = [];
        for(i=1; i <= total_chunk_number; i++)
            decrypt_chunk_arr.push(i);
        decrypt_chunk();
    }
    else if(cmd == 'decrypt_nextchunk'){
        decrypt_chunk();
    }
    else if(cmd == 'decrypt_chunk_complete'){
        var chunk_number = e.data.chunk_number;
        decrypted_chunk_arr.push(chunk_number);
        if(chunk_number == 1) {
            console.log('append decrypted chunk: 1');
            append_decrypted_chunk(1);
        }
    }
    else if(cmd == 'append_decrypted_chunk_complete') {
        var chunk_number = e.data.chunk_number;
        if (chunk_number < total_chunk_number){
            var next_chunk = chunk_number + 1;
            console.log('append decrypted chunk: ' + next_chunk);
            append_decrypted_chunk(next_chunk, 100);
            progress = chunk_number * 1.00 / total_chunk_number;
            $('#result_file').html("Download completed. Waiting for Decryption(" + (progress * 100).toFixed(1) + "%)");
            $('#result_file').show();
        }
        else {
            var file_url = e.data.file_url;
            loader.setProgress(1);
            $('#result_file').attr('href', file_url);
            $('#result_file')[0].click();
            $('#result_file').html("Decryption completed! Click me if your file is not saved automaticaly");
        }
    }
    else if(cmd == 'err'){
        var msg = e.data.msg;
        alert(msg);
    }
});