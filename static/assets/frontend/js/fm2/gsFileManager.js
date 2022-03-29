/**
 * Free Web File Manager is free software released under MIT License.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
 * TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 * CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 *
 * George Sarafov
 * http://freewebfilemanager.com
 */

/** 
 * 
 * @param {integer} type
 * @param {string} name
 * @param {string} path
 * @param {integer} size
 * @param {integer} id
 * @param {string} exta
 * @param {datetime} uploadDate
 * @param {integer} totalDownload
 * @param {integer} todayDownload
 * @param {datetime} lastDownload
 * @returns {gsItem}
 */
var gsItem = function (type, name, path, size, id, exta, uploadDate, totalDownload, todayDownload, lastDownload, fileMode) {
  this.path = path;
  this.type = type; //1=file, 2= folder
  this.name = name; //file_name
  this.size = size; //file_size
  this.fileMode = fileMode; // file_mode
  this.id = id;
  this.exta = exta.toLowerCase();
  this.uploadDate = uploadDate;
  this.totalDownload = totalDownload;
  this.todayDownload = todayDownload;
  this.lastDownload = lastDownload;

  this.getSize = function () {
    if (this.size < 1048576) {
      return Math.ceil(this.size / 1024) + ' KB';
    } else {
      return Math.ceil(this.size / 1048576) + ' MB';
    }
  };

  this.getExt = function () {
    return this.exta;
  };

  this.getLastMod = function () {
    return this.uploadDate;
  };
  
  this.getTotalDownload = function () {
    return this.totalDownload;
  };
  
  this.getTodayDownload = function () {
    return this.todayDownload;
  };
  
  this.getLastDownload = function () {
    return this.lastDownload;
  };

  this.isPicture = function () {
    return typeof (gs_ext_pictures[this.exta]) !== 'undefined';
  };

  this.isEditable = function () {
    return typeof (gs_ext_editables[this.exta]) !== 'undefined';
  };

  this.isArchive = function () {
    return typeof (gs_ext_arhives[this.exta]) !== 'undefined';
  };

  this.getType = function () {
    type = 'unknown';
    if (this.isPicture()) {
      type = 'picture';
    } else if (this.isEditable()) {
      type = 'editable';
    } else if (this.isArchive()) {
      type = 'archive';
    }
    return type;
  };
};

function updateCoords(c) {
  $('#gs_jcrop_x').val(c.x);
  $('#gs_jcrop_y').val(c.y);
  $('#gs_jcrop_w').val(c.w);
  $('#gs_jcrop_h').val(c.h);
}

function gs_get_cur_item(id) {
  result = null;
  if (typeof (gs_cur_items[id]) !== 'undefined') {
    result = gs_cur_items[id];
  }
  return result;
}

function gsGetSelectedItemsPath() {
  var arr = new Array();
  for (var x in gs_clipboard) {
    arr.push(gs_clipboard[x].path);
  }
  if (arr.length > 0) {
    return arr.join(',,,');
  }
  return null;
}

function gsGetSelectedItems() {
  var arr = new Array();
  $("#gs_content_table tr.rowSelected").each(function () {
    var id = $(this).find("td:first").attr('rel');
    if (typeof (gs_cur_items[id]) !== 'undefined') {
      arr.push(gs_cur_items[id].name);
    }
  });
  if (arr.length > 0) {
    return arr.join(',,,');
  }
  return null;
}

function gsGetSelectedItemsFileName() {
  var arr = new Array();
  if($("#gs_content_table tr.rowSelected").length){
    $("#gs_content_table tr.rowSelected").each(function () {
      var id = $(this).find("td:first").attr('rel');
      if (typeof (gs_cur_items[id]) !== 'undefined') {
        if (gs_cur_items[id].type === "1")
          arr.push(gs_cur_items[id].name);
      }
    });
  }
  else{
    $("tbody#search_result tr.rowSelected").each(function () {
      var name = $(this).find("td:first").text();
      arr.push(name);
    });
  }
  return arr;
}

function gsGetSelectedItemsFileID() {
  var arr = new Array();
  if($("#gs_content_table tr.rowSelected").length){
    $("#gs_content_table tr.rowSelected").each(function () {
      var id = $(this).find("td:first").attr('rel');
      if (typeof (gs_cur_items[id]) !== 'undefined') {
        if (gs_cur_items[id].type === "1")
          arr.push(gs_cur_items[id].id);
      }
    });
  }
  else{
    $("tbody#search_result tr.rowSelected").each(function () {
      var id = $(this).find("td:first").attr('rel');
      arr.push(id);
    });
  }
  return arr;
}

function gsGetSelectedItemsFolderID() {
  var arr = new Array();
  $("#gs_content_table tr.rowSelected").each(function () {
    var id = $(this).find("td:first").attr('rel');
    if (typeof (gs_cur_items[id]) !== 'undefined') {
      if (gs_cur_items[id].type === "2")
        arr.push(gs_cur_items[id].id);
    }
  });
  return arr;
}


function gsCheckResponce(data) {
  if (typeof (data) === 'undefined') {
    return;
  }
  if (data.substr(0, 9) === '{result: ') {
    eval('var my_responce = ' + data + ';');
    if (typeof (my_responce.result !== 'undefined')) {
      if (my_responce.result === '1') {
        //alert('OK');
      } else if (typeof (my_responce.gserror) !== 'undefined') {
        alert(my_responce.gserror);
      } else {
        alert('Error');
      }
    }
    delete my_responce;
  }

}

function gs_storeSelectedItems() {
  gs_clipboard = new Array();
  $("#gs_content_table tr.rowSelected").each(function () {
    var id = $(this).find("td:first").attr('rel');
    if (typeof (gs_cur_items[id]) !== 'undefined') {
      gs_clipboard.push(gs_cur_items[id]);
    } else {
      alert('Uknown item selected');
    }
  });
}

function gs_showClipboardContent() {
  var diva = $('#gsclipboardContent');
  var divaHtml = '';
  for (var xx in gs_clipboard) {
    var clasa = 'file';
    if (gs_clipboard[xx].getExt() === 'dir') {
      clasa = 'directory';
    }
    divaHtml += '<div class="' + clasa + '">&nbsp;&nbsp;&nbsp;' + gs_clipboard[xx].path + '<div>';
  }
  diva.html(divaHtml);
  diva.dialog({title: 'Clipboard', modal: true, buttons: {
      "Clear": function () {
        gs_clipboard = new Array();
        $('#gsclipboardContent').html('');
        $("#gsClipBoard").html('0 items');
        $(this).dialog('close');
      }
    }
  });
  return false;
}

function gs_makeUrl(root, params) {
  if (root.indexOf('?') !== -1) {
    return root + '&' + params;
  } else {
    return root + '?' + params;
  }
}

var gs_filemanager_languages = new Array();
gs_filemanager_languages['en'] = new Array();
gs_filemanager_languages['en'][1] = 'Current Dir';
gs_filemanager_languages['en'][2] = 'Clipboard';
gs_filemanager_languages['en'][3] = 'Upload';
gs_filemanager_languages['en'][4] = 'Root Folder';//New File
gs_filemanager_languages['en'][5] = 'New Directory';
gs_filemanager_languages['en'][6] = 'Paste';
gs_filemanager_languages['en'][7] = 'Name';
gs_filemanager_languages['en'][8] = 'Last Download Date';
gs_filemanager_languages['en'][9] = 'Size';
gs_filemanager_languages['en'][10] = 'Upload Date';
gs_filemanager_languages['en'][50] = 'Total Download';
gs_filemanager_languages['en'][51] = 'Today Download';
gs_filemanager_languages['en'][11] = 'Open with';
gs_filemanager_languages['en'][12] = 'Notepad';
gs_filemanager_languages['en'][13] = 'ImageViewer';
gs_filemanager_languages['en'][14] = 'Copy';
gs_filemanager_languages['en'][15] = 'Cut';
gs_filemanager_languages['en'][16] = 'Rename';
gs_filemanager_languages['en'][17] = 'Copy AS';
gs_filemanager_languages['en'][18] = 'Get Download Links'; //Download
gs_filemanager_languages['en'][19] = 'Delete';
gs_filemanager_languages['en'][20] = 'Open';
gs_filemanager_languages['en'][21] = 'CKeditor';
gs_filemanager_languages['en'][22] = 'JCrop';
gs_filemanager_languages['en'][23] = 'Select all';
gs_filemanager_languages['en'][24] = 'Deselect all';
gs_filemanager_languages['en'][25] = 'Invert selection';
gs_filemanager_languages['en'][26] = 'Width';
gs_filemanager_languages['en'][27] = 'Height';
gs_filemanager_languages['en'][28] = 'Cancel';
gs_filemanager_languages['en'][29] = 'Upload File';
gs_filemanager_languages['en'][30] = 'Items';
gs_filemanager_languages['en'][31] = 'Save';
gs_filemanager_languages['en'][32] = 'Resize';
gs_filemanager_languages['en'][33] = 'Crop';
gs_filemanager_languages['en'][34] = 'As name';
gs_filemanager_languages['en'][35] = 'New name';
gs_filemanager_languages['en'][36] = 'File name';
gs_filemanager_languages['en'][37] = 'Directory name';
gs_filemanager_languages['en'][38] = 'Are you sure that you want to deleted selected items?';
gs_filemanager_languages['en'][39] = 'Zip directory';
gs_filemanager_languages['en'][40] = 'Zip file';
gs_filemanager_languages['en'][41] = 'Zip archive name';
gs_filemanager_languages['en'][42] = 'UnZip';
gs_filemanager_languages['en'][43] = 'UnZip Name';
gs_filemanager_languages['en'][44] = 'Lock sizes';
gs_filemanager_languages['en'][45] = 'Add upload field';
gs_filemanager_languages['en'][46] = 'Remove';
gs_filemanager_languages['en'][47] = 'Invalid name, name can not contains \ / . * ? " < > |';
gs_filemanager_languages['en'][48] = 'Trash';
gs_filemanager_languages['en'][49] = 'Are you sure that you want to move selected items to trash?';
gs_filemanager_languages['en'][52] = 'Set / Unset Premium File';
gs_filemanager_languages['en'][53] = 'Are you sure that you want to set / unset premium for selected files?';

function gs_getTranslation(lg, code) {
  result = null;
  if (typeof (gs_filemanager_languages[lg]) !== 'undefined') {
    if (typeof (gs_filemanager_languages[lg][code]) !== 'undefined') {
      result = gs_filemanager_languages[lg][code];
    }
  }
  return result;
}

if(typeof (resumableObjList) === 'undefined'){
  var resumableObjList = {};
}

var gs_cur_items = new Array();

var gs_clipboard = new Array();

var gs_ext_editables = new Array();
gs_ext_editables['txt'] = '1';
gs_ext_editables['php'] = '1';
gs_ext_editables['doc'] = '1';
gs_ext_editables['js'] = '1';
gs_ext_editables['html'] = '1';
gs_ext_editables['htm'] = '1';
gs_ext_editables['rtf'] = '1';
gs_ext_editables['css'] = '1';
gs_ext_editables['java'] = '1';
gs_ext_editables['asp'] = '1';
gs_ext_editables['xml'] = '1';
gs_ext_editables['xls'] = '1';
gs_ext_editables['sql'] = '1';
gs_ext_editables['log'] = '1';

var gs_ext_pictures = new Array();
gs_ext_pictures['png'] = '1';
gs_ext_pictures['jpg'] = '1';
gs_ext_pictures['jpeg'] = '1';
gs_ext_pictures['gif'] = '1';
gs_ext_pictures['pdf'] = '1';
gs_ext_pictures['ico'] = '1';

var gs_ext_arhives = new Array();
gs_ext_arhives['zip'] = '1';

var gs_forbitten_ext_mapping = new Array();
gs_forbitten_ext_mapping['editable'] = '15,16,17,23';
gs_forbitten_ext_mapping['picture'] = '12,18,23';
gs_forbitten_ext_mapping['unknown'] = '12,15,16,17,18,23';
gs_forbitten_ext_mapping['archive'] = '12,15,16,17,18,19';

var recycleBinID = '';

// Get screen width and height
var w=window,d=document,e=d.documentElement,g=d.getElementsByTagName('body')[0],deviceWidth=w.innerWidth||e.clientWidth||g.clientWidth,deviceHeight=w.innerHeight||e.clientHeight||g.clientHeight;

var totalRecords, global_folder_id, global_parent_folder_path;

if ($)
  (function ($) {

    $.extend($.fn, {
      gsFileManager: function (o) {

        if (!o)
          var o = {};
        if (o.root === undefined)
          o.root = '/';
        if (o.language === undefined)
          o.language = 'en';
        if (o.script === undefined)
          o.script = 'jqueryFileTree.php';
        if (o.expandSpeed === undefined)
          o.expandSpeed = 500;
        if (o.collapseSpeed === undefined)
          o.collapseSpeed = 500;
        if (o.expandEasing === undefined)
          o.expandEasing = null;
        if (o.collapseEasing === undefined)
          o.collapseEasing = null;
        if (o.loadMessage === undefined)
          o.loadMessage = 'Loading...';
        
        function generateHTML() {
          var navBarHtml = '<nav class=\'top-bar\' data-topbar role=\'navigation\'>'
                  + '<div id=\'navbar\' class=\'top-bar-section\'>'
                  + '<ul class=\'navbar-form left\'>'
                  + '<ul class=\'button-group radius\'>'
                  + '<li><a href=\'javascript:void(0)\' class=\'button primary\' data-reveal-id=\'newfolder\' id=\'gs_newdirbutton\'><i class=\'fi fi-folder-add size-14\'></i> <span>Create folder</span></a></li>' 
                  + '<li><a href=\'javascript:void(0)\' class=\'button primary\' data-reveal-id=\'uploadfile\' id=\'gs_uploadbutton\'><i class=\'fa fa-upload fa-2\'></i> <span>Upload file</span></a></li>'
                  + '<li><a href=\'javascript:void(0)\' class=\'button success\' id=\'gs_pastebutton\'><i class=\'fa fa-paste fa-2\'></i><span>Paste</span></a></li>'
                  + '<li><a href=\'javascript:void(0)\' class=\'button success\' id=\'gs_selectallbutton\'><i class=\'fa fa-clipboard fa-2\'></i> <span>Select all</span></a></li>'
                  + '<li><a href=\'javascript:void(0)\' class=\'button success\' id=\'gs_deselectbutton\'><i class=\'fa fa-eraser fa-2\'></i> <span>Deselect all</span></a></li>'
                  + '<li><a href=\'javascript:void(0)\' class=\'button success\' id=\'gs_invertselectbutton\'><i class=\'fa fa-undo fa-2\'></i> <span>Invert selection</span></a></li>'
                  + '</ul></ul>'
//                  + '<li class=\'has-form\'>'
//                  + '<a href=\'javascript:void(0)\' class=\'button primary\' data-reveal-id=\'newfolder\' id=\'gs_newdirbutton\'><i class=\'fa fa-plus fa-2\'></i><span>Create folder</span></a>'
//                  + '</li>'
//                  + '<li class=\'has-form\'>'
//                  + '<a href=\'javascript:void(0)\' class=\'button primary\' data-reveal-id=\'uploadfile\' id=\'gs_uploadbutton\'><i class=\'fa fa-upload fa-2\'></i><span>Upload file</span></a>'
//                  + '</li>'
//                  + '<li class=\'has-form\'>'
//                  
//                  + '</li>'
//                  + '<li class=\'has-form\'>'
//                  + '<a href=\'javascript:void(0)\' class=\'button success\' id=\'gs_selectallbutton\'><i class=\'fa fa-clipboard fa-2\'></i><span>Select all</span></a>'
//                  + '</li>'
//                  + '<li class=\'has-form\'>'
//                  + '<a href=\'javascript:void(0)\' class=\'button success\' id=\'gs_deselectbutton\'><i class=\'fa fa-eraser fa-2\'></i><span>Deselect all</span></a>'
//                  + '</li>'
//                  + '<li class=\'has-form\'>'
//                  + '<a href=\'javascript:void(0)\' class=\'button success\' id=\'gs_invertselectbutton\'><i class=\'fa fa-undo fa-2\'></i><span>Invert selection</span></a>'
//                  + '</li>'
//                  + '<li class=\'has-form\'>'
//                  + '<input type=\'text\' class=\'form-control\' placeholder=\'Search files and folders...\'>'
//                  + '</li>'
                  + '<ul class=\'navbar-form left\'>'
                  + '<li class="has-form"><div class="row collapse" style="padding-right:3px;"><div class="small-12 large-12 columns"><select id=\'itemsPerPage\'><option value=\'50\' selected>50 Items</option><option value=\'100\'>100 Items</option><option value=\'0\'>Show all</option></select></div></div></li>'
                  + '<li class="has-form"><div class="row collapse"><div class="small-9 large-9 columns"><input id="filename_input" placeholder="Search files..." type="text"></div><div class="small-3 large-3 columns"><a class="alert button expand" id="search_file" href="javascript:void(0)">Search</a></div></div></li>'
                  + '</ul></ul>'
                  + '</div>'
                  + '</nav>';
          var breadCrumbHtml = '<li>'
                  + '<a href=\"javascript:void()\"'
                  + '<i class=\"fi fi-folder-add size-12\"></i>'
                  + '</a>'
                  + '</li>';          
          var wrapperHtml = '<div class=\'row fm-container\'><div id=\'gs_dir_list\' class=\'small-2 columns sidebar-fm file-tree\' onClick="$(this).doGSAction({action: 21})"></div>';
          wrapperHtml += '<div class=\'small-10 columns\' onClick="$(this).doGSAction({action: 21})">'
                       + navBarHtml
                       + '<div id=\'topbar\'><ul class=\"breadcrumbs mb0\">';
          wrapperHtml += breadCrumbHtml;
          wrapperHtml += '<span id=\'gsClipBoard\' rel=\'\'></span></ul>';
          wrapperHtml += '<span id=\'curDir\'></span></div>';
          wrapperHtml += '<div id=\'gs_dir_content\' class=\'gs_dir_content_files main\'></div>';
          wrapperHtml += '</div>';
          var contexMenus = '<ul id="gsFileMenu" class="f-dropdown drop-right">';
          contexMenus += '<li class="cut"><a href="#Cut" rel="8"><i class="fi fi-x-circle size-14"></i> ' + gs_getTranslation(o.language, 15) + '</a></li>';
          contexMenus += '<li class="rename"><a href="#Rename" rel="10"><i class="fi fi-page-edit size-14"></i> ' + gs_getTranslation(o.language, 16) + '</a></li>';
          contexMenus += '<li class="set_premium_file"><a href="#SetPremium" rel="28"><i class="fi fi-page-edit size-14"></i> ' + gs_getTranslation(o.language, 52) + '</a></li>';
          //contexMenus += '<li class="rename"><a href="#Copy As" rel="13">' + gs_getTranslation(o.language, 17)+ '</a></li>';
          //contexMenus += '<li class="zip"><a href="#zip" rel="19">' + gs_getTranslation(o.language, 40)+ '</a></li>';
          //contexMenus += '<li class="zip"><a href="#zip" rel="23">' + gs_getTranslation(o.language, 42)+ '</a></li>';
          contexMenus += '<li class="download separator"><a href="#Download" rel="11"><i class="fi fi-download size-14"></i> ' + gs_getTranslation(o.language, 18) + '</a></li>';
          contexMenus += '<li class="delete"><a href="#Trash" rel="6"><i class="fi fi-trash size-14"></i> ' + gs_getTranslation(o.language, 48) + '</a></li>';
          contexMenus += '<li class="delete"><a href="#Delete" rel="4"><i class="fi fi-minus size-14"></i> ' + gs_getTranslation(o.language, 19) + '</a></li>';
          contexMenus += '</ul>';

          contexMenus += '<ul id="gsDirMenu" class="f-dropdown drop-right" data-dropdown-content aria-hidden="true" tabindex="-1">';
          contexMenus += '<li class="directorymenu"><a href="#Open" rel="5"><i class="fi fi-folder-add size-14"></i> ' + gs_getTranslation(o.language, 20) + '</a></li>';
          //contexMenus += '<li class="copy separator"><a href="#Copy" rel="7">' + gs_getTranslation(o.language, 14)+ '</a></li>';
          contexMenus += '<li class="cut"><a href="#Cut" rel="8"><i class="fi fi-x-circle size-14"></i> ' + gs_getTranslation(o.language, 15) + '</a></li>';
          contexMenus += '<li class="rename"><a href="#Rename" rel="10"><i class="fi fi-page-edit size-14"></i> ' + gs_getTranslation(o.language, 16) + '</a></li>';
          //contexMenus += '<li class="zip"><a href="#zip" rel="19">' + gs_getTranslation(o.language, 39)+ '</a></li>';
          //contexMenus += '<li class="zip"><a href="#zip" rel="23">' + gs_getTranslation(o.language, 42)+ '</a></li>';
          contexMenus += '<li class="delete"><a href="#Trash" rel="6"><i class="fi fi-trash size-14"></i> ' + gs_getTranslation(o.language, 48) + '</a></li>';
          contexMenus += '<li class="delete"><a href="#Delete" rel="4"><i class="fi fi-minus size-14"></i> ' + gs_getTranslation(o.language, 19) + '</a></li>';
          contexMenus += '</ul>';

          contexMenus += '<ul id="gsContentMenu" class="f-dropdown drop-right">';
          contexMenus += '<li class="paste separator"><a href="#Paste" rel="9"><i class="fi fi-folder size-14"></i> ' + gs_getTranslation(o.language, 6) + '</a></li>';
          //contexMenus += '<li class="newfile separator"><a href="#New File" rel="2">' + gs_getTranslation(o.language, 4)+ '</a></li>';
          contexMenus += '<li class="newdir"><a href="#New Directory" rel="3"><i class="fi fi-folder-add size-14"></i> ' + gs_getTranslation(o.language, 5) + '</a></li>';
          contexMenus += '<li class="uploadfolder separator"><a href="#Upload" rel="29"><i class="fi fi-upload size-14"></i> ' + gs_getTranslation(o.language, 3) + '</a></li>';
          contexMenus += '<li class="selection separator"><a href="#Select All" rel="20"><i class="fi fi-checkbox size-14"></i> ' + gs_getTranslation(o.language, 23) + '</a></li>';
          contexMenus += '<li class="selection"><a href="#Deselect all" rel="21"><i class="fi fi-refresh size-14"></i> ' + gs_getTranslation(o.language, 24) + '</a></li>';
          contexMenus += '<li class="selection"><a href="#Invert selection" rel="22"><i class="fi fi-rewind-ten size-14"></i> ' + gs_getTranslation(o.language, 25) + '</a></li>';
          contexMenus += '</ul>';

          wrapperHtml += contexMenus;
          return wrapperHtml;
        }

        $(this).html(generateHTML());

        $('#gs_dir_content').contextMenu({
          menu: 'gsContentMenu',
          addSelectedClass: false
        }, function (action, el, pos) {
          $(el).doGSAction({action: parseInt(action), script: o.script, type: 'context', lg: o.language});
        });                                               
        
        $('#gs_uploadbutton').click(function (e) {
          e.stopPropagation();          
          $("#gs_uploadAddField").unbind("click");
          $('#upload-fields').html('');
          addUploadField();
          $("#gs_uploadAddField").bind("click", function(e){
            e.stopPropagation();
            e.preventDefault();
            addUploadField();
          });
          $(this).doGSAction({action: 14, script: o.script, type: 'file', lg: o.language});
        });

        $('#gs_newdirbutton').click(function (e) {
          e.stopPropagation();
          $(this).doGSAction({action: 3, script: o.script, type: 'dir', lg: o.language});
        });

        $('#gs_pastebutton').click(function (e) {
          e.stopPropagation();
          $(this).doGSAction({script: o.script, action: 9, lg: o.language});
        });

        $('#gs_selectallbutton').click(function (e) {
          e.stopPropagation();
          $(this).doGSAction({action: 20, script: o.script, type: 'context', lg: o.language});
        });

        $('#gs_deselectbutton').click(function (e) {
          e.stopPropagation();
          $(this).doGSAction({action: 21, script: o.script, type: 'context', lg: o.language});
        });

        $('#gs_invertselectbutton').click(function (e) {
          e.stopPropagation();
          return $(this).doGSAction({action: 22, script: o.script, type: 'context', lg: o.language});
        });        
        
        $('a#search_file').on('click', function (e){
          e.stopPropagation();
          var token = $('input#filename_input').val();          
          showSearchResult(token);
        });
        
        $('input#filename_input').on('keypress', function(e){
          e.stopPropagation();
          if(e.keyCode === 13){            
            showSearchResult($(this).val());
          }
        });
        
        $('#itemsPerPage').on('change', function(){
          $('#' + $("#curDir").attr('rel')).trigger('click');
        });

        function showSearchResult(token_value) {  
          $('tbody#search_result').empty();
          $('input#filename_input, input#inside_filename_input').val(token_value);
          
          if ($('input#folder_search_include').is(':checked')) {
            getFolderByName(token_value, function (data) {
              for (var i in data) {
                $('tbody#search_result').append('<tr><td class=\'directory directory_info gsItem\' rel=\'' + data[i].id + '\'>' + data[i].name + '</td><td></td><td class=\'trigger_click\'>' + data[i].created_date.substring(0, 10) + '<li class=\'collapsed\' style=\'display:none;\'><a href=\'#/fm2\' rel=\'/' + data[i].name + '#' + data[i].id + '/\' id=\'' + data[i].id + '\'><i class="fi-trash size-18"></i>' + data[i].name + '</a></li></td></tr>');
              }
              setHandlersForSearchResult(1);
            });
          }
          getFileByName(token_value, function (data) {            
            for (var i in data) {
              $('tbody#search_result').append('<tr><td class=\'file gsItem directory_info\' rel=\'' + data[i].id + '\'>' + data[i].file_name + '</td><td>' + filesize(data[i].file_size) + '</td><td>' + data[i].created_date.substring(0, 10) + '</td></tr>');
            }
            if (!$('#modal-search').hasClass('active')) {
              $('#modal-search').foundation('reveal', 'open');
              $('#modal-search').addClass('active');
            }
            setHandlersForSearchResult(2);
          });
        }
        
        function setHandlersForSearchResult(type){
          $('#gs_getlinkfromsearch, a#inside_search_file, #gs_selectallfromsearch').unbind('click');
          $('input#inside_filename_input').unbind('keypress');         
          $('a#inside_search_file').bind('click', function (e){
            e.stopPropagation();
            var token = $('input#inside_filename_input').val();          
            showSearchResult(token);
          });
          $('input#inside_filename_input').bind('keypress', function(e){
            e.stopPropagation();
            if(e.keyCode === 13){            
              showSearchResult($(this).val());
            }
          });
          
          $('#gs_getlinkfromsearch').css({"display" : "none"});
          $('#gs_getlinkfromsearch').removeClass("active");
          
          if(type === 2) {            
            $('tbody#search_result td.gsItem.file').unbind('click');
            $('tbody#search_result td.gsItem.file').bind('click', function (e) {
              var cur_element = $(this);
              var rel = $(this).attr('rel');
              if (rel !== 'up') {
                if (cur_element.parent().hasClass('rowSelected')) {
                  cur_element.parent().removeClass('rowSelected');
                  if(!$('tbody#search_result td.gsItem.file').closest('tr.rowSelected').length) {
                    $('#gs_getlinkfromsearch').css({"display" : "none"});
                    $('#gs_getlinkfromsearch').removeClass("active");
                  }
                } else {
                  cur_element.parent().addClass('rowSelected');
                  if (!$('#gs_getlinkfromsearch').hasClass('active')) {
                    $('#gs_getlinkfromsearch').addClass('active');
                    $('#gs_getlinkfromsearch').fadeIn(200);
                  }
                  if ((!e.ctrlKey && !e.metaKey) || (e.ctrlKey && e.metaKey)) {
                    $("tbody#search_result tr.rowSelected").each(function () {
                      if ($(this).find('td.gsItem').attr('rel') !== rel) {
                        $(this).removeClass('rowSelected');
                      }
                    });
                  }
                }
              }
            });
            $('#gs_getlinkfromsearch').bind('click', function(e){
              e.stopPropagation();
              $('#modal-search').foundation('reveal', 'close');
              $('#download').foundation('reveal', 'open');
              $(this).doGSAction({action: 11, script: o.script, type: 'context', lg: o.language});
            });
            $('#gs_selectallfromsearch').bind('click', function(e){
              $("tbody#search_result tr").each(function () {               
                $(this).addClass('rowSelected');                
              });
              $('#gs_getlinkfromsearch').addClass('active');
              $('#gs_getlinkfromsearch').fadeIn(200);
            });
            $('#gs_deselectallfromsearch').bind('click', function(e){
              $("tbody#search_result tr").each(function () {               
                if($(this).hasClass('rowSelected')){
                  $(this).removeClass('rowSelected');
                }                
              });
              $('#gs_getlinkfromsearch').css({"display" : "none"});
              $('#gs_getlinkfromsearch').removeClass("active");
            });
          }
          else {
            $('tbody#search_result td.directory.directory_info').unbind('dblclick');                              
            $('tbody#search_result td.directory.directory_info').bind('dblclick', function(e){
              e.stopPropagation();
              $('#modal-search').foundation('reveal', 'close');
              $('tbody#search_result').empty();
              if($(this).attr("rel") === 'up'){
                $('#'+$('#curDir').attr('rel')).parent().parent().parent().children('a').trigger('click'); 
                return false;
              }
              else {      
                showTree($(this).siblings('.trigger_click').find('li'), $(this).siblings('.trigger_click').find('li a').get(0));
                return false;
              }              
            });
          }                    
          $(document).on('click', 'button.close-modal', function(e) {
            e.stopPropagation();
            $(this).closest('div.reveal-modal').foundation('reveal', 'close');
          });
          $(document).on('closed.fndtn.reveal', '#modal-search', function (e) {
            e.stopPropagation();
            $(this).removeClass('active');
          });
        }
        
        function addUploadField(){
          var uploadsFieldsHolder = $('#upload-fields');
          var uploadsFieldsLength = $('#upload-fields fieldset').length;            
          randomID = Math.random().toString(36).substring(2);
          uploadsFieldsHolder.append('<fieldset><a href="javascript:void(0)" onclick="$(this).parent().remove();" class=\'gs_dir_content_button\'><i class="fi fi-x-circle size-21"></i></a><legend>File Upload</legend><label>Choose file <input type="file" id="input_' + randomID + '" name="filename"/> </label></fieldset>');
          folder_id = $('#curDir').attr('rel');
          if (folder_id === 'rootLink'){
            folder_id = '';
          }            
          var resumableObj = applyResumableToInput('input_' + randomID, 'gsuploadfiles_button', 'progress_' + randomID, 'upspeed_' + randomID, folder_id, randomID, function (progress_id) {             
            $('span#'+progress_id).closest('td').addClass('success');
            $('span#'+progress_id).closest('tr').addClass('deactivate');
            $('span#'+progress_id).closest('td').html('Completed');              
            $('#' + $("#curDir").attr('rel')).trigger('click');
          }, function (file_name, errorMessage) {
            alert("Upload failed: " + file_name);
          });
          resumableObjList[randomID] = resumableObj;
        }                         

        function manageGsMenu(srcElement, menu) {
          if (srcElement.attr('rel') === 'up') {
            return false;
          }
          gs_item = gs_cur_items[srcElement.attr('rel')];
          type = gs_item.getType();
          if (typeof (gs_forbitten_ext_mapping[type]) !== 'undefined') {
            menu.disableContextMenuItems(gs_forbitten_ext_mapping[type]);
          }
          return true;
        }

        function showFiles(gsfiless) {
          var fileshtml = '';
          if (gsfiless.length > 0) {
            for (var num in gsfiless) {
              var curItem = gsfiless[num];
              gs_cur_items[curItem.id] = curItem;
              if(curItem.fileMode === 1){
                var premium_status = "premium";
              }
              else{
                var premium_status = "";
              }
              fileshtml += "<tr><td rel=\'"
                        + curItem.id 
                        + "\' id=\'"
                        + curItem.id  
                        + "\' class='file gsItem "
                        + premium_status
                        + " directory_info ext_"
                        + curItem.getExt()
                        + "'><i class=\"fa fa-file size-12\"></i> " 
                        + curItem.name 
                        + "</td><td>" 
                        + curItem.getSize()
                        + "</td><td>" 
                        + curItem.getLastDownload() 
                        + "</td><td>" 
                        + curItem.getLastMod() 
                        + "</td><td>" 
                        + curItem.getTotalDownload() 
                        + "</td><td>" 
                        + curItem.getTodayDownload() 
                        + "</td></tr>";
            }
          }
          return fileshtml;
        }
        
        function showDirs(gsfiless) {
          var dirshtml = '';
          var gs_lastparent = $('#' + $("#curDir").attr('rel')).parent().parent().parent().children('a');
          if (gs_lastparent.length > 0) {
            dirshtml += "<tr><td rel=\'up\' class=\'directory directory_info gsItem\'><i class=\"fi fi-folder size-14\"></i>up...</td><td class=\'no-sort\'>9999999 MB</td><td class=\'no-sort\'>2009-12-12</td><td class=\'no-sort\'>2099-12-12</td><td class=\'no-sort\'>9999999</td><td class=\'no-sort\'>9999999</td></tr>";
          }
          if (gsfiless.length > 0) {
            for (var numf in gsfiless) {
              var curItem = gsfiless[numf];
              gs_cur_items[curItem.id] = curItem;
              if(curItem.recycleBin === true){
                folderIcon = "<i class=\"fi-trash size-14\"></i>";
              }
              else {
                folderIcon = "<i class=\"fi-folder size-14\"></i>";
              }
              dirshtml += "<tr><td rel=\'"
                        + curItem.id 
                        + "\' class=\'directory directory_info gsItem\'>"
                        + folderIcon
                        + curItem.name
                        + "</td><td class=\'no-sort\'>9999999 MB</td><td class=\'no-sort\'>2099-12-12</td><td class=\'no-sort\'>2099-12-12</td><td class=\'no-sort\'>9999999</td><td class=\'no-sort\'>9999999</td></tr>";
            }
          }
          return dirshtml;
        }

        function showContent(gsdirss, gsfiless, page) {
          // Display content          
          var fileshtml = showFiles(gsfiless);
          if(page === 0){
            var dirshtml = showDirs(gsdirss);
          }
          else{
            var dirshtml = "";
          }
          $('#gs_dir_content tbody').html(dirshtml + fileshtml);
          
          // Integrate context menu
          $('td.file').contextMenu({
            menu: 'gsFileMenu'
          },
          function (action, el, pos) {            
            $(el).doGSAction({action: parseInt(action), script: o.script, type: 'file', lg: o.language});
          },
          manageGsMenu);
          if(page === 0){
            $('td.directory').contextMenu({
              menu: 'gsDirMenu'
            },
            function (action, el, pos) {
              $(el).doGSAction({action: parseInt(action), script: o.script, type: 'dir', lg: o.language});
            },
            manageGsMenu);
          }
          
          // Set handlers
          $('table.table tr').find('td.gsItem').unbind('click');
          $('table.table tr').find('td.gsItem').bind('click', function (e) {
            var cur_element = $(this);
            var rel = $(this).attr('rel');
            if (rel !== 'up') {
              if (cur_element.parent().hasClass('rowSelected')) {
                cur_element.parent().removeClass('rowSelected');
              } else {
                cur_element.parent().addClass('rowSelected');
                if((!e.ctrlKey && !e.metaKey) || (e.ctrlKey && e.metaKey)){
                  $("#gs_content_table tr.rowSelected").each(function() {
                    if($(this).find('td.gsItem').attr('rel') !== rel){
                      $(this).removeClass('rowSelected');
                    }
                  });
                }
              }
            }
            $(".contextMenu").hide();
            return false;
          });
          
          // Set size for main content based on panel's height
          if($("#panel").hasClass("active")) {
            $("div.main").height(deviceHeight - 318);
          }         
          else {
            $("div.main").height(deviceHeight - 178);
          }
          $('div.sidebar-fm').height($('div.small-10.columns').height());          
          
          // Initialize datatable
          $('#gs_content_table').dataTable({
            destroy: true,
            paging: false,
            searching: false,
            autoWidth: false,
            stripeClasses: [],
            columnDefs: [
              { type: "html", targets: 0 },
              { type: "num", targets: [4, 5] },
              { type: "Date.parse()", targets: [2, 3] }
            ],
            order: [[ 3, 'desc' ]]            
          });          
        }
        
        function getContent(cObject, folder_id, t, page, perPage, callback){
          var offset = page * perPage;
          listFileAndFolder(folder_id, offset, perPage, function (data) {
            //Remember current dir id
            var gsdirs = new Array();
            var gsfiles = new Array();
            gs_cur_items = new Array();            
            
            // Hide loader
            $('.loader').hide();
            
            // Clear old datatable
            $('#gs_content_table').dataTable().fnDestroy();
            
            // Set up curDir element's attribute
            if(callback){
              global_parent_folder_path = '/';
              totalRecords = data.file_count;
              global_folder_id = folder_id;
              if (folder_id === '') {
                $("#curDir").html('root');
                $("#curDir").attr('rel', 'rootLink');
              }
              else{
                global_parent_folder_path = $('#' + folder_id).attr('rel');              
                $("#curDir").html(global_parent_folder_path);
                $("#curDir").attr('rel', $('a', cObject).attr('id'));
              }
              path_array = global_parent_folder_path.split("/");
              path_history = '/';
              var breadCrumbItemHtml = '<li>'
                    + '<a href=\"javascript:void()\" id=\"rootLink\">'
                    + '<i class=\"fi fi-cloud size-12\"></i>'
                    + ' Cloud Storage</a>'
                    + '</li>';
              for (var i = 1; i <= path_array.length - 2; i++) {
                dirItem = path_array[i].split("#");
                path_history += dirItem[0] + '#' + dirItem[1] + '/';
                breadCrumbItemHtml += '<li>'
                        + '<a href=\"#\/fm2\" rel=\"'
                        + path_history
                        + '\" id=\"'
                        + dirItem[1]
                        + '\"><i class=\"fi fi-folder-add size-12\"></i> '
                        + dirItem[0]
                        + '</a>'
                        + '</li>';
              }
              $(".breadcrumbs.mb0").html(breadCrumbItemHtml + "<span id=\"gsClipBoard\" rel=\"" + $('#gsClipBoard').attr('rel') + "\">"+$('#gsClipBoard').html()+"</span>");
            }
            
            // Get folder and file list
            for (var i in data.fileList) {
              var userFile = data.fileList[i];
              gsfiles.push(new gsItem("1", userFile.fields.file_name, global_parent_folder_path + userFile.fields.file_name, data.fileInfoDict[userFile.pk].file_size, userFile.pk, "", userFile.fields.modified_date.substring(0, 10), userFile.fields.download_count, data.fileInfoDict[userFile.pk].download_count_24h, userFile.fields.last_download_date.substring(0,10), userFile.fields.file_mode));
            }
            for (var i in data.folderList) {
              var folder = data.folderList[i];              
              if (folder.fields.folder_type === 1) {
                recycleBinID = folder.pk;//type=1 is recycle bin
              }
              var folderGS = new gsItem("2", folder.fields.name, global_parent_folder_path + folder.fields.name + "#" + folder.pk, "0", folder.pk, "dir", folder.fields.modified_date.substring(0, 10));
              if(folder.fields.folder_type === 1){
                folderGS.recycleBin = true;
              }
              else{
                folderGS.recycleBin = false;
              }
              gsdirs.push(folderGS);
            }
            
            // Show folder tree
            if(callback){
              if (folder_id === "" && !$("ul.file-tree-root").length) {
                var dirhtml = '<ul class=\"side-nav file-tree-root\"><li><a href=\"#/fm2\" id=\"rootLink\" class=\"active\"><i class=\"fi-cloud size-18\"></i> Cloud Storage</a>';
              }
              else {
                var dirhtml = '';
              }
              if (typeof (gsdirs) !== 'undefined' && gsdirs.length > 0) {
                dirhtml += "<ul class=\"side-nav file-tree\" style=\"display: none;\">";
                for (var num in gsdirs) {
                  var curItem = gsdirs[num];
                  if(curItem.recycleBin === true){
                    folderIcon = "<i class=\"fi-trash size-18\"></i>";
                  }
                  else {
                    folderIcon = "<i class=\"fi-folder size-18\"></i>";
                  }
                  dirhtml += "<li class=\"collapsed\"><a href=\"#/fm2\" rel=\"" + curItem.path + "/\" id=\"" + curItem.id + "\">" + folderIcon + curItem.name + "</a></li>";
                }
                dirhtml += "</ul></ul>";
              } else {
                gsdirs = new Array();
              }
              cObject.find('.start').html('');
              cObject.find('ul.file-tree').remove();
              cObject.removeClass('wait').append(dirhtml);            
              if (o.root === t) {
                cObject.find('ul:hidden').show();
              } else {
                cObject.find('ul:hidden').slideDown({duration: o.expandSpeed, easing: o.expandEasing});
              }
            }
            if (typeof (gsfiles) === 'undefined') {
              gsfiles = new Array();
            }            
            
            // Show content
            showContent(gsdirs, gsfiles, page, unescape(t));
            
            // Callback function
            if(callback){
              callback();
            }
            // Set handlers
            if(callback){
              setHandlers(cObject);
            }
            else{
              setHandlers();
            }
          });
        }
        
        function showTree(c, t) {//c is element, t is an a href tag, with id = folder_id, rel=folder_path
          // Initialize variable
          var cObject = $(c);
          var perPage = $('#itemsPerPage').val();
          cObject.addClass('wait');                           
          $(".jqueryFileTree.start").remove();
          var folder_id = t.id;
          var tableheader = '<table class=\'table\' role=\'grid\' id="gs_content_table"><thead><tr><th>' + gs_getTranslation(o.language, 7) + '</th><th>' + gs_getTranslation(o.language, 9) + '</th><th>' + gs_getTranslation(o.language, 8) + '</th><th>' + gs_getTranslation(o.language, 10) + '</th><th>' + gs_getTranslation(o.language, 50) + '</th></th><th>' + gs_getTranslation(o.language, 51) + '</th></tr></thead>';
          
          if (t === '' || t.id === 'rootLink'){
            folder_id = '';
          }          
          $('#gs_dir_content').html(tableheader + "<tbody></tbody><div class=\'loader\'><img id=\'loading-image\' src=\'/static/assets/frontend/images/ajax-spinner.gif\' alt=\'Loading...\'/></div></table>");
          $('.loader').show();
          getContent(cObject, folder_id, t, 0, perPage, function(){
            // Remove old pagination
            if($('#fm_pagination').length){
              $('#fm_pagination').remove();
            }
            
            // Initialize pagination
            if(totalRecords !== 0 && parseInt(perPage) !== 0){                            
              $('#curDir').after('<ul class=\'pagination right\' id=\'fm_pagination\' role=\'menubar\' aria-label=\'Pagination\'></ul>');
              $('#fm_pagination').twbsPagination({
                totalPages: (totalRecords % perPage === 0) ? (totalRecords / perPage) : (Math.ceil(totalRecords / perPage)),
                prev: '&laquo; Previous',
                next: 'Next &raquo;',
                first: '&laquo;&laquo; First',
                last: 'Last &raquo;&raquo;',
                nextClass: 'arrow',
                prevClass: 'arrow',
                activeClass: 'current',
                disabledClass: 'unavailable',
                visiblePages: 10,
                onPageClick: function (event, page) {
                  $('.loader').show(); 
                  getContent(null, global_folder_id, null, page - 1, $('#itemsPerPage').val());
                }
              });
            }
          });          
        }

        function setHandlers(t) {                    
          // Unbind click events
          if(typeof(t) !== 'undefined'){
            $(t).find('li > a').unbind('click');
            $('ul.breadcrumbs li a').unbind('click');
          }          
          $('td.directory.directory_info').unbind('dblclick');
          $('td.file.directory_info').unbind('dblclick');                    
          
          // Bind click events
          if(typeof(t) !== 'undefined'){
            $(t).find('li > a').bind('click', function (e) {
              e.stopPropagation();
              showTree($(this).parent(), this); //this here is the tag a href with id=folder id
              $(this).parent().removeClass('collapsed').addClass('expanded');
              $(this).addClass('active');
              relAttr = $(this).attr('id');
              $('ul.file-tree-root').find('a').each(function(){
                if($(this).attr('id') !== relAttr){
                  $(this).removeClass('active');
                }
              });
            });
            $('ul.breadcrumbs li a').bind('click', function(e){
              e.stopPropagation();
              $('#'+$(this).attr('id')).trigger('click'); 
              return false;
            });
          }          
          $('td.directory.directory_info').bind('dblclick', function(e){
            e.stopPropagation();
            if($(this).attr("rel") === 'up'){
              $('#'+$('#curDir').attr('rel')).parent().parent().parent().children('a').trigger('click'); 
              return false;
            }
            else{
              $('#'+$(this).attr('rel')).trigger('click'); 
              return false;
            }
          });                
          $('td.file.directory_info').bind('dblclick', function(e){
            e.stopPropagation();
            $(this).doGSAction({action: 25, script: o.script, type: 'context', lg: o.language, fileID: $(this).attr('rel'), fileName: $(this).text()});
          });
        }                
        
        function showRoot() {
          showTree($('#gs_dir_list'), '');
        }

        var cusElement = $('#gs_dir_list');
        
        // Loading message
        cusElement.html('<ul class="jqueryFileTree start"><li class="wait">' + o.loadMessage + '<li></ul>');
        
        // Get the initial file list
        cusElement.find('#rootLink').bind('click', showRoot);
        showRoot();
      },
      
      doGSAction: function (o) {
        var curDir = $("#curDir").attr('rel');
        var dataForSend = null;
        var gsitem = gs_get_cur_item($(this).attr('rel'));

        if (gsitem === null) {
          //alert('no gsitem');
        }
        
        if (o.action === 20) { // select
          $("#gs_content_table td.file.gsItem").each(function () {
            $(this).parent().addClass('rowSelected');            
          });
          return false;
        }
        
        if (o.action === 21) { // deselect
          $("#gs_content_table td.gsItem").each(function () {
            $(this).parent().removeClass('rowSelected');
          });
          return false;
        }
        
        if (o.action === 22) { // invert select
          $("#gs_content_table td.gsItem").each(function () {
            if ($(this).attr('rel') !== 'up') {
              if ($(this).parent().hasClass('rowSelected')) {
                $(this).parent().removeClass('rowSelected');
              } else {
                $(this).parent().addClass('rowSelected');
              }
            }
          });
          return false;
        }
        
        if (o.action === 28) { // set premium file
          setPremiumFile(o, curDir, gsitem);
          return;
        }
        
        if (o.action === 29) {
          $('#gs_uploadbutton').trigger('click');
        }

        if (o.action === 23) { // zip
          unZipItem(o, curDir, gsitem);
          return;
        }

        if (o.action === 12) { // show notepad
          showNotePad(o, curDir, gsitem);
          return;
        }

        if (o.action === 13) { // copy as
          copyAs(o, curDir, gsitem);
          return;
        }

        if (o.action === 14) { // show upload
          $("button.close-modal").on('click', function(){
            $(this).closest('div.reveal-modal').foundation('reveal', 'close');
            $('#upload-progress tbody').find('tr.deactivate, tr.initialize').remove();
          });
          
          $('#uploadfile').on('closed.fndtn.reveal', function () {
            $('#upload-progress tbody').find('tr.deactivate, tr.initialize').remove();
          });                    
          
          $('#gsuploadfiles_button').unbind('click');//remove previous event handler          
          return;
        }

        if (o.action === 15) { // show image viewer
          showImageViewer(o, curDir, gsitem);
          return;
        }
        if (o.action === 16) { // show crop zoom image
          showJcrop(o, curDir, gsitem);
          return;
        }
        if (o.action === 18) { // ckeditor
          showCKEditor(o, curDir, gsitem);
          return;
        }
        if (o.action === 19) { // zip
          zipItem(o, curDir, gsitem);
          return;
        }
        if (o.action === 7) { // copy
          var clipBoard = $("#gsClipBoard");
          gs_storeSelectedItems();
          clipBoard.html('(Copy) ' + gs_clipboard.length + ' ' + gs_getTranslation(o.lg, 30));
          clipBoard.attr('rel', o.action);
          return;
        }
        if (o.action === 8) { // cut
          var clipBoard = $("#gsClipBoard");
          gs_storeSelectedItems();
          clipBoard.html('You have chosen ' + gs_clipboard.length + ' ' + gs_getTranslation(o.lg, 30));
          clipBoard.attr('rel', o.action);
          return;
        }
        if (o.action === 9) { //paste
          pasteItems(o, curDir, gsitem);
          return;
        }
        if (o.action === 10) { //rename
          renameItem(o, curDir, gsitem);
          return;
        }
        if (o.action === 11 || o.action === 25) { //get download links
          var regexp = new RegExp('#([^\\s]*)','g');
          $("input[name='option']").unbind('change');
          $("input[name='option']").prop('checked',false);
          $("input#normal-download").prop('checked',true);
          $("tbody#download_url_list").removeClass("hidden-table");
          $('#sort_by_name').unbind('click');
          if(o.action === 11){ 
            $('#download').foundation('reveal', 'open');
            $("button.close-modal").on('click', function() {
              $(this).closest('div.reveal-modal').foundation('reveal', 'close');
            });
          }
          showItemDownloadLink(o, curDir, gsItem);          
          $("input[name='option']").on('change', function(){
            switch($(this).attr('id')){
              case "not-include-file-key":
                if($(this).is(':checked')){
                  $('tbody#download_url_list tr.original').each(function(){
                    $('tbody#no_key_url_list').append("<tr rel=\"" + $(this).attr('rel') + "\" id=\"" + $(this).attr('id') + "-no-key\"><td>" + $(this).find('td').text().replace(regexp, '') + "</td></tr>");
                  });
                }
                else{
                  $('tbody#download_url_list tr.original').each(function(){
                    $('tbody#no_key_url_list tr#'+$(this).attr('id')+'-no-key').remove();
                  });
                }
                break;
              case "auto-download-torrent":
                if($(this).is(':checked')){
                  $('tbody#download_url_list tr.original').each(function(){
//                    if($(this).siblings('tr#'+$(this).attr('id')+'-no-key').length){
//                      $(this).siblings('tr#'+$(this).attr('id')+'-no-key').after("<tr rel=\"" + $(this).attr('rel') + "\" id=\"" + $(this).attr('id') + "-torrent\"><td>" + $(this).find('td').text() + "?auto=torrent</td></tr>");
//                    }
//                    else{
//                      $(this).after("<tr rel=\"" + $(this).attr('rel') + "\" id=\"" + $(this).attr('id') + "-torrent\"><td>" + $(this).find('td').text() + "?auto=torrent</td></tr>");
//                    }
                    $('tbody#torrent_url_list').append("<tr rel=\"" + $(this).attr('rel') + "\" id=\"" + $(this).attr('id') + "-torrent\"><td>" + $(this).find('td').text() + "?auto=torrent</td></tr>");
                  });
                }
                else{
                  $('tbody#download_url_list tr.original').each(function(){
                    $('tbody#torrent_url_list tr#'+$(this).attr('id')+'-torrent').remove();
                  });
                }
                break;
              case "auto-free-download":
                if($(this).is(':checked')){
                  $('tbody#download_url_list tr.original').each(function(){
                    $('tbody#browser_url_list').append("<tr rel=\"" + $(this).attr('rel') + "\" id=\"" + $(this).attr('id') + "-browser\"><td>" + $(this).find('td').text() + "?auto=browser</td></tr>");
                  });
                }
                else{
                  $('tbody#download_url_list tr.original').each(function(){
                    $('tbody#browser_url_list tr#'+$(this).attr('id')+'-browser').remove();
                  });
                }
                break;
              case "auto-direct-download":                
                if($(this).is(':checked')){
                  $('tbody#download_url_list tr.original').each(function(){
                    $('tbody#direct_url_list').append("<tr rel=\"" + $(this).attr('rel') + "\" id=\"" + $(this).attr('id') + "-direct\"><td>" + $(this).find('td').text() + "?auto=direct</td></tr>");       
                  });
                }
                else{
                  $('tbody#download_url_list tr.original').each(function(){
                    $('tbody#direct_url_list tr#'+$(this).attr('id')+'-direct').remove();
                  });
                }
                break;
              case "normal-download":
                if(!$(this).is(':checked')){
                  $('tbody#download_url_list').addClass('hidden-table');
                }
                else{
                  $('tbody#download_url_list').removeClass('hidden-table');
                }
                break;
            }
          });
          $('#sort_by_name').click(function(){
            var listID = ["tbody#download_url_list", "tbody#no_key_url_list", "tbody#torrent_url_list", "tbody#browser_url_list", "tbody#direct_url_list"];
            for (var i in listID){
              var $table= $(listID[i]);
           
              var rows = $table.find('tr').get();
              rows.sort(function (a, b) {
                var keyA = $(a).attr('rel');
                var keyB = $(b).attr('rel');
                if (keyA < keyB)
                  return -1;
                if (keyA > keyB)
                  return 1;
                return 0;
              });
              $.each(rows, function (index, row) {
                $table.append(row);
              });
            }            
          });
          return;
        }
        if (o.action === 2) { //new file
          newFile(o, curDir, gsitem);
          return;
        }
        if (o.action === 3) { //new dir
          $('#newfolder').foundation('reveal', 'open');
          $("button.close-modal").on('click', function() {
            $(this).closest('div.reveal-modal').foundation('reveal', 'close');
            $('#newDir').unbind('click');
          });
          $('#newDir').bind('click', function () {
            newDir(o, curDir, gsitem, $('input#dirName').val());
          });
          return;
        }
        if (o.action === 4) { //delete item
          deleteItem(o, curDir, gsitem);
          return;
        }
        if (o.action === 5) { //open dir
          $('#' + gsitem.id).trigger('click');
          return;
        }

        if (o.action === 6) { //move item to trash
          moveItemToTrash(o, curDir, gsitem);
          return;
        }

        function showCKEditor(o, curDir, gsitem) {
          var height = parseInt($(window).height()) - 100;
          var width = parseInt($(window).width()) - 100;
          $('#gsckeditor').dialog({title: 'CKEditor ' + gsitem.name, modal: true, width: width, height: height,
            buttons: [{
                click: function () {
                  $(this).dialog("close");
                  $('#gs_ckeditor_content').html('');
                },
                text: gs_getTranslation(o.lg, 28)
              },
              {
              text: gs_getTranslation(o.lg, 31),
              click: function () {
                $('#gs_ckeditor_content').hide();
                $(this).append('<div class="loadingDiv">&nbsp;</div>');
                //$(this).doGSAction({action: 13, type: 'file', script: o.script});
                texta = $('#gsckeditor').find('textarea');
                targetFile = texta.attr('rel');
                content = CKEDITOR.instances.gsFileContent.getData();
                dataForSend = {opt: 10, filename: targetFile, dir: curDir, filenContent: content};
                sendAndRefresh(o, dataForSend, true, function (data) {
                  $('#gs_ckeditor_content').find('div.loadingDiv').remove();
                  $('#gs_ckeditor_content').show();
                });
              }
            }]
          });
          $('#gs_ckeditor_content').html('<div class="loadingDiv">&nbsp;</div>');
          dataForSend = {opt: 9, filename: gsitem.name, dir: curDir};
          sendAndRefresh(o, dataForSend, false, function (data) {
            $('#gs_ckeditor_content').html('<textarea id="gsFileContent" name=\'gsFileContent\' rel="' + gsitem.name + '">' + data + '</textarea>');

            if (typeof (CKEDITOR.instances.gsFileContent) !== 'undefined') {
              CKEDITOR.remove(CKEDITOR.instances['gsFileContent']);
            }

            CKEDITOR.replace('gsFileContent', {language: o.lg});

          });
        }

        function showNotePad(o, curDir, gsitem) {
          var height = parseInt($(window).height()) - 100;
          var width = parseInt($(window).width()) - 100;
          var rows = parseInt(height / 30);
          var cols = parseInt(width / 10);
          $('#gsnotepadedit').dialog({title: 'Edit ' + gsitem.name, modal: true, width: width, height: height,
            buttons: [{
                click: function () {
                  $(this).dialog("close");
                },
                text: gs_getTranslation(o.lg, 28)
              },
              {
                text: gs_getTranslation(o.lg, 31),
                click: function () {
                  $(this).find('textarea').hide();
                  $(this).append('<div class="loadingDiv">&nbsp;</div>');
                  texta = $('#gsnotepadedit').find('textarea');
                  targetFile = texta.attr('rel');
                  content = texta.val();
                  dataForSend = {opt: 10, filename: targetFile, dir: curDir, filenContent: content};
                  sendAndRefresh(o, dataForSend, true, function (data) {
                    $('#gsnotepadedit').find('div.loadingDiv').remove();
                    $('#gsnotepadedit').find('textarea').show();
                  });
                }
              }]
          });
          $('#gsnotepadedit').html('<div class="loadingDiv">&nbsp;</div>');
          dataForSend = {opt: 9, filename: encodeURIComponent(gsitem.name), dir: curDir};
          sendAndRefresh(o, dataForSend, false, function (data) {
            $('#gsnotepadedit').html('<textarea name=\'gsFileContent\' rows="' + rows + '" cols="' + cols + '" rel="' + gsitem.name + '">' + data + '</textarea>');
          });
        }

        function showImageViewer(o, curDir, gsitem) {
          var height = parseInt($(window).height()) - 100;
          var width = parseInt($(window).width()) - 100;
          $('#gsimageviewer').dialog({title: 'Image viewer ' + gsitem.name, modal: true, width: width, height: height,
            buttons: [{
                click: function () {
                  $(this).dialog("close");
                  $('#gsimageviewer_content').html('');
                },
                text: gs_getTranslation(o.lg, 28)
              },
              {
                text: gs_getTranslation(o.lg, 32),
                click: function () {
                  $('#gsimageviewer_content').html('<div class="loadingDiv">&nbsp;</div>');
                  dataForSend = {opt: 13, filename: gsitem.name, dir: curDir, new_x: $('#gs_image_x').val(), new_y: $('#gs_image_y').val()};
                  sendAndRefresh(o, dataForSend, true, function (data) {
                    dataForSend = {opt: 15, filename: gsitem.name, dir: curDir};
                    $('#gsimageviewer_content').html('<img src="' + gs_makeUrl(o.script, $.param(dataForSend) + '&time=' + new Date().getTime()) + '" id="gs_imageviewer_image"/>');
                  });
                }
              }]
          });
          dataForSend = {opt: 15, filename: gsitem.name, dir: curDir};
          var imageSrc = gs_makeUrl(o.script, $.param(dataForSend) + '&time=' + new Date().getTime());
          $('#gs_image_x').val('');
          $('#gs_image_y').val('');
          $('#gsimageviewer_content').html('<img id="gs_imageviewer_image"/>');
          $('#gs_imageviewer_image').load(function () {
            var tImageelement = $(this);
            $('#gs_image_x').val(tImageelement.width());
            $('#gs_image_y').val(tImageelement.height());
            $('#gs_image_x').attr('rel', tImageelement.width());
            $('#gs_image_y').attr('rel', tImageelement.height());
          });
          $('#gs_imageviewer_image').attr('src', imageSrc);
        }

        function showJcrop(o, curDir, gsitem) {
          var gs_jcrop_div = $('#gs_jcrop_div');
          var height = parseInt($(window).height()) - 100;
          var width = parseInt($(window).width()) - 100;
          gs_jcrop_div.dialog({title: 'JCrop ' + gsitem.name, width: width, height: height, modal: true,
            buttons: [{
                click: function () {
                  $(this).dialog("close");
                },
                text: gs_getTranslation(o.lg, 28)
              }, {
                text: gs_getTranslation(o.lg, 33),
                click: function () {
                  $('#gs_jcrop_div_container').html('<div class="loadingDiv">&nbsp;</div>');
                  $('#gs_jcrop_form').submit();
                }
              }]
          });
          $('#gs_jcrop_div_container').html('<div class="loadingDiv">&nbsp;</div>');
          dataForSend = {opt: 15, filename: gsitem.name, dir: curDir};
          var imageSrc = gs_makeUrl(o.script, $.param(dataForSend) + '&time=' + new Date().getTime());
          $('#gs_jcrop_div_container').html('<img src="' + imageSrc + '" id="gsjcrop_target"/>');
          $('#gsjcrop_target').load(function () {
            $('#gsjcrop_target').Jcrop({onSelect: updateCoords});
          });
          $("#gs_jcrop_dir").val(curDir);
          $("#gs_jcrop_filename").val(gsitem.name);
        }

        function pasteItems(o, curDir, gsitem) {
          var clipBoard = $("#gsClipBoard");
          var opt = null;
          var selectedFiles = gsGetSelectedItemsPath();
          //get file_id_list stored in gs_clipboard
          var file_id_list = new Array();
          var folder_id_list = new Array();
          for (var xx in gs_clipboard) {
            if (gs_clipboard[xx].type === "1") {//file
              file_id_list.push(gs_clipboard[xx].id);
            }
            if (gs_clipboard[xx].type === "2") {//folder
              folder_id_list.push(gs_clipboard[xx].id);
            }
          }        
          if (parseInt(clipBoard.attr('rel')) === 7) { //copy
            opt = 5;//copy
          } 
          else if (parseInt(clipBoard.attr('rel')) === 8) { // paste
            gs_clipboard = new Array();
            clipBoard.html('');
            //$('#gsclipboardContent').html('');
            clipBoard.attr('rel', '');
            opt = 7;//move
          } 
          else {
            return;
          }
          if (selectedFiles !== null) {
            var folder_id = curDir;
            if (curDir === "")
              folder_id = "0";
            if (curDir === "rootLink")
              folder_id = "0";

            if (file_id_list.length > 0) {
              moveFile(file_id_list, folder_id, function () {
                $('#' + $("#curDir").attr('rel')).trigger('click');
              });
            }

            if (folder_id_list.length > 0) {
              moveFolder(folder_id_list, folder_id, function () {
                $('#' + $("#curDir").attr('rel')).trigger('click');
              });
            }
          }
          if (opt === 7) {
            for (var xx in gs_clipboard) {
              if (gs_clipboard[xx].getExt() === 'dir') {
                $("#" + gs_clipboard[xx].id).parent().remove();
              }
            }
          }
        }

        function copyAs(o, curDir, gsitem) {
          var newName = window.prompt(gs_getTranslation(o.lg, 34) + ': ', htmlspecialchars_decode(gsitem.name, 'ENT_QUOTES'));
          if (newName === null) {
            return;
          }
          dataForSend = {opt: 14, filename: gsitem.name, dir: curDir, newfilename: newName};
          sendAndRefresh(o, dataForSend, true);
        }

        function unZipItem(o, curDir, gsitem) {
          var newName = window.prompt(gs_getTranslation(o.lg, 43) + ': ', 'unzipped_' + htmlspecialchars_decode(gsitem.name, 'ENT_QUOTES'));
          if (newName === null) {
            return;
          }
          dataForSend = {opt: 17, filename: gsitem.name, dir: curDir, newfilename: newName};
          sendAndRefresh(o, dataForSend, true);
        }

        function zipItem(o, curDir, gsitem) {
          var newName = window.prompt(gs_getTranslation(o.lg, 41) + ': ', htmlspecialchars_decode(gsitem.name, 'ENT_QUOTES') + '.zip');
          if (newName === null) {
            return;
          }
          dataForSend = {opt: 16, filename: gsitem.name, dir: curDir, newfilename: newName};
          sendAndRefresh(o, dataForSend, true);
        }

        function renameItem(o, curDir, gsitem) {
          var newName = window.prompt(gs_getTranslation(o.lg, 35) + ': ', htmlspecialchars_decode(gsitem.name, 'ENT_QUOTES'));
          if (newName === null) {
            return;
          }
          dataForSend = {opt: 6, filename: curDir + gsitem.name, dir: curDir, newfilename: newName};          
          if (gsitem.type === "1") {
            editFile(gsitem.id, newName, function () {
              $('#' + $("#curDir").attr('rel')).trigger('click');
            });
          }
          if (gsitem.type === "2") {
            editFolder(gsitem.id, newName, function () {
              $('#' + $("#curDir").attr('rel')).trigger('click');
            });
          }
        }

        function newFile(o, curDir, gsitem) {          
          $('#rootLink').trigger('click');
        }

        function newDir(o, curDir, gsitem, dirName) {
          if (dirName === null || dirName.length < 1) {
            return;
          }          
          if (curDir === 'rootLink') curDir = 0;
          newFolder(dirName, curDir, function () {
            $('#' + $("#curDir").attr('rel')).trigger('click');
            $('#newfolder').foundation('reveal', 'close');
            $('#newDir').unbind('click');
          });
        }

        function deleteItem(o, curDir, gsitem) {
          if (!window.confirm(gs_getTranslation(o.lg, 38))) {
            return;
          }
          var file_id_list = gsGetSelectedItemsFileID();
          var folder_id_list = gsGetSelectedItemsFolderID();
          if (file_id_list.length > 0) {
            deleteFile(file_id_list, function () {
              $('#' + $("#curDir").attr('rel')).trigger('click');
            });
          }
          if (folder_id_list.length > 0) {
            deleteFolder(folder_id_list, function () {
              $('#' + $("#curDir").attr('rel')).trigger('click');
            });
          }
        }

        function showItemDownloadLink(o, curDir, gsitem) {          
          var getLink_file_id_list = new Array();
          var download_url_list = new Array();
          var serverURL = location.protocol + '//' + location.host;
          var url_path_array;
          var regexp = new RegExp('#([^\\s]*)','g');
          
          if(typeof (o.fileID) === 'undefined'){
            var file_id_list = gsGetSelectedItemsFileID();
            var file_name_list = gsGetSelectedItemsFileName();
          }
          else{
            var file_id_list = new Array(o.fileID);
            var file_name_list = new Array(o.fileName);
          }          
          
          for (var i in file_id_list) {
            file_id = file_id_list[i];//gsitem.id
            file_name = file_name_list[i];//gsitem.name
            var realFileKey = window.localStorage.getItem(StorageFileKeyPrefix + file_id);

            if (realFileKey) {
              console.log("Found FileKey=" + realFileKey);
              var download_url = '/dl/' + file_id + '/' + file_name.trim() + '#' + realFileKey;
              console.log("download_url=" + download_url);
              download_url_list.push(download_url);
            } else {
              getLink_file_id_list.push(file_id);
            }
          }

          $('tbody#download_url_list').html('');
          $('tbody#no_key_url_list').html('');
          $('tbody#torrent_url_list').html('');
          $('tbody#browser_url_list').html('');
          $('tbody#direct_url_list').html('');
          for (var i in download_url_list){
            url_path_array = download_url_list[i].split("/");            
            $('tbody#download_url_list').append('<tr class=\'original\' rel=\'' + decodeURIComponent(url_path_array[3].replace(regexp, '')) + '\' id=\'' + url_path_array[2] + '\'><td>' + serverURL + download_url_list[i] + '</td></tr>');
            if(typeof (o.fileID) !== 'undefined'){
              window.open(download_url_list[i],'_blank');
            }
          }
          if (getLink_file_id_list.length > 0) {
            if(typeof (o.fileID) === 'undefined'){
              $(".loader").show();
            }
            getLink(getLink_file_id_list, function (data) {
              if (data.download_url_list.length > 0) {
                for (var i in data.download_url_list){
                  url_path_array = data.download_url_list[i].split("/");                  
                  $('tbody#download_url_list').append('<tr class=\'original\' rel=\'' + decodeURIComponent(url_path_array[5].replace(regexp, '')) + '\' id=\'' + url_path_array[4] + '\'><td>' + data.download_url_list[i] + '</td></tr>');
                  if(typeof (o.fileID) !== 'undefined'){
                    window.open(data.download_url_list[i],'_blank');
                  }
                }
              }
              else{
                alert("Error while getting download links");
              }              
              $(".loader").hide();                
            });        
          }          
          copyToClipboard();          
          return;
        }
        
        function copyToClipboard(){
          var client = new ZeroClipboard($('#copy_links_to_clipboard'));          
          
          client.on('ready', function (event) {
            client.on('copy', function (event) {
              var contentClipboard = "";
              if(!$('tbody#download_url_list').hasClass('hidden-table')){
                $('tbody#download_url_list tr td').each(function(){
                  contentClipboard += $(this).text() + "\n";            
                });
              }
              $('tbody#no_key_url_list tr td').each(function(){
                contentClipboard += $(this).text() + "\n";            
              });
              $('tbody#torrent_url_list tr td').each(function(){
                contentClipboard += $(this).text() + "\n";            
              });
              $('tbody#browser_url_list tr td').each(function(){
                contentClipboard += $(this).text() + "\n";            
              });
              $('tbody#direct_url_list tr td').each(function(){
                contentClipboard += $(this).text() + "\n";            
              });              
              event.clipboardData.setData('text/plain', contentClipboard);
            });

            client.on('aftercopy', function (event) {
              $("div#contentClipboard").show();
              $("div#contentClipboard textarea").val(event.data['text/plain']);
            });
          });

          client.on('error', function (event) {
            ZeroClipboard.destroy();
          });
        }
        
        function moveItemToTrash(o, curDir, gsitem) {
          if (!window.confirm(gs_getTranslation(o.lg, 49))) {
            return;
          }

          var file_id_list = gsGetSelectedItemsFileID();
          var folder_id_list = gsGetSelectedItemsFolderID();

          if (!recycleBinID) {
            alert("recycleBinID is not set!");
            return;
          }

          if (file_id_list.length > 0) {
            moveFile(file_id_list, recycleBinID, function () {
              $('#' + $("#curDir").attr('rel')).trigger('click');
            });
          }
          if (folder_id_list.length > 0) {
            moveFolder(folder_id_list, recycleBinID, function () {
              $('#' + $("#curDir").attr('rel')).trigger('click');
            });
          }
        }
        
        function setPremiumFile(o, curDir, gsitem) {          
          if (!window.confirm(gs_getTranslation(o.lg, 53))) {
            return;
          }
          var file_id_list = gsGetSelectedItemsFileID();
          var folder_id_list = gsGetSelectedItemsFolderID();

          if (file_id_list.length > 0) {
            setPremium(file_id_list, function (data, textStatus, jqXHR) {
              if(textStatus === "success"){
                $('#' + $("#curDir").attr('rel')).trigger('click');
              }
            },function(jqXHR, textStatus, errorThrown){
              console.log(jqXHR + " - " + textStatus + " - " + errorThrown);
            });
          }
        }

        function sendAndRefresh(o, dataForSend, refresh, callback, type) {
          if (refresh) {
            gs_show_loading();
          }
          if (typeof (type) === 'undefined') {
            type = 'text';
          }
          $.ajax({
            type: 'POST',
            url: o.script,
            data: $.param(dataForSend) + '&time=' + new Date().getTime(),
            dataType: type,
            contentType: 'application/x-www-form-urlencoded;charset=utf-8',
            beforeSend: function (xhr) {
              xhr.setRequestHeader('Accept', "text/html; charset=utf-8");
            },
            success: function (data) {
              gsCheckResponce(data);
              if (refresh) {
                $('#' + $("#curDir").attr('rel')).trigger('click');
              }
              if (callback) {
                callback(data);
              }
            }});
        }

        function htmlspecialchars_decode(string, quote_style) {
          // http://kevin.vanzonneveld.net
          // +   original by: Mirek Slugen
          // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
          // +   bugfixed by: Mateusz "loonquawl" Zalega
          // +      input by: ReverseSyntax
          // +      input by: Slawomir Kaniecki
          // +      input by: Scott Cariss
          // +      input by: Francois
          // +   bugfixed by: Onno Marsman
          // +    revised by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
          // +   bugfixed by: Brett Zamir (http://brett-zamir.me)
          // +      input by: Ratheous
          // +      input by: Mailfaker (http://www.weedem.fr/)
          // +      reimplemented by: Brett Zamir (http://brett-zamir.me)
          // +    bugfixed by: Brett Zamir (http://brett-zamir.me)
          // *     example 1: htmlspecialchars_decode("<p>this -&gt; &quot;</p>", 'ENT_NOQUOTES');
          // *     returns 1: '<p>this -> &quot;</p>'
          // *     example 2: htmlspecialchars_decode("&amp;quot;");
          // *     returns 2: '&quot;'
          var optTemp = 0,
                  i = 0,
                  noquotes = false;
          if (typeof quote_style === 'undefined') {
            quote_style = 2;
          }
          string = string.toString().replace(/&lt;/g, '<').replace(/&gt;/g, '>');
          var OPTS = {
            'ENT_NOQUOTES': 0,
            'ENT_HTML_QUOTE_SINGLE': 1,
            'ENT_HTML_QUOTE_DOUBLE': 2,
            'ENT_COMPAT': 2,
            'ENT_QUOTES': 3,
            'ENT_IGNORE': 4
          };
          if (quote_style === 0) {
            noquotes = true;
          }
          if (typeof quote_style !== 'number') { // Allow for a single string or an array of string flags
            quote_style = [].concat(quote_style);
            for (i = 0; i < quote_style.length; i++) {
              // Resolve string input to bitwise e.g. 'PATHINFO_EXTENSION' becomes 4
              if (OPTS[quote_style[i]] === 0) {
                noquotes = true;
              } else if (OPTS[quote_style[i]]) {
                optTemp = optTemp | OPTS[quote_style[i]];
              }
            }
            quote_style = optTemp;
          }
          if (quote_style & OPTS.ENT_HTML_QUOTE_SINGLE) {
            string = string.replace(/&#0*39;/g, "'"); // PHP doesn't currently escape if more than one 0, but it should
            // string = string.replace(/&apos;|&#x0*27;/g, "'"); // This would also be useful here, but not a part of PHP
          }
          if (!noquotes) {
            string = string.replace(/&quot;/g, '"');
          }
          // Put this in last place to avoid escape being double-decoded
          string = string.replace(/&amp;/g, '&');

          return string;
        }


      }
    });

  })($);

//$ Context Menu Plugin
//
// Version 1.01
//
// Cory S.N. LaViska
// A Beautiful Site (http://abeautifulsite.net/)
//
// More info: http://abeautifulsite.net/2008/09/jquery-context-menu-plugin/
//
// Terms of Use
//
// This plugin is dual-licensed under the GNU General Public License
//   and the MIT License and is copyright A Beautiful Site, LLC.
//
if ($)
  (function () {
    $.extend($.fn, {
      contextMenu: function (o, callback, onShowMenu) {
        // Defaults
        if (o.menu === undefined)
          return false;
        if (o.inSpeed === undefined)
          o.inSpeed = 150;
        if (o.addSelectedClass === undefined)
          o.addSelectedClass = true;
        if (o.outSpeed === undefined)
          o.outSpeed = 75;
        // 0 needs to be -1 for expected results (no fade)
        if (o.inSpeed === 0)
          o.inSpeed = -1;
        if (o.outSpeed === 0)
          o.outSpeed = -1;
        // Loop each context menu
        $(this).each(function () {
          var el = $(this);
          var offset = $(el).offset();
          // Add contextMenu class
          $('#' + o.menu).addClass('contextMenu');
          // Simulate a true right click
          $(this).mousedown(function (e) {
            var evt = e;
            evt.stopPropagation();
            $(this).mouseup(function (e) {
              e.stopPropagation();
              var srcElement = $(this);              
              srcElement.unbind('mouseup');
              if (evt.button === 2) {
                // Hide context menus that may be showing
                $(".contextMenu").hide();
                
                // Get this context menu
                var menu = $('#' + o.menu);
                menu.enableContextMenuItems();
                if (onShowMenu) {
                  if (!onShowMenu(srcElement, menu)) {
                    return false;
                  }
                }
                if (!srcElement.parent().hasClass('rowSelected')) {
                  $("#gs_content_table td.gsItem").each(function () {
                    $(this).parent().removeClass('rowSelected');
                  });
                  if (o.addSelectedClass) {
                    srcElement.parent().addClass('rowSelected');
                  }
                }

                var jmenu = $(menu);
                if ($(el).hasClass('disabled')) {
                  return false;
                }
                // Detect mouse position
                var d = {}, x, y;
                if (self.innerHeight) {
                  d.pageYOffset = self.pageYOffset;
                  d.pageXOffset = self.pageXOffset;
                  d.innerHeight = self.innerHeight;
                  d.innerWidth = self.innerWidth;
                } else if (document.documentElement &&
                        document.documentElement.clientHeight) {
                  d.pageYOffset = document.documentElement.scrollTop;
                  d.pageXOffset = document.documentElement.scrollLeft;
                  d.innerHeight = document.documentElement.clientHeight;
                  d.innerWidth = document.documentElement.clientWidth;
                } else if (document.body) {
                  d.pageYOffset = document.body.scrollTop;
                  d.pageXOffset = document.body.scrollLeft;
                  d.innerHeight = document.body.clientHeight;
                  d.innerWidth = document.body.clientWidth;
                }
                (e.pageX) ? x = e.pageX : x = e.clientX + d.scrollLeft;
                (e.pageY) ? y = e.pageY : y = e.clientY + d.scrollTop;

                // Show the menu
                $('#fileTreeDemo_1').unbind('click');
                y -= 60; //fix bug ui
                x -= 50; //fix menu too far from mouse
                jmenu.css({top: y, left: x}).fadeIn(o.inSpeed);

                // Hover events
                jmenu.find('a').mouseover(function () {
                  jmenu.find('li.hover').removeClass('hover');
                  if (!$(this).parent().parent().hasClass('subContextMenu')) {
                    jmenu.find('ul.subContextMenu').hide();
                  }
                  $(this).parent().addClass('hover');
                  $(this).parent().find('ul').css({top: 0, left: 120}).fadeIn(o.inSpeed);
                }).mouseout(function () {
                  jmenu.find('li.hover').removeClass('hover');
                });

                // When items are selected
                menu.find('a').unbind('click');
                menu.find('a').bind('click', function () {
                  if ($(this).parent().hasClass('disabled')) {
                    return false;
                  }
                  $(".contextMenu").hide();
                  // Callback
                  if (callback) {
                    callback($(this).attr('rel'), $(srcElement), {x: x - offset.left, y: y - offset.top, docX: x, docY: y});
                  }
                  return false;
                });

                // Hide bindings
//                setTimeout(function () { // Delay for Mozilla
//                  $(document).click(function () {
//                    $(menu).fadeOut(o.outSpeed);
//                  });
//                }, 0);
              }
            });
          });

          // Disable text selection
          //There is jquery bug here
          //if( $.browser.mozilla ) {
          //  $('#' + o.menu).each( function() { $(this).css({ 'MozUserSelect' : 'none' }); });
          //} else if( $.browser.msie ) {
          //  $('#' + o.menu).each( function() { $(this).bind('selectstart.disableTextSelect', function() { return false; }); });
          //} else {
          //  $('#' + o.menu).each(function() { $(this).bind('mousedown.disableTextSelect', function() { return false; }); });
          //}

          // Disable browser context menu (requires both selectors to work in IE/Safari + FF/Chrome)
          $(el).add($('ul.contextMenu')).bind('contextmenu', function () {
            return false;
          });

        });
        return $(this);
      },
      // Disable context menu items on the fly
      disableContextMenuItems: function (o) {
        if (o === undefined) {
          // Disable all
          $(this).find('li').addClass('disabled');
          return($(this));
        }
        $(this).each(function () {
          if (o !== undefined) {
            var d = o.split(',');
            for (var i = 0; i < d.length; i++) {
              //alert(d[i]);
              $(this).find('a[rel="' + d[i] + '"]').parent().addClass('disabled');
            }
          }
        });
        return($(this));
      },
      // Enable context menu items on the fly
      enableContextMenuItems: function (o) {
        if (o === undefined) {
          // Enable all
          $(this).find('li.disabled').removeClass('disabled');
          return($(this));
        }
        $(this).each(function () {
          if (o !== undefined) {
            var d = o.split(',');
            for (var i = 0; i < d.length; i++) {
              $(this).find('a[rel="' + d[i] + '"]').parent().removeClass('disabled');

            }
          }
        });
        return($(this));
      },
      // Disable context menu(s)
      disableContextMenu: function () {
        $(this).each(function () {
          $(this).addClass('disabled');
        });
        return($(this));
      },
      // Enable context menu(s)
      enableContextMenu: function () {
        $(this).each(function () {
          $(this).removeClass('disabled');
        });
        return($(this));
      },
      // Destroy context menu(s)
      destroyContextMenu: function () {
        // Destroy specified context menus
        $(this).each(function () {
          // Disable action
          $(this).unbind('mousedown').unbind('mouseup');
        });
        return($(this));
      }
    });
  })($);