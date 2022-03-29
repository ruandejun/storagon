importScripts('/static/assets/frontend/js/cryptojs/aes.js',
			  '/static/assets/frontend/js/cryptojs/mode-ctr-min.js',
			  '/static/assets/frontend/js/cryptojs/lib-typedarrays-min.js');


/*
wordArray: { words: [..], sigBytes: words.length * 4 }
*/

// assumes wordArray is Big-Endian (because it comes from CryptoJS which is all BE)
// From: https://gist.github.com/creationix/07856504cf4d5cede5f9#file-encode-js
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

self.requestFileSystemSync = self.webkitRequestFileSystemSync || self.requestFileSystemSync;

var Worker_helper = function(){

    this.initVariable = function(){
        key = null; //CryptoJS.enc.Hex.parse(e.data.key);
        //iv = CryptoJS.enc.Hex.parse('00000000000000000000000000000001');
        aesEncryptor=null;// = CryptoJS.algo.AES.createEncryptor(key, { 'iv': iv });
        aesDecryptor=null;
        reader = null;
        total_chunk = null;
        lastChunk = null;
        file_size = null;
        fs_type = null;
        fs_space = null;
        download_link = null;
        chunk_size = null;
        chunk_array_buffer = null;
        support_fs = null;
        start_down_time = null;
        received_size = 0;
        init_time = null;
        fs = null;
        decryptQueue = [];
        decrypted_array = null;
        raw_data_array = null;
        worker_track = null;
        tmp_chunk_arr = null;
        save_waiting_chunk = null;
    };

    this.encryptAES = function(rawArrayBuffer){
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
        aesEncryptor._mode._counter = modeCounter;

        var data = aesEncryptor.process(CryptoJS.lib.WordArray.create(encrypted_blob));
        //console.log(aesEncryptor._mode._counter);

        if(firstChunk && !lastChunk){
            encrypted_blob = new Blob([this.convertWordArrayToUint8Array(data)]);
            firstChunk=false;
        }else{
            if(lastChunk){
              console.log("LastChunk3");
              encrypted_blob = new Blob([this.convertWordArrayToUint8Array(data), this.convertWordArrayToUint8Array(aesEncryptor.finalize()) ]);
            }
            else encrypted_blob = new Blob([this.convertWordArrayToUint8Array(data, chunk_array_buffer)]);
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
    };

    this.convertWordArrayToUint8Array = function(wordArray,arrayBuffer) {
        var len = wordArray.words.length, offset = 0, word, i;

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
        return u8_array.buffer;
    };

    // concat 2 arraybuffer
    this.appendBuffer =  function( buffer1, buffer2 ) {
      var tmp = new Uint8Array( buffer1.byteLength + buffer2.byteLength );
      tmp.set( new Uint8Array( buffer1 ), 0 );
      tmp.set( new Uint8Array( buffer2 ), buffer1.byteLength );
      return tmp.buffer;
    };

    this.handleResponse = function(xhr, current_chunk_number, time_try){
        //console.log(xhr.readyState);
		if (xhr.readyState === 4){
			if (xhr.status === 206 || xhr.status === 200){//OK or partial responded
                received_size += xhr.response.byteLength;
                //typeof this.response;
                console.log('chunk:' + current_chunk_number + 'downloaded');


                if(support_fs){
                    var blob = new Blob([xhr.response]);
                    var waiting_chunk = {};
                    waiting_chunk["chunk_number"] = current_chunk_number;
                    waiting_chunk["data"] = blob;
                    save_waiting_chunk.push(waiting_chunk);
                    worker_track["wait_saving_chunk"]++;

                    if(worker_track["saving_chunk"] == 0)
                        this.saveBlobTemporary(3);
                }
                else{//not Chrome
                     raw_data_array.push(xhr.response);
                }
			}else{
				console.log("Failed to download chunk with error: "+xhr.statusText);
				time_try--;
				if(time_try > 0){
					//downloadNextChunkIfChunkNotAlreadyExist(); //dont need to check because its already checked
					this.download_chunk(current_chunk_number, time_try);
				}
                else{
                    self.postMessage({
						'cmd':'err',
                        'msg': 'Can\'t download the file dute to network error, please try again later'
					});
                }
			}
		}
    };

    this.updateProgressXHR = function(oEvent, current_chunk_number, init_time){
        if(current_chunk_number % 2 == 0){
            var duration = new Date() - init_time;
            //console.log('duration ' + duration);
            //console.log(received_size+oEvent.loaded);
            var speed = (received_size + oEvent.loaded) / duration;
            //console.log('spped: ' + speed);
            var progress = (received_size + oEvent.loaded ) / file_size;
            var timeLeft = (((file_size - received_size) / 1024) / speed).toFixed(0).toHHMMSS();
            var timestart = (duration / 1000).toString().toHHMMSS();
            self.postMessage({
                'cmd': 'download_progress',
                'speed': speed,
                'progress': progress,
                'time_left': timeLeft,
                'time_start': timestart
            });
        }
    };

    this.download_chunk = function(current_chunk_number, time_try){
        var fs = requestFileSystemSync(fs_type, fs_space);
        try {
              var fileEntry = fs.root.getFile(stored_file_name +'_part_'+current_chunk_number, {create: false});
              var current_chunk_size = fileEntry.getMetadata().size;
              console.log("File chunk exist with size " + current_chunk_size);
              // if chunk is not completed -> need download again
              if(current_chunk_size != chunk_size) {
                  fileEntry.remove();
                  this.download_chunk(current_chunk_number)
              }
              else{
                  // chunk downloaded, post notification
                  received_size += chunk_size;
                  self.postMessage({
                        'cmd':'dl_chunk_complete',
                        'chunk_number': current_chunk_number
                  });
              }

        } catch (e) {
             // Chunk not exist, download it
            if(e instanceof DOMException) {

                var from_byte = (current_chunk_number - 1) * chunk_size;
                console.log('Download chunk:' + current_chunk_number);

                var to_byte = from_byte + chunk_size - 1;
                var xhr = new XMLHttpRequest();
                xhr.onreadystatechange = function () {
                    worker_helper.handleResponse(xhr, current_chunk_number, time_try);
                };
                xhr.addEventListener("progress", function (oEvent) {
                    worker_helper.updateProgressXHR(oEvent, current_chunk_number, init_time);
                }, false);

                xhr.open("GET", file_download_link);
                if (received_size + 2 * chunk_size >= file_size) {
                    xhr.setRequestHeader('Range', 'bytes=' + (from_byte) + '-');
                } else {
                    xhr.setRequestHeader('Range', 'bytes=' + (from_byte) + '-' + (to_byte));
                }
                xhr.responseType = 'arraybuffer';
                xhr.send();
            }
            else{
                this.onError(e);
            }
        }
    };

    this.saveBlobTemporary = function(time_try){

        worker_track["saving_chunk"]++;
        var saving_chunk = save_waiting_chunk[0];
        try {
            var chunk_number = saving_chunk["chunk_number"];
            console.error("Number of saving chunk: " + worker_track["saving_chunk"]);
            worker_track["wait_saving_chunk"]--;
            if(worker_track["wait_saving_chunk"] == 0){
                self.postMessage({
                    'cmd':'dl_chunk_complete',
                    'chunk_number': chunk_number
                });
            }

            var blob = saving_chunk["data"];
            var fileEntry = fs.root.getFile(stored_file_name + '_part_' + chunk_number, {
                create: true,
                exclusive: true
            });
            fileEntry.createWriter().write(blob);

            save_waiting_chunk.splice(0, 1); // remove first item
            blob = null;


            tmp_chunk_arr.push(chunk_number);
            if (tmp_chunk_arr.length == total_chunk) {
                self.postMessage({
                    'cmd': 'saved_lastchunk'
                });
            }
            worker_track["saving_chunk"]--;

            if(worker_track["wait_saving_chunk"] > 0)
                this.saveBlobTemporarytime_try(3);
        } catch (e) {
            this.onError(e);
            if (e instanceof DOMException) {
                fileEntry.remove();
                time_try--;
                worker_track["wait_saving_chunk"]++;
                console.log('download chunk: ' + chunk_number + ' again');
                if (time_try > 0)
                    this.saveBlobTemporary(time_try);
                else console.error('can\'t save chunk: ' + chunk_number);
            }
        }


    };

    this.decrypt_chunk = function(current_chunk_number){
        var fs = requestFileSystemSync(fs_type, fs_space);
        try {
            var counter = 1 + chunk_size / 16 * (current_chunk_number - 1);
            if (current_chunk_number > 1)
                counter--; //fix bug decryping first chunk lack of 1 block
            modeCounter = [0, 0, 0, counter];

            if(current_chunk_number == 1){
                //actually init encryptor
                var hexCounter = counter.toString(16);
                var prefix='';
                for(var i=0;i<32-hexCounter.length;i++)prefix+='0';
                    hexCounter=prefix+hexCounter;

                iv = CryptoJS.enc.Hex.parse(hexCounter);
                aesDecryptor = CryptoJS.algo.AES.createDecryptor(key, {mode: CryptoJS.mode.CTR, 'iv': iv });// padding: CryptoJS.pad.NoPadding,
                //if(chunkNumber!=1)aesDecryptor.process(CryptoJS.lib.WordArray.create(e.data.response));//decrypt twice to fix bug lack of 1 block in first decrypted chunk
            }

            aesDecryptor._mode._counter = modeCounter;
            var data = null;
            if(support_fs) {
                var chunk_name = stored_file_name + '_part_' + current_chunk_number;
                var fileEntry = fs.root.getFile(chunk_name, {create: false, exclusive: true});
                // read and decrypt
                var reader = new FileReaderSync();
                data = reader.readAsArrayBuffer(fileEntry.file());
                //console.log(aesDecryptor._mode._counter);
            }
            else // not chrome
                data = raw_data_array.shift();

            data = aesDecryptor.process(CryptoJS.lib.WordArray.create(data));

            if (current_chunk_number == 1 && current_chunk_number < total_chunk) {
                data = new Blob([this.convertWordArrayToUint8Array(data)]);
            } else {
                if (current_chunk_number == total_chunk) {
                    data = new Blob([this.convertWordArrayToUint8Array(data), this.convertWordArrayToUint8Array(aesDecryptor.finalize())]);
                }
                else data = new Blob([this.convertWordArrayToUint8Array(data, chunk_array_buffer)]);//
            }

            decrypted_array[current_chunk_number] = data;
            data = null;
            self.postMessage({
                'cmd':'decrypt_chunk_complete',
                'chunk_number': current_chunk_number
            });

        } catch (e) {
          this.onError(e);
        }
    };

    this.appendFile = function(current_chunk_number, time_try){
        var fs = requestFileSystemSync(fs_type, fs_space);
        try {
            var data;
            if (current_chunk_number in decrypted_array) {
                data = decrypted_array[current_chunk_number];
            }
            else return;
            self.postMessage({
                'cmd': 'decrypt_nextchunk'
            });
            // write to file
            var fileEntry;
            var writer;
            var file_url = null;
            if(current_chunk_number > 1){
                fileEntry = fs.root.getFile(stored_file_name, {create: false});
                writer = fileEntry.createWriter();
                writer.seek(writer.length);
            }
            else if(current_chunk_number == 1) {
                fileEntry = fs.root.getFile(stored_file_name, {create: true});
                writer = fileEntry.createWriter();
            }
            console.log('File state:' + fileEntry.readyState);
            writer.write(data);
            delete decrypted_array[current_chunk_number];

            if(current_chunk_number == total_chunk)
                file_url = fileEntry.toURL();
            self.postMessage({
                'cmd': 'append_decrypted_chunk_complete',
                'chunk_number': current_chunk_number,
                'file_url': file_url
            });
        } catch (e) {
            this.onError(e);
            if(e instanceof DOMException) {
                if(time_try > 0) {
                    console.log('attemp to write again');
                    time_try--;
                    setTimeout(function () {
                        console.log('Append again');
                        this.append_decrypted_chunk(current_chunk_number, time_try)
                    }, 500);
                }
            }

        }
    };

    this.onError = function(e){
        console.log(e);
    }
};

var worker_helper = new Worker_helper();
worker_helper.initVariable();

self.addEventListener('message', function(e) {


    var cmd= e.data.cmd;
	console.log("worker: cmd="+cmd);
    if(cmd == 'decrypt_chunk' || cmd == 'append_decrypted_chunk'){
        var current_chunk_number = e.data.chunkNumber;
        console.log('chunk: ' + current_chunk_number);
    }
	if(cmd=='init_decrypt_aes') {
		file_size = e.data.file_size;
		chunk_size = e.data.chunk_size;
        total_chunk = e.data.total_chunk;
        support_fs = e.data.support_fs;
        raw_data_array = [];
        tmp_chunk_arr = [];
        decrypted_array = {};
		file_download_link = e.data.file_download_link;
		stored_file_name = e.data.stored_file_name;
        fs_type = e.data.fs_type;
        fs_space = e.data.fs_space;
        init_time = new Date();
        fs = requestFileSystemSync(fs_type, fs_space);
		console.log("Init AES Decryptor with key="+e.data.key);
		key = CryptoJS.enc.Hex.parse(e.data.key);
		//aesDecryptor = CryptoJS.algo.AES.createDecryptor(key, {mode: CryptoJS.mode.CTR, 'iv': iv });// padding: CryptoJS.pad.NoPadding,
		aesDecryptor=null;
		chunk_array_buffer = new Uint8Array(chunk_size);
        save_waiting_chunk = [];
        worker_track = {saving_chunk:0, wait_saving_chunk:0};
		//console.log('chunk_array_buffer='+chunk_array_buffer.length);
	}

	else if(cmd=='decrypt_aes'){

		chunkNumber = e.data.chunkNumber;
		lastChunk = e.data.lastChunk;

        decryptQueue.push(chunkNumber);

        worker_helper.blockingDecrypt(e);

	}

	else if(cmd=='init_encrypt_aes') {
		file_size = e.data.file_size;
		chunk_size = e.data.chunk_size;
		console.log("Init AES Encryptor with key="+e.data.key);
		key = CryptoJS.enc.Hex.parse(e.data.key);
		aesEncryptor=null;
		chunk_array_buffer = new Uint8Array(chunk_size );

	}

    else if(cmd=='encrypt_aes') {

		//console.log('encrypting aes of size:'+blob.size);
		chunkNumber = e.data.chunkNumber;
		lastChunk = e.data.lastChunk;
		reader = new FileReaderSync();

		worker_helper.encryptAES(reader.readAsArrayBuffer(e.data.blob));
		reader=null;
    }

    else if(cmd == 'download_chunk'){

        var current_chunk_number = e.data.chunkNumber;
        worker_helper.download_chunk(current_chunk_number, 3);
    }

    else if(cmd == 'decrypt_chunk'){
        var current_chunk_number = e.data.chunkNumber;
        console.log('chunk: ' + current_chunk_number);
        worker_helper.decrypt_chunk(current_chunk_number);
    }

    else if(cmd == 'append_decrypted_chunk'){
        var current_chunk_number = e.data.chunkNumber;
        worker_helper.appendFile(current_chunk_number, 3);
    }
}, false);