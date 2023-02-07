var nhtqConfig = {
    Domain : 'maidzo.vn',
    apiDomain : 'https://maidzo.vn/',
    apiaddtocart : 'page/add_items_cart_old/',
    apiexchangerate : 'page/exchange_rate/',
    cart : 'web_app/#/gio-hang/',
};

var HTMLUtil = {
    hideElement: function(selector) {
        var element = this.select(selector);
        if (element != null && typeof element !== 'undefined' && typeof element.style !== 'undefined') {
            element.style.display = 'none';
        }
    },
    select: function(selector, element) {
        if (typeof selector !== 'string') {
            return null;
        }
        if (typeof element === 'undefined' || !element) {
            element = document;
        }
        return element.querySelector(selector);
    },
    selectAll: function(selector, element) {
        if (typeof element === 'undefined' || !element) {
            return document.querySelectorAll(selector);
        }
        return element.querySelectorAll(selector);
    },
    formatMoney: function(input) {
        return input.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1.");
    },
    each: function(elements, callback) {
        for (var i in elements) {
            if (typeof elements[i] === 'object') {
                callback(elements[i]);
            }
        }
    },
    serialize: function (obj, prefix) {
        var str = [], p;
        for(p in obj) {
            if (obj.hasOwnProperty(p)) {
                var k = prefix ? prefix + "[" + p + "]" : p, v = obj[p];
                str.push((v !== null && typeof v === "object") ?
                    HTMLUtil.serialize(v, k) :
                    encodeURIComponent(k) + "=" + encodeURIComponent(v));
            }
        }
        return str.join("&");
    },
    get: function(url, callback) {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", url, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4
                && xhr.status === 200) {
                callback && callback(xhr.response);
            }
        };

        xhr.withCredentials = true;
        xhr.send();
    },
    post: function(url, data, callback) {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", url, true);
        xhr.responseType = 'json';
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                callback && callback(xhr.response);
            }
        };

        xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhr.withCredentials = true;
        if (data !== null && data !== undefined) {
            xhr.send(HTMLUtil.serialize(data));
        } else {
            xhr.send();
        }
    },
    fullHeight: function(element) {
        var e = null;
        if (typeof element === 'string') {
            e = HTMLUtil.select(element);
        } else {
            e = element;
        }
        if (e !== null) {
            e.style.height = window.innerHeight + 'px';
            HTMLUtil.addEvent(window, "resize", function(event) {
                e.style.height = window.innerHeight + 'px';
            });
        }
    },
    addEvent: function(object, type, callback) {

        if (object === null || typeof(object) === 'undefined') return;
        if (object.addEventListener) {
			console.log('addEventListener',type);
            object.addEventListener(type, callback, false);
        } else if (object.attachEvent) {
            object.attachEvent("on" + type, callback);
        } else {
            object["on"+type] = callback;
        }
    },
    getSearchUrl: function(website, keyword) {
        var url = "";
        switch(website) {
            case "taobao.com":
            case "taobao":
                url = 'http://s.taobao.com/search?q='+keyword;
                break;
            case "tmall.com":
            case "tmall.hk":
            case "tmall":
                url = 'http://list.tmall.com/search_product.htm?q='+keyword;
                break;
            case "1688.com":
            case "1688":
                url = 'http://s.1688.com/selloffer/offer_search.htm?keywords='+keyword;
                break;
            default:
                return null;
                break;
        }
        return url;
    },
    getItemUrl: function(website, itemId) {
        var url = "";
        switch(website) {
            case "taobao.com":
            case "taobao":
                url = 'https://item.taobao.com/item.htm?id='+itemId;
                break;
            case "tmall.com":
            case "tmall.hk":
            case "tmall":
                url = 'https://detail.tmall.com/item.htm?id='+itemId;
                break;
            case "1688.com":
            case "1688":
                url = 'https://detail.1688.com/offer/'+itemId+'.html';
                break;
            default:
                return null;
                break;
        }
        return url;
    },
    alert: function(msg, options) {
        var type = 'alert';
        var parent = 'body';
        if (typeof options !== 'undefined' && options !== null) {
            if (typeof options.type !== 'undefined') {
                type = options.type;
            }

            if (typeof options.parent !== 'undefined') {
                parent = options.parent;
            }
        }
        var html = '<div class="nhtqAlert nhtqAlert-'+type+'">' +
            '<div class="nhtqAlertContent">' +
                    '<div class="nhtqAlertMessage">' +
                        msg +
                    '</div>' +
                    '<button type="button" class="nhtqAlertClose" data-dismiss="alert" aria-label="Close">' +
                        '<span aria-hidden="true">\u00d7</span>' +
                    '</button>' +
                '</div>' +
            '</div>';
        var p = HTMLUtil.select(parent);
        // Đóng tất cả alert trong parent
        var olds = HTMLUtil.selectAll('.nhtqAlertWrap', p);
        if (olds.length > 0) {
            for(var i = 0; i < olds.length; i++) {
                olds[i].parentNode.removeChild(olds[i]);
            }
        }
        if (typeof p !== 'undefined' && p !== null) {
            var e = document.createElement('div');
            e.classList.add('nhtqAlertWrap');
            e.innerHTML = html;
            HTMLUtil.select('.nhtqAlertClose', e).onclick = function() {
                e.parentNode.removeChild(e);
            };
            p.appendChild(e);
        }
    }
}



function NHToolbar()
{
    // Init
    var instance = this;
    HTMLUtil.post(nhtqConfig.apiDomain + "page/addon_config/", null, function(res) {
		var x = document.cookie;
		var theFrame = document.createElement('iframe');
		theFrame.src = "about:blank";
		theFrame.style.display = "none";
		document.body.appendChild(theFrame);
		window.console = theFrame.contentWindow.console;
		console.log('=====cookies:',x);
        instance.config = res;
        instance.hostname = instance.getHostName();
        instance.website = instance.getWebsite();
        instance.shop = instance.getShopInfo();
        instance.item = instance.getItemInfo();
        instance.sku = null;
        instance.selectedQuantity = 0;
        instance.subtotal = 0;
        instance.run();


    });
}


NHToolbar.prototype.itemDetailPatterns = [
    'item.taobao.com',
    'tw.taobao.com/item',
    'world.taobao.com/item',
    'detail.tmall.com',
    'taiwan.tmall.com/item',
    'world.tmall.com/item',
    'detail.1688.com',
	'detail.tmall.hk/hk/item'
];

NHToolbar.prototype.setSidebarState = function(data)
{
    var instance = this;

    if (typeof this.sidebar.state === 'undefined' || this.sidebar.state === null) {
        this.sidebar.state = {website:"taobao.com"};
    }
    var oldState = this.sidebar.state;

    for (var i in data) {
        this.sidebar.state[i] = data[i];
    }

    if (this.sidebar.state.isShowContent) {
        HTMLUtil.select('.nhtq-sidebar-content').style.display = 'block';
    } else {
        this.sidebar.state.screen = false;
        HTMLUtil.select('.nhtq-sidebar-content').style.display = 'none';

        HTMLUtil.each(this.sidebar.buttons, function(element) {
            element.classList.remove('nh-selected');
        });
    }
    if (this.sidebar.state.screen) {
        var originScreen = this.sidebar.state.screen;
        if (this.sidebar.state.screen === 'user') {
            if (this.config.user === null) {
                this.sidebar.state.screen = 'login';
            }
        }

        HTMLUtil.each(this.sidebar.screens, function(screen) {
            screen.style.display = 'none';
        });
        var selected = HTMLUtil.select('.nhtq-sidebar-screen[data-screen="'+this.sidebar.state.screen+'"]');
        selected.style.display = 'block';

        HTMLUtil.select('.nhtq-sidebar-title').innerHTML = selected.getAttribute('data-screen-title');
        HTMLUtil.each(this.sidebar.buttons, function(btn) {
            if (btn.getAttribute('data-screen') === originScreen) {
                btn.classList.add('nh-selected');
            } else {
                btn.classList.remove('nh-selected');
            }
        });
    }
    if (typeof this.sidebar.state.website !== 'undefined' && this.sidebar.state.website !== null) {
        var elements = HTMLUtil.selectAll('.nhtq-select-website a');
        HTMLUtil.each(elements, function(element) {
            element.classList.remove('nh-selected');
        });

        HTMLUtil.select('.nhtq-select-website a[data-website="'+this.sidebar.state.website+'"]').classList.add('nh-selected');
    }
    if (typeof this.sidebar.state.searchResult !== 'undefined' && this.sidebar.state.searchResult !== null) {
        var html = '';
        if (this.sidebar.state.searchResult.length > 0) {
            for(i = 0; i < this.sidebar.state.searchResult.length; i++) {
                var word = this.sidebar.state.searchResult[i];
                html += '<div class="nh-search-item">' +
                            '<div class="nh-search-keyword">' +
                                '<a href="'+ HTMLUtil.getSearchUrl(this.sidebar.state.website, word.keyword_cn) +'" target="_blank">' +
                                word.keyword_label + '</a></div>' +
                        '</div>';
            }
        } else {
            html += '<div class="nh-search-item" style="color:#c00;">Kh\u00f4ng c\u00f3 k\u1ebft qu\u1ea3 n\u00e0o \u0111\u01b0\u1ee3c t\u00ecm th\u1ea5y.</div>';
        }
        HTMLUtil.select('#nhtqSearchResult').innerHTML = html;
    }
}

NHToolbar.prototype.render = function()
{
    var instance = this;
    console.log('===render===');
    HTMLUtil.get(nhtqConfig.apiDomain + 'page/addon_index/', function(res) {
        instance.sidebar = document.createElement('div');
        instance.sidebar.setAttribute('id', 'nhtqSideBar');
        instance.sidebar.innerHTML = res;

        var body = document.getElementsByTagName('body')[0];
        body.insertBefore(instance.sidebar, body.firstChild);
        HTMLUtil.fullHeight(instance.sidebar);
        HTMLUtil.fullHeight(HTMLUtil.select('.nhtq-sidebar-icons', instance.sidebar));

        //
        instance.sidebar.screens = HTMLUtil.selectAll('.nhtq-sidebar-screen', instance.sidebar);
        instance.sidebar.buttons = HTMLUtil.selectAll('.nh-sidebar-btn', instance.sidebar);
        //
        HTMLUtil.each(instance.sidebar.buttons, function(lnk) {
            lnk.onclick = function(event) {
                if (this.classList.contains('nh-selected')) {
                    instance.setSidebarState({isShowContent:false});
                    return false;
                }

                instance.setSidebarState({
                    isShowContent: true,
                    screen: lnk.getAttribute('data-screen')
                });
                return false;
            }
        });
        HTMLUtil.select('.nh-sidebar-close', instance.sidebar).onclick = function() {
            instance.setSidebarState({isShowContent:false});
            return false;
        };
        var elements = HTMLUtil.selectAll('.nhtq-select-website a');
        HTMLUtil.each(elements, function(element) {
            element.onclick = function() {
                instance.setSidebarState({website:this.getAttribute('data-website')});
                return false;
            };
        });
        var idxTimeout = null;
        var txtKeyword = HTMLUtil.select('#nhTxtKeyword');
        var patternNumberOnly = /^(\d+)$/;
        var btnViewItem = HTMLUtil.select('#nhBtnViewItem');
        HTMLUtil.addEvent(txtKeyword, 'keyup', function(event) {
            var keyword = txtKeyword.value.trim();
            if (patternNumberOnly.test(keyword)) {
                if (keyword.length >= 5) {
                    btnViewItem.style.display = 'block';
                    btnViewItem.onclick = function() {
                        var url = HTMLUtil.getItemUrl(instance.sidebar.state.website, keyword);
                        if (url !== null) {
                            window.open(url, '_blank');
                        }
                    }
                } else {
                    btnViewItem.style.display = 'none';
                }
                return;
            }
            if (idxTimeout !== null) {
                clearTimeout(idxTimeout);
            }
            idxTimeout = setTimeout(function() {
                HTMLUtil.get(nhtqConfig.apiDomain + 'autoComplete/search?term=' + encodeURIComponent(keyword), function(res) {
                    var words = JSON.parse(res);
                    instance.setSidebarState({searchResult: words});
                });
            }, 500);
        });

        instance.setSidebarState({website:instance.website});
		window.fbAsyncInit = function() {
		  FB.init({
			xfbml            : true,
			version          : 'v4.0'
		  });
		};

		(function(d, s, id) {
		var js, fjs = d.getElementsByTagName(s)[0];
		if (d.getElementById(id)) return;
		js = d.createElement(s); js.id = id;
		js.src = 'https://connect.facebook.net/en_US/sdk/xfbml.customerchat.js';
		fjs.parentNode.insertBefore(js, fjs);
	  }(document, 'script', 'facebook-jssdk'));		
    });
}

NHToolbar.prototype.renderItemInfo = function()
{
	console.log('===renderItemInfo===');
    switch (this.website) {
        case 'taobao.com':
			console.log('===renderItemInfoTaobao===');
            this.renderItemInfoTaobao();
            break;
        case 'tmall.com':
        case 'tmall.hk':
			console.log('===renderItemInfoTmall===');
            this.renderItemInfoTmall();
            break;
        case '1688.com':
        default:
			console.log('===renderItemInfo1688===');
            this.renderItemInfo1688();
            break;
    }

    // Add `add-to-cart` event
    var instance = this;
    var btnAddToCart = HTMLUtil.select('#nhtqBtnAddToCart');
    if (btnAddToCart) {
        btnAddToCart.onclick = function() {
            instance.addToCart();
        };
    }
    var btnLoveItem = HTMLUtil.select('#nhtqBtnLoveItem');
    if (btnLoveItem) {
        btnLoveItem.onclick = function() {
            if (!instance.config.user) {
                HTMLUtil.alert('Qu\u00fd kh\u00e1ch vui l\u00f2ng \u0111\u0103ng nh\u1eadp \u0111\u1ec3 c\u00f3 th\u1ec3 th\u00eam s\u1ea3n ph\u1ea9m v\u00e0o danh s\u00e1ch y\u00eau th\u00edch.', {parent:'#nhtqLoveMsg'});
                return;
            }
            var data = {
                objectId: instance.item.id,
                objectName: instance.item.title,
                objectType: 2,
                itemImages: instance.item.image,
                itemPrice: 0,
                siteName: instance.website,
                itemUrl: instance.item.url
            };
            HTMLUtil.post(nhtqConfig.apiDomain + 'favourite/add', {postData: data}, function(res) {
                HTMLUtil.alert(res.msg, {parent:'#nhtqLoveMsg', type: 'success'});
            });
        };
    }
    var btnLoveShop = HTMLUtil.select('#nhtqBtnLoveShop');
    if (btnLoveShop) {
        btnLoveShop.onclick = function() {
            if (!instance.config.user) {
                HTMLUtil.alert('Qu\u00fd kh\u00e1ch vui l\u00f2ng \u0111\u0103ng nh\u1eadp \u0111\u1ec3 c\u00f3 th\u1ec3 th\u00eam shop v\u00e0o danh s\u00e1ch y\u00eau th\u00edch.', {parent:'#nhtqLoveMsg'});
                return;
            }
            var data = {
                objectId: instance.shop.id,
                objectName: instance.shop.name,
                objectType: 1,
                siteName: instance.website,
                itemUrl: instance.shop.url
            };
            HTMLUtil.post(nhtqConfig.apiDomain + 'favourite/add', {postData: data}, function(res) {
                HTMLUtil.alert(res.msg, {parent:'#nhtqLoveMsg', type: 'success'});
            });
        };
    }
	

}

NHToolbar.prototype.renderItemInfo1688 = function()
{
    var html = this.getItemInfoHTML(this.item);
    var t = HTMLUtil.selectAll('.obj-order');
    if (t.length === 0) {
        t = HTMLUtil.selectAll('.order-action-container');
    }
	if (t.length === 0) {
		t = HTMLUtil.selectAll('.detail-affix-sku-wrapper');
	}
    var parent = null;
    if (t.length > 0) {
        parent = t[t.length - 1];
    }

    if (parent !== null) {
		var div = document.createElement('div');

		div.innerHTML = html;
		parent.appendChild(div);
        //parent.innerHTML = html;
        // Gán sự kiện vào các phần nhập số lượng đặt mua:
        var instance = this;
        instance.timeoutResourceId = null;

        var elements = HTMLUtil.selectAll('.mod-detail-purchasing .unit-detail-amount-control');
        if (elements.length < 1) {
            elements = HTMLUtil.selectAll('.obj-amount .unit-detail-amount-control');
        }
        if (elements.length < 1) {
            elements = HTMLUtil.selectAll('.spu-list-content .unit-detail-amount-control');
        }
        if (elements.length < 1) {

            elements = HTMLUtil.selectAll('.next-number-picker .next-input-group');
        }
        if (elements) {
			
            HTMLUtil.each(elements, function(element) {
				
                var amountInput = HTMLUtil.select('input', element);
                var buttonUp = HTMLUtil.selectAll('button', element);
				if (buttonUp.length < 2) {
					var buttonUp = HTMLUtil.selectAll('a', element);
				}
				//console.log('==buttonUp==');
				//console.log(buttonUp);
                buttonUp[0].onclick = buttonUp[1].onclick = amountInput.onkeyup = function() {
                    clearTimeout(instance.timeoutResourceId);
                    instance.timeoutResourceId = setTimeout(function() {
                        instance.updateSelectedSKU1688();
                    }, 500);
                }
            });
            instance.updateSelectedSKU1688();
        }
    }
}

NHToolbar.prototype.renderItemInfoTaobao = function()
{
	console.log('===item:',this.item);
    var html = this.getItemInfoHTML(this.item);
    var originButtonParent = HTMLUtil.select('#J_box_buycart');
    if (originButtonParent === null) {
        originButtonParent = HTMLUtil.select('#J_juValid');
    }
    if (originButtonParent) {
        // Insert giao diện đặt hàng
		console.log('===Insert addon===');
        //originButtonParent.innerHTML = '';
        var ele = HTMLUtil.select('#J_Title');
        // if (ele) {
            var div = document.createElement('div');
            div.innerHTML = html;
            originButtonParent.appendChild(div);
        // }
        // J_isSku
        var instance = this;
        instance.timeoutResourceId = null;
        var jskuAElements = HTMLUtil.selectAll('#J_SKU a');
        if (jskuAElements.length > 0) {
            for (var i = 0; i < jskuAElements.length; i++) {
                jskuAElements[i].onclick = function () {
                    clearTimeout(instance.timeoutResourceId);
                    instance.timeoutResourceId = setTimeout(function() {
                        instance.updateSelectedSKUTaobao();
                    }, 500);
                };
            }
        }

        var amountInput = HTMLUtil.select('#J_Stock input[type=text]');
        var buttonUp = HTMLUtil.selectAll('#J_Stock a');
        if (buttonUp !== null && buttonUp !== undefined && buttonUp.length > 0) {
            buttonUp[0].onclick = buttonUp[1].onclick = amountInput.onkeyup = function() {
                clearTimeout(instance.timeoutResourceId);
                instance.timeoutResourceId = setTimeout(function() {
                    instance.updateSelectedSKUTaobao();
                }, 500);
            };
        }

        instance.updateSelectedSKUTaobao();
    }
}

NHToolbar.prototype.renderItemInfoTmall = function()
{
    var html = this.getItemInfoHTML(this.item);
    var originButtonParent = HTMLUtil.select('.tb-action.tm-clear');
    if (originButtonParent) {
        // Insert giao diện đặt hàng
        // originButtonParent.innerHTML = '';
        // var ele = HTMLUtil.select('.tb-detail-hd');
        // if (ele) {
            var div = document.createElement('div');
            div.innerHTML = html;
            originButtonParent.appendChild(div);
        // }
        // J_isSku
        var instance = this;
        instance.timeoutResourceId = null;
        var jskuAElements = HTMLUtil.selectAll('.J_TSaleProp li a');
        if (jskuAElements.length > 0) {
            for (var i = 0; i < jskuAElements.length; i++) {
                jskuAElements[i].onclick = function () {
                    clearTimeout(instance.timeoutResourceId);
                    instance.timeoutResourceId = setTimeout(function() {
                        instance.updateSelectedSKUTmall();
                    }, 500);
                };
            }
        }
        //
        var amountInput = HTMLUtil.select('.tb-amount-widget input[type=text]');
        var buttonUp = HTMLUtil.selectAll('.mui-amount-btn span');
        if (buttonUp !== null && buttonUp !== undefined && buttonUp.length > 0) {
            buttonUp[0].onclick = buttonUp[1].onclick = amountInput.onkeyup = function() {
                clearTimeout(instance.timeoutResourceId);
                instance.timeoutResourceId = setTimeout(function() {
                    instance.updateSelectedSKUTmall();
                }, 500);
            };
        }

        instance.updateSelectedSKUTmall();
    }
}

NHToolbar.prototype.getItemInfoHTML = function(item) {
    var htmlPriceRange = '';
    if (this.website == '1688.com') {
        if (item.price_ranges !== null && item.price_ranges.length > 0) {
            var htmlTmpRange = '';
            for (var i = 0; i < item.price_ranges.length; i++) {
                var range = item.price_ranges[i];
                htmlTmpRange +=
                    '<div class="nhtq-price-range-item">' +
                    '<div class="nhtq-price-range-quantity mgr-btm-10">' + ((range.quantity_end !== null) ? (range.quantity_start + ' - ' + range.quantity_end) : ('&ge; ' + range.quantity_start)) + '</div>' +
                    '<div class="nhtq-price-range-price">' + HTMLUtil.formatMoney(range.price_vnd) + '\u0111</div>' +
                    '</div>';
            }

            htmlPriceRange =
                '<div class="nhtq-price-range">' +
                '<div class="nhtq-price-range-left">' +
                '<div class="lbl-quantity mgr-btm-10">S\u1ed1 l\u01b0\u1ee3ng:</div>' +
                '<div class="lbl-quantity">Gi\u00e1 b\u00e1n:</div>' +
                '</div>' +
                '<div class="nhtq-price-range-right">' +
                htmlTmpRange +
                '<div class="clrb"></div>' +
                '</div>' +
                '<div class="clrb"></div>' +
                '</div>';
        } else {
            htmlPriceRange =
                '<div class="nhtq-price-range">' +
                '<div class="nhtq-price-range-left">' +
                '<div class="lbl-quantity mgr-btm-10">S\u1ed1 l\u01b0\u1ee3ng:</div>' +
                '<div class="lbl-quantity">Gi\u00e1 b\u00e1n:</div>' +
                '</div>' +
                '<div class="nhtq-price-range-right">' +
                '<div class="nhtq-price-range-item">' +
                '<div class="nhtq-price-range-quantity mgr-btm-10">&ge;' + item.min_quantity + '</div>' +
                '<div class="nhtq-price-range-price" id="nhtqStdPrice">' + HTMLUtil.formatMoney(item.min_price_vnd) +
                ((item.max_price_vnd > 0)? (" - " + HTMLUtil.formatMoney(item.max_price_vnd)):"") +
                '\u0111</div>' +
                '</div>' +
                '<div class="clrb"></div>' +
                '</div>' +
                '<div class="clrb"></div>' +
                '</div>';
        }
    }

    var htmlShopInfo = '';
    if (this.shop && this.shop.name) {
        htmlShopInfo = '<tr><td colspan="2">Shop: <a href="'+this.shop.url+'" target="_blank">' + this.shop.name + '</a></td></tr>' +
            '<tr><td colspan="2"><div id="nhtqLoveMsg"></div><a href="'+this.shop.url+'" target="_blank" class="nhtq-love-item nhtq-go-to-shop">S\u1ea3n ph\u1ea9m c\u00f9ng shop</a> ' +
            '<a href="javascript:void(0)" id="nhtqBtnLoveShop" class="nhtq-love-item nhtq-love-shop">Y\u00eau th\u00edch shop</a> <a href="javascript:void(0)" id="nhtqBtnLoveItem" class="nhtq-love-item">Y\u00eau th\u00edch s\u1ea3n ph\u1ea9m</a>' +
            '</td></tr>';
    }

    var html =
        '<div class="nhtq-item-info">' +
        '<div class="nhtq-box-title">'+nhtqConfig.Domain+'</div>' +
            htmlPriceRange + // Khoảng giá nếu có
        '<div class="nhtq-item-detail" style="padding:10px;">' +
        '<table border="1" class="nhtq-table-item-detail">' +
        '<tbody>' + htmlShopInfo +
        '<tr>'+
		'<td>M\u00e3 s\u1ea3n ph\u1ea9m: <span class="text-red">' + item.id + '</span></td>' +
		'<td>T&#7927; gi&aacute;: <span class="text-red">' + this.config.config.exchange_rate + '</span></td>' +
		'</tr>'+
        '<tr>' +
        '<td width="50%">\u0110\u00e3 ch\u1ecdn: <span class="text-item-price text-red" id="nhtqSelectedQuantity">0</span></td>' +
        '<td>Th\u00e0nh ti\u1ec1n: <span class="text-item-price text-red" id="nhtqSelectedSubtotal">0\u0111</span></td>' +
        '</tr>' +
        '<tr>' +
        '<td colspan="2"><div id="nhtqOrderMsg">' +
        '<textarea id="item_note" name="item_note" rows="4" cols="50" placeholder="ghi ch&uacute; s&#7843;n ph&#7849;m" style="width:100%;"></textarea>' +
        '</div><div class="nhtq-item-btn-order"><a href="javascript:void(0)" id="nhtqBtnAddToCart"></a></div></td>' +
        '</tr>' +
        '</tbody></table>' +
        '<div class="text-notice clrb">Qu\u00fd kh\u00e1ch vui l\u00f2ng ch\u1ecdn \u0111\u1ea7y \u0111\u1ee7 th\u00f4ng tin s\u1ea3n ph\u1ea9m \u0111\u1ec3 xem gi\u00e1 chu\u1ea9n.</div>' +
        '</div>' +
        '<div class="nhtq-box-footer" style="text-align:left;padding:5px 10px;">' +
        '<strong>L\u01b0u \u00fd: </strong><br>' +
        'S\u1ea3n ph\u1ea9m y\u00eau c\u1ea7u \u0111\u1eb7t mua s\u1ed1 l\u01b0\u1ee3ng t\u1ed1i thi\u1ec3u l\u00e0: ' + this.item.min_quantity + '<br>' +
        'Qu\u00fd kh\u00e1ch vui l\u00f2ng kh\u00f4ng s\u1eed d\u1ee5ng Google Translate khi \u0111\u1eb7t h\u00e0ng.' +
        '</div>' +
        '</div>';

    return html;
}

NHToolbar.prototype.getItemStruct = function() {

    return {
        "id": null,
        "title": null,
        "website": this.getWebsite(),
        "url": window.location.href,
        "image": null,
        "min_price": 0,
        "max_price": 0,
        "min_price_vnd": 0,
        "max_price_vnd": 0,
        "ws_rule_number": 1,
        "min_quantity": 1,
        "price_ranges": null,
        "weight": 0,
        "shop_id": null,
        "shop_name": null,
        "shop_address": null,
    }
}



NHToolbar.prototype.getItemInfo = function() {
	console.log('==getItemInfo==');
    if (this.isItemDetailPage()) {
        switch(this.website) {
            case "1688.com":
                return this.getItemInfo1688();
            case "taobao.com":
                return this.getItemInfoTaobao();
                break;
            case "tmall.com":
            case "tmall.hk":
                return this.getItemInfoTmall();
                break;
        }
    }
	console.log('this is not item link...');
    return null;
}

NHToolbar.prototype.getItemInfo1688 = function() {
	console.log('==getItemInfo1688==',typeof iDetailConfig);
    var item = this.getItemStruct();
    // Khoảng giá
    item.price_ranges = [];
    var price_ranges = [];
	
    // Mã sản phẩm
	var dataObj = null;
	if (typeof iDetailConfig === 'undefined') {
		var dataObj = window.__INIT_DATA.data;
		var originButtonParent = HTMLUtil.select('.layout-right');
		keyObj = Object.keys(dataObj).find(key => dataObj[key].componentType === '@ali/tdmod-od-pc-offer-price')
		console.log('====',keyObj);
		var INIT_DATA = dataObj[keyObj].data.offerDomain
		INIT_DATA = JSON.parse(INIT_DATA).tradeModel;
		// Insert giao diện đặt hàng
		// originButtonParent.innerHTML = '';
		// var ele = HTMLUtil.select('.tb-detail-hd');
		// if (ele) {
		
		//var div = document.createElement('div');
		//div.innerHTML =  Object.keys(INIT_DATA)//JSON.stringify(INIT_DATA)//Object.keys(INIT_DATA);
		//originButtonParent.appendChild(div);
	}
	
	
	var htmlSite = document.getElementsByTagName('html')[0].innerHTML;
	console.log('===b2c_auction===',htmlSite.match('&b2c_auction=(.+?)&')[1]);
	item.id = htmlSite.match('&b2c_auction=(.+?)&')[1];

	item.title = HTMLUtil.select('title').innerHTML;
	var elImage = HTMLUtil.select('.mod-detail-gallery img');
	if (elImage === null || typeof elImage === 'undefined') {
		elImage = HTMLUtil.select('.mod-detail-version2018-gallery .tab-pane .box-img img');
	}
	if (elImage === null || typeof elImage === 'undefined') {
		elImage = HTMLUtil.selectAll('.detail-gallery-img')[1];
	}	
	if (elImage !== null && typeof elImage !== 'undefined') {
		item.image = elImage.src;
	}
	
	var itemInfoArea = HTMLUtil.select('.mod-detail-purchasing');
	if (itemInfoArea !== null && typeof itemInfoArea !== 'undefined') {
		var modConfig = itemInfoArea.getAttribute('data-mod-config');
		if (modConfig !== undefined && modConfig !== null && modConfig) {
			modConfig = JSON.parse(modConfig);

			if (modConfig.wsRuleNum !== undefined && modConfig.wsRuleNum !== "") {
				var wsRuleNum = parseInt(modConfig.wsRuleNum);

				if (!isNaN(wsRuleNum)) {
					item.ws_rule_number = wsRuleNum;
				}
			}

			if (modConfig.min !== undefined && modConfig.min !== "") {
				var minQty = parseInt(modConfig.min);

				if (!isNaN(item.ws_rule_number)) {
					item.min_quantity = minQty;
				}
			}
		}
	}	
	if (typeof iDetailConfig !== 'undefined') {
		if (iDetailData.sku !== undefined && iDetailData.sku.price !== undefined) {
			var arrPrice = iDetailData.sku.price.split("-");
			item.min_price = parseFloat(arrPrice[0].replace(",", "."));
			item.min_price_vnd = this.rmbToVnd(item.min_price);
			if (arrPrice.length > 1) {
				item.max_price = parseFloat(arrPrice[1].replace(",", "."));
				item.max_price_vnd = this.rmbToVnd(item.max_price);
			}
		}		
		if (iDetailData.sku !== undefined && iDetailData.sku.priceRange !== undefined) {
			for (var i = 0, len = iDetailData.sku.priceRange.length; i < len; i++) {
				var range = iDetailData.sku.priceRange[i];
				var nextRange = (i < len - 1) ? iDetailData.sku.priceRange[i+1] : null;
				price_ranges.push({
					'quantity_start': range[0],
					'quantity_end': (nextRange != null) ? (nextRange[0] - 1) : null,
					'price': range[1],
					'price_vnd': this.rmbToVnd(range[1])
				});
			}
		}
		else {
			var elementPriceTd = HTMLUtil.selectAll('#mod-detail-price .d-content .price td');
			if (elementPriceTd && elementPriceTd.length > 0) {
				for (var i = 0; i < elementPriceTd.length; i++) {
					var range = elementPriceTd[i].getAttribute('data-range');
					if (range !== undefined && range !== null) {
						range = JSON.parse(range);
						if (typeof range.price !== 'undefined') {
							var prc = parseFloat(range.price.replace(",", "."));
							price_ranges.push({
								'quantity_start': range.begin,
								'quantity_end': (range.end != "") ? range.end : null,
								'price': prc,
								'price_vnd': this.rmbToVnd(prc)
							});
						}
					}
				}
			} else {
				elementPriceTd = HTMLUtil.select('.d-content .obj-price .price-now');
				if (elementPriceTd) {
					var prc = parseFloat(elementPriceTd.innerHTML);
					price_ranges.push({
						'quantity_start': 1,
						'quantity_end': null,
						'price': prc,
						'price_vnd': this.rmbToVnd(prc)
					});
				}
			}
		}
		if ((iDetailConfig && (iDetailConfig.isRangePriceSku === "true" || iDetailConfig.isRangePriceSku === true || iDetailConfig.isSKUOffer === "false"))
			|| price_ranges.length > 1
		) {
			item.price_ranges = price_ranges;
		}		
		
	} else if (typeof dataObj !== 'undefined' && dataObj !== null){
		keyObj = Object.keys(dataObj).find(key => dataObj[key].componentType === '@ali/tdmod-od-pc-offer-price');
		var INIT_DATA = dataObj[keyObj].data.offerDomain
		var tradeModel = JSON.parse(INIT_DATA).tradeModel;
		console.log(tradeModel);
		if (tradeModel.beginAmount !== undefined && tradeModel.beginAmount !== "") {
			var minQty = parseInt(tradeModel.beginAmount);
			item.ws_rule_number = minQty;
			item.min_quantity = minQty;

		}		
		if (tradeModel.minPrice !== undefined && tradeModel.minPrice !== "") {
			var minPrice = parseFloat(tradeModel.minPrice.replace(",", "."));
			item.min_price = minPrice;
			item.min_price_vnd = this.rmbToVnd(item.min_price);

		}
		if (tradeModel.maxPrice !== undefined && tradeModel.maxPrice !== "") {
			var maxPrice = parseFloat(tradeModel.maxPrice.replace(",", "."));
			item.max_price = maxPrice;
			item.max_price_vnd = this.rmbToVnd(item.max_price);
		}
		
		if (tradeModel.disPriceRanges !== undefined && tradeModel.disPriceRanges !== ""){
			var disPriceRanges = tradeModel.disPriceRanges;
			console.log('==disPriceRanges==');
			console.log(disPriceRanges);
			for (var i = 0; i < disPriceRanges.length; i++) {
				var priceRanges = disPriceRanges[i];
				console.log('==priceRanges==');
				console.log(priceRanges);
				if (typeof priceRanges.discountPrice !== 'undefined') {
					var prc = parseFloat(priceRanges.discountPrice.replace(",", "."));
					price_ranges.push({
						'quantity_start': priceRanges.beginAmount,
						'quantity_end': (priceRanges.endAmount != 0) ? priceRanges.endAmount : null,
						'price': prc,
						'price_vnd': this.rmbToVnd(prc)
					});
					console.log('==priceRanges==');
					console.log(price_ranges);
				}				

			}
			if (price_ranges.length > 0){
				item.price_ranges = price_ranges;
			}
		}
	}
	console.log(item);
    return item;
}

NHToolbar.prototype.getItemInfoTaobao = function() {
	console.log('==getItemInfoTaobao==');
    var te = HTMLUtil.select('.operation #buy a');
    if (te) {
        te.innerText = 'Xem chi ti\u1ebft v\u00e0 mua h\u00e0ng';
        return;
    }

    var item = this.getItemStruct();
    var titleSelector = '.tb-main-title .t-title';
    var imageSelector = '.tb-thumb-content img'
    if (this.hostname === 'item.taobao.com') {
        titleSelector = '.tb-main-title';
        imageSelector = '.tb-booth img';
    }
    item.title = HTMLUtil.select(titleSelector).innerText.trim();
    item.image = HTMLUtil.select(imageSelector).src;

    if (g_config !== undefined) {
        if (g_config.itemId !== undefined) {
            item.id = g_config.itemId;
        }
    }
	console.log('getItem:',item)
    return item;
};
NHToolbar.prototype.getItemInfoTmall = function() {
    var item = this.getItemStruct();
    item.title = HTMLUtil.select('#detail .tb-detail-hd h1').innerText;
    item.image = HTMLUtil.select('#detail .tb-booth img').src;
    if (g_config !== undefined) {
        if (g_config.itemId !== undefined) {
            item.id = g_config.itemId;
        }
    }

    return item;
};
NHToolbar.prototype.shopInfoTags1688 = ['.company-name a','.logoName a', '.smt-info a.name', '.content .abstract .company .name'];
NHToolbar.prototype.getShopInfo = function() {
    var shop = {
        id: "",
        name: "",
        address: "",
        url: ""
    };

    var lnkToShop = null;

    if (this.website === '1688.com') {

        for(var ix in this.shopInfoTags1688)
        {
            lnkToShop = HTMLUtil.select(this.shopInfoTags1688[ix]);
            if (lnkToShop) {
                break;
            }
        }
        // lnkToShop = HTMLUtil.select('.company-name a');
        // if (!lnkToShop) {
        //     lnkToShop = HTMLUtil.select('.smt-info a.name');
        // }
		console.log('===lnkToShop===');
		//console.log(lnkToShop);
		//meta[name="description"]
        if (lnkToShop !== null) {
            shop.name = lnkToShop.innerText;
            shop.url = lnkToShop.href;
            shop.id = shop.url.replace("http://", "").replace("https://", "").split("/")[0].split('.')[0];
        }else {
			lnkToShop = HTMLUtil.select('meta[property="og:product:nick"]');
			if (lnkToShop!== null) {
				shop.name = lnkToShop.content.split(';')[0].trim().replace('name=','');
				shop.url = lnkToShop.content.split(';')[1].trim().replace('url=','https:');
				shop.id = shop.url.replace("http://", "").replace("https://", "").split("/")[0].split('.')[0];				
			} else if (typeof window.__INIT_DATA.data !== 'undefined') {
				console.log('===get shop new===')
				var dataObj = window.__INIT_DATA.data;
				keyObj = Object.keys(dataObj).find(key => dataObj[key].componentType === '@ali/tdmod-od-pc-offer-price')
				console.log('====',keyObj);
				var INIT_DATA = dataObj[keyObj].data.offerDomain
				INIT_DATA = JSON.parse(INIT_DATA).sellerModel;
				shop.name = INIT_DATA.companyName;
				shop.url = INIT_DATA.winportUrl;
				shop.id = shop.url.replace("http://", "").replace("https://", "").split("/")[0].split('.')[0];					
			}
		}
        // Shop address
        var dElement = HTMLUtil.select('.delivery-detail .delivery-addr');
        if (dElement !== undefined && dElement && dElement.innerHTML) {
            var addr = dElement.innerHTML.split(" ");
            if (addr.length > 0) {
                shop.address = addr[0];
            }
        }
        if (shop.url) {
            shop.url = 'https://' + shop.id + '.1688.com/page/offerlist.htm';
        }
    } else if(this.website === 'taobao.com') {
        if (this.hostname === 'item.taobao.com') {
            if (g_config && g_config.shopName !== undefined) {
                shop.name = g_config.shopName;
                shop.url = 'https:' + g_config.idata.shop.url;
                if (typeof g_config !== 'undefined' && typeof g_config.shopId !== 'undefined') {
                    shop.id = 'shop' + g_config.shopId;
                } else {
                    shop.id = shop.url.replace("http://", "").replace("https://", "").split("/")[0].split('.')[0];
                }
            }
        } else {
            lnkToShop = HTMLUtil.select('.shop-info .tb-shop-name a');
            if (lnkToShop) {
                shop.name = lnkToShop.innerHTML;
                shop.url = lnkToShop.href;
                shop.id = shop.url.replace("http://", "").replace("https://", "").split("/")[0].split('.')[0];
            }
        }
        if (shop.url) {
            shop.url = 'https://' + shop.id + '.taobao.com/search.htm';
        }
        var addrTags = ['#J_LogisticInfo .tb-location em', '#J_WlAreaInfo #J-From'];
        for(var i = 0; i < addrTags.length; i++) {
            var addrTag = HTMLUtil.select(addrTags[i]);
            if (typeof addrTag !== 'undefined' && addrTag !== null) {
                var sa = addrTag.innerHTML.trim();
                if(sa !== '') {
                    shop.address = sa.substring(0,2);
                    break;
                }
            }
        }
    } else if (this.website === "tmall.com" || this.website === "tmall.hk") {
        if (g_config !== undefined && g_config !== null)
        {
            if (g_config.shopId !== undefined && g_config.shopId !== null)
            {
                shop.name = decodeURIComponent(g_config.sellerNickName);
                shop.url = 'https:' + g_config.shopUrl;
                shop.id = shop.url.replace("http://", "").replace("https://", "").split("/")[0].split('.')[0];
            }
        }
        if (shop.url) {
            shop.url = 'https://' + shop.id + '.tmall.com/search.htm';
        }
        var addrInput = HTMLUtil.select('input[name=region]');
        if (typeof addrInput !== 'undefined' && addrInput !== null) {
            var sa = addrInput.value;
            if (sa !== '') {
                shop.address = sa.substring(0,2);
            }
        }
    }

    return shop;
}

NHToolbar.prototype.priceTag = {
    "taobao.com": [
        "#J_PromoPriceNum", "#J_PromoPrice .tb-rmb-num", "#J_priceStd .tb-rmb-num", "#J_StrPrice .tb-rmb-num"
    ]
};

NHToolbar.prototype.updateSelectedSKU1688 = function() {
    this.selectedQuantity = 0;
    this.subtotal = 0;
    console.log("===updateSelectedSKU1688===");
	if (typeof iDetailConfig !== 'undefined') {
		if (iDetailConfig.isSKUOffer === "true") {
			if (iDetailData.sku !== undefined && iDetailData.sku.skuMap !== undefined) {
				var selectedSku = [];
				var isPriceEmpty = false;
				for (var i in iDetailData.sku.skuMap) {
					var s = iDetailData.sku.skuMap[i];
					var amount = 0;
					if (typeof s.amount === 'undefined' && typeof s.amountValue !== 'undefined') {
						amount = parseInt(s.amountValue);
					} else if (typeof s.amount !== 'undefined') {
						amount = parseInt(s.amount);
					}
					if (amount !== 0) {
						// console.log(i + " -> " + amount);
						var si = {
							"name": i,
							"quantity": amount
						};
						if (typeof s.price === 'string') {
							s.price = parseFloat(s.price.replace(",", "."));
						}

						if (typeof s.discountPrice === 'string') {
							s.discountPrice = parseFloat(s.discountPrice.replace(",", "."));
						}

						if (typeof s.discountPrice !== 'undefined') {
							if (typeof s.price === 'undefined' || s.discountPrice <= s.price) {
								si.price = s.discountPrice;
							}
						} else if (typeof s.price !== 'undefined') {
							si.price = s.price;
						} else { // Không có price và priceDiscount
							isPriceEmpty = true;
						}
						si.price_vnd = this.rmbToVnd(si.price);
						
						if (iDetailData.sku.skuProps !== undefined && iDetailData.sku.skuProps.length > 0) {
							var arrName = si.name.split('&gt;');

							for (var idx = 0; idx < arrName.length; idx++) {
								if (iDetailData.sku.skuProps[idx] !== undefined) {
									for (var pi = 0; pi < iDetailData.sku.skuProps[idx].value.length; pi++) {
										if (iDetailData.sku.skuProps[idx].value[pi].name !== undefined
											&& arrName[idx] === iDetailData.sku.skuProps[idx].value[pi].name) {
											if (iDetailData.sku.skuProps[idx].value[pi].imageUrl !== undefined) {
												si.image = iDetailData.sku.skuProps[idx].value[pi].imageUrl;
											}
										}
									}
								}
							}
						}

						selectedSku.push(si);
						this.selectedQuantity += si.quantity;
						this.subtotal += (si.price_vnd * si.quantity);
					}
				}

				if (isPriceEmpty && typeof this.item !== 'undefined'
					&& typeof this.item.price_ranges !== 'undefined'
					&& this.item.price_ranges.length > 0) {
					var tmpPrice = 0, tmpPriceVnd = 0;
					for (var i = 0; i < this.item.price_ranges.length; i++) {
						if (this.item.price_ranges[i].quantity_start <= this.selectedQuantity
						&& this.item.price_ranges[i].quantity_end >= this.selectedQuantity) {
							tmpPrice = parseFloat(this.item.price_ranges[i].price.replace(",", "."));
							tmpPriceVnd = this.rmbToVnd(tmpPrice);
						}
					}
					if (tmpPrice > 0) {
						// console.log('Tmp Price: ' + tmpPrice);
						this.subtotal = 0;
						for (var i = 0; i < selectedSku.length; i ++) {
							selectedSku[i].price = tmpPrice;
							selectedSku[i].price_vnd = tmpPriceVnd;
							this.subtotal += (selectedSku[i].price_vnd * selectedSku[i].quantity);
						}
					}
				}

				this.sku = selectedSku;

				HTMLUtil.select('#nhtqSelectedQuantity').innerHTML = HTMLUtil.formatMoney(this.selectedQuantity);
				HTMLUtil.select('#nhtqSelectedSubtotal').innerHTML = HTMLUtil.formatMoney(this.subtotal) + '\u0111';
			}
		} else {
			var element = HTMLUtil.select('.obj-amount .unit-detail-amount-control .amount-input');
			if (element) {
				// Select price from range
				var price = 0;
				var quantity = parseInt(element.value);
				if (this.item.price_ranges != null && this.item.price_ranges.length > 0) {
					for (var i = 0; i < this.item.price_ranges.length; i++) {
						if (quantity >= this.item.price_ranges[i].quantity_start) {
							price = this.item.price_ranges[i].price;
						}
					}

				}
				var si = {
					"name": "",
					"quantity": quantity,
					"price": price,
					"price_vnd": this.rmbToVnd(price)
				};
				this.sku = [];
				this.sku.push(si);
				this.selectedQuantity += quantity;
				this.subtotal += (si.price_vnd * quantity);

				HTMLUtil.select('#nhtqSelectedQuantity').innerHTML = HTMLUtil.formatMoney(this.selectedQuantity);
				HTMLUtil.select('#nhtqSelectedSubtotal').innerHTML = HTMLUtil.formatMoney(this.subtotal) + '\u0111';
			}
		}		
	} else {
		
		var price = 0;
		var totalQuantity = 0
		var skuItems = [];
		this.sku = [];	
		// get ImageObj
		myImageObj = new Object();
		var elementsWrappers = HTMLUtil.selectAll('.prop-item-inner-wrapper');
		if (elementsWrappers.length > 0) {
			console.log('==elementsWrappers==');
			for (var i = 0; i < elementsWrappers.length; i++) {
				var elementsWrapper = elementsWrappers[i];
				var elementsTotal = HTMLUtil.select('.prop-item-total', elementsWrapper);
				if (elementsTotal != null){
					//totalQuantity += parseInt(elementsTotal.innerHTML.replace('x',''));
					var nameElement = HTMLUtil.select('.prop-name', elementsWrapper);
					
					var imageElement = HTMLUtil.select('.prop-img', elementsWrapper)
					if (imageElement !== null){
						var imageValue = imageElement.style.backgroundImage.replace('url("','').replace('")','');
					}
					else {
						var imageValue = this.item.image;
					}
					//console.log(imageValue,nameElement.innerHTML,parseInt(elementsTotal.innerHTML.replace('x','')));
					var nameSelected = nameElement.innerText;
					myImageObj[nameSelected] = imageValue
				}					
			}
		}
		else {
			var elements = HTMLUtil.selectAll('.sku-item-wrapper');
			for (var i = 0; i < elements.length; i++) {
				var element = elements[i];
				var inputElements = HTMLUtil.select('.next-number-picker .next-input-group input', element)
				if (inputElements != null){
					if (parseInt(inputElements.value) > 0){
						//totalQuantity += parseInt(inputElements.value);
						var nameElement = HTMLUtil.select('.sku-item-name', element)
						var discountPriceElements = HTMLUtil.select('.discountPrice-price', element)
						var imageElements = HTMLUtil.select('.sku-item-image', element)
						var discountPrice = parseFloat(discountPriceElements.innerText.replace('元',''))
						var nameSelected = nameElement.innerText;
						if (imageElements !== null && imageElements !== 'undefined'){
							var imageValue = imageElements.style.backgroundImage.replace('url("','').replace('")','');		
							myImageObj[nameSelected] = imageValue
						} 
						else {
							var imageValue = this.item.image;		
							myImageObj[nameSelected] = imageValue;							
						}
					}			
				}
			}				
		
		}
		
		// Click selected items and get data;
		var dataObj = window.__INIT_DATA.data;
		keyObj = Object.keys(dataObj).find(key => dataObj[key].componentType === '@ali/tdmod-od-pc-offer-price')
		console.log('====',keyObj);
		var INIT_DATA = dataObj[keyObj].data.offerDomain
		var tradeModel = JSON.parse(INIT_DATA).tradeModel;
		var skuMap = tradeModel.skuMap;
		console.log('==skuMap==')
		console.log(skuMap)

		var selectButton = HTMLUtil.select('.order-has-select-button');
		var selectedElements = HTMLUtil.selectAll('.selected-item-wrapper');
		
		if (selectButton != null && selectedElements.length === 0){
			selectButton.click();
			var selectedElements = HTMLUtil.selectAll('.selected-item-wrapper');
		}


		for (var i = 0; i < selectedElements.length; i++) {
			var elementSelected = selectedElements[i];
			var childrenName = HTMLUtil.select('.name', elementSelected);
			var childrenWrappers = HTMLUtil.selectAll('.children-wrapper', elementSelected);
			var itemName = childrenName.innerText;
			if (Object.keys(myImageObj).length !== 0) {
				console.log('==childrenNameImage==');
				console.log(myImageObj[childrenName.innerText]);
				var itemImage = myImageObj[childrenName.innerText];				
			} 
			else {
				var itemImage = this.item.image;
			} 

			for (var ii = 0; ii < childrenWrappers.length; ii++) {
				var childrenWrapper = childrenWrappers[ii];
				console.log('==childrenWrapper==',childrenWrapper);
				
				var childrenWrapperName = HTMLUtil.select('.children-wrapper-name', childrenWrapper);
				var itemWrapper = childrenWrapper.innerText;
				console.log('==childrenWrapperName==',childrenWrapperName.title);
				var itemProperties = childrenWrapperName.title
				var itemQuantity = itemWrapper.split('(').pop().trim().replace(')','')
				if (itemProperties.length === 0) {
					var itemNameProperties = itemName;	
				}
				else {
					var itemNameProperties = itemName +'&gt;'+itemProperties;
				}
				totalQuantity += parseInt(itemQuantity);
				console.log('==itemNameProperties==',itemNameProperties);
				let objItem = skuMap.find(o => o.specAttrs === itemNameProperties);
				if ('discountPrice' in objItem) {
					var itemPrice = parseFloat(objItem.discountPrice);
					var si = {
						'name':itemNameProperties.replace('&gt;','>'),
						'image':itemImage,
						'quantity':itemQuantity,
						'price':itemPrice,
						'price_vnd':this.rmbToVnd(itemPrice)
					};
					this.sku.push(si);					
				}
				else {
					var si = {
						'name':itemNameProperties.replace('&gt;','>'),
						'image':itemImage,
						'quantity':itemQuantity,
					};
					skuItems.push(si);					
				}
			}	

		}
		var selectedElements = HTMLUtil.selectAll('.selected-item-wrapper');
		if (selectButton != null && selectedElements.length !== 0){
			selectButton.click();
		}
		//check price_ranges
		if (this.item.price_ranges != null && this.item.price_ranges.length > 0) {
			for (var i = 0; i < this.item.price_ranges.length; i++) {
				if (totalQuantity >= this.item.price_ranges[i].quantity_start) {
					price = this.item.price_ranges[i].price;
				}
			}

		} 
		// append to sku array;
		for (var i = 0; i < skuItems.length; i++) {
			var lineSku = skuItems[i];
			var newSKU = {
			"name": lineSku.name,
			"image": lineSku.image,
			"quantity": lineSku.quantity,
			"price": price,
			"price_vnd": this.rmbToVnd(price)
			};	
			this.sku.push(newSKU);
		}			


		this.selectedQuantity += totalQuantity;
		this.subtotal += (this.rmbToVnd(price) * totalQuantity);

		HTMLUtil.select('#nhtqSelectedQuantity').innerHTML = HTMLUtil.formatMoney(this.selectedQuantity);
		HTMLUtil.select('#nhtqSelectedSubtotal').innerHTML = HTMLUtil.formatMoney(this.subtotal) + '\u0111';
	}
	

}

NHToolbar.prototype.updateSelectedSKUTaobao = function() {
    this.selectedQuantity = parseInt(HTMLUtil.select('#J_IptAmount').value);
    this.subtotal = 0;

    var price = 0;
    var ele = null;
    for (var i = 0; i < this.priceTag["taobao.com"].length; i++) {
        ele = HTMLUtil.select(this.priceTag["taobao.com"][i]);
        if (ele !== null && typeof ele !== 'undefined') {
            break;
        }
    }
    if (ele !== null) {
        var str = ele.innerText.replace("¥", "").trim();
        price = parseFloat(str.replace(",", "."));
    }

    var priceVnd = this.rmbToVnd(price);

    // Selected SKU
    this.sku = [];
    var elementJSKU = (this.hostname == 'item.taobao.com')
        ? HTMLUtil.selectAll('.J_Prop.tb-prop')
        : HTMLUtil.selectAll('#J_SKU dl');

    if (elementJSKU !== null && elementJSKU.length > 0) {
        var selectedProperties = (this.hostname == 'item.taobao.com')
            ? HTMLUtil.selectAll('.J_Prop.tb-prop .tb-selected a')
            : HTMLUtil.selectAll('#J_SKU dl .tb-selected a');
        if (selectedProperties !== null
            && selectedProperties !== undefined
            && selectedProperties.length == elementJSKU.length) {
            var tmpSkuName = [];
            var img = "";
            for (var i = 0; i < selectedProperties.length; i++) {
                if (this.hostname == 'item.taobao.com') {
                    tmpSkuName.push(HTMLUtil.select('span', selectedProperties[i]).innerText.trim());
                } else {
                    tmpSkuName.push(selectedProperties[i].getAttribute('title').trim());
                }

                // Ảnh của SKU.
                if (selectedProperties[i].style !== undefined
                    && selectedProperties[i].style !== null
                    && selectedProperties[i].style.backgroundImage !== null
                    && selectedProperties[i].style.backgroundImage.length != "") {

                    img = selectedProperties[i].style.backgroundImage.slice(4, -1).replace(/"/g, "").replace("30x30", "400x400").trim();
                }
            }
            this.sku.push({
                "name": tmpSkuName.join(" ; "),
                "quantity": this.selectedQuantity,
                "price": price,
                "price_vnd": priceVnd,
                "image": img
            });
        }
    } else {
        this.sku.push({
            "name": "",
            "quantity": this.selectedQuantity,
            "price": price,
            "price_vnd": priceVnd
        });
    }
    
    this.subtotal = priceVnd * this.selectedQuantity;

    var ele = HTMLUtil.select('#nhtqStdPrice');
    if (typeof ele !== 'undefined' && ele !== null) {
        ele.innerHTML = HTMLUtil.formatMoney(priceVnd) + '\u0111';
    }

    HTMLUtil.select('#nhtqSelectedQuantity').innerHTML = HTMLUtil.formatMoney(this.selectedQuantity);
    HTMLUtil.select('#nhtqSelectedSubtotal').innerHTML = HTMLUtil.formatMoney(this.subtotal) + '\u0111';
}

NHToolbar.prototype.updateSelectedSKUTmall = function() {
    if (this.shop == null || this.shop.id == "") {
        this.shop = this.getShopInfo();
    }

    this.selectedQuantity = parseInt(HTMLUtil.select('.tb-text.mui-amount-input').value);
    this.subtotal = 0;

    var price = 0;

    var priceElement = HTMLUtil.select('.tm-promo-price .tm-price');
    if (typeof priceElement === 'undefined' || priceElement === null) {
        priceElement = HTMLUtil.select('#J_StrPriceModBox .tm-price');
    }

    if (typeof priceElement !== 'undefined' && priceElement !== null) {
        price = parseFloat(priceElement.innerText.trim().replace(",", "."));
    }

    var priceVnd = this.rmbToVnd(price);

    // Selected SKU
    this.sku = [];
    var elementJSKU = HTMLUtil.selectAll('.tb-sku .tb-prop.tm-sale-prop');

    if (elementJSKU !== null && elementJSKU.length > 0) {
        var selectedProperties = HTMLUtil.selectAll('.tb-sku .tb-prop .tb-selected a');
        if (selectedProperties !== null
            && selectedProperties !== undefined
            && selectedProperties.length == elementJSKU.length) {

            var tmpSkuName = [];
            var img = "";
            for (var i = 0; i < selectedProperties.length; i++) {
                tmpSkuName.push(selectedProperties[i].innerText.trim());

                // Ảnh của SKU.
                if (selectedProperties[i].style !== undefined
                    && selectedProperties[i].style !== null
                    && selectedProperties[i].style.backgroundImage !== null
                    && selectedProperties[i].style.backgroundImage.length != "") {

                    img = selectedProperties[i].style.backgroundImage.slice(4, -1).replace(/"/g, "").replace("40x40", "400x400").trim();
                }
            }
            this.sku.push({
                "name": tmpSkuName.join(" ; "),
                "quantity": this.selectedQuantity,
                "price": price,
                "price_vnd": priceVnd,
                "image": img
            });
        }
    } else {
        this.sku.push({
            "name": "",
            "quantity": this.selectedQuantity,
            "price": price,
            "price_vnd": priceVnd
        });
    }

    this.subtotal = priceVnd * this.selectedQuantity;
    var ele = HTMLUtil.select('#nhtqStdPrice');
    if (typeof ele !== 'undefined' && ele !== null) {
        ele.innerHTML = HTMLUtil.formatMoney(priceVnd) + '\u0111';
    }

    HTMLUtil.select('#nhtqSelectedQuantity').innerHTML = HTMLUtil.formatMoney(this.selectedQuantity);
    HTMLUtil.select('#nhtqSelectedSubtotal').innerHTML = HTMLUtil.formatMoney(this.subtotal) + '\u0111';
}


NHToolbar.prototype.addToCart = function() {
    HTMLUtil.alert("\u0110ang x\u1eed l\u00fd...", {parent:'#nhtqOrderMsg', type:'info'});

    if (this.website === '1688.com') {
        this.updateSelectedSKU1688();
    } else if (this.website === 'taobao.com') {
        this.updateSelectedSKUTaobao();
    } else if (this.website === 'tmall.com' || this.website === 'tmall.hk') {
        this.updateSelectedSKUTmall();
    } else {
        HTMLUtil.alert("Kh\u00f4ng x\u00e1c \u0111\u1ecbnh \u0111\u01b0\u1ee3c website b\u00e1n h\u00e0ng.");
        return;
    }
    if (this.shop.address === "") {
        this.shop = this.getShopInfo();
    }

    if (typeof this.sku !== 'undefined' && this.sku !== null && this.sku.length > 0 && this.selectedQuantity >= this.item.min_quantity) {
        for(var i = 0; i < this.sku.length; i++) {
            if (typeof this.sku[i].image !== 'undefined' && this.sku[i].image && this.sku[i].image.indexOf("//") === 0) {
                this.sku[i].image = "https:" + this.sku[i].image;
            }
        }		
        var data = {
            website: this.getWebsite(),
            id: this.item.id,
            title: this.item.title,
            url: this.item.url,
            image: this.item.image,
            ws_rule_number: this.item.ws_rule_number,
            min_quantity: this.item.min_quantity,
            price_ranges: JSON.stringify(this.item.price_ranges),
            weight: this.item.weight,
            shop_id: this.shop.id,
            shop_name: this.shop.name,
            shop_url: this.shop.url,
            shop_address: this.shop.address,
            item_note: document.getElementById('item_note').value,
            list_sku: JSON.stringify(this.sku)
        };
        var t = null;
        HTMLUtil.post(nhtqConfig.apiDomain + nhtqConfig.apiaddtocart, data, function(response) {
			console.log('===response===');
			console.log(response);
            if (response.success === true) {
                if (t !== null) {
                    clearTimeout(t);
                }
                t = setTimeout(function() {
                    HTMLUtil.alert('S\u1ea3n ph\u1ea9m \u0111\u00e3 \u0111\u01b0\u1ee3c th\u00eam v\u00e0o gi\u1ecf h\u00e0ng. ' +
                        '<a href="' + nhtqConfig.apiDomain + nhtqConfig.cart +'" target="_blank"><b>Xem gi\u1ecf h\u00e0ng &raquo;</b> T&#7893;ng:'+response.count+' s&#7843;n ph&#7849;m</a>.',
                        {parent: '#nhtqOrderMsg', type: 'success'});
                }, 250);
            } else {
                HTMLUtil.alert('Th\u00eam s\u1ea3n ph\u1ea9m v\u00e0o gi\u1ecf h\u00e0ng kh\u00f4ng th\u00e0nh c\u00f4ng: ' + response.error, {
                    parent: '#nhtqOrderMsg', type: 'error'
                });
            }
        });
    } else {
        if (typeof this.sku === 'undefined' || this.sku === null || this.sku.length === 0) {
            HTMLUtil.alert('Qu\u00fd kh\u00e1ch vui l\u00f2ng ch\u1ecdn th\u00f4ng s\u1ed1 s\u1ea3n ph\u1ea9m mu\u1ed1n \u0111\u1eb7t mua.', {parent:'#nhtqOrderMsg', type:'error'});
        } else if (this.selectedQuantity) {
            HTMLUtil.alert('S\u1ed1 l\u01b0\u1ee3ng \u0111\u1eb7t mua qu\u00fd kh\u00e1ch y\u00eau c\u1ea7u kh\u00f4ng ph\u00f9 h\u1ee3p.', {parent:'#nhtqOrderMsg', type:'error'});
        }
    }
}


NHToolbar.prototype.run = function()
{
    var instance = this;

	if (instance.isItemDetailPage()) {
		console.log('isItemDetailPage:',instance.isItemDetailPage());
		setTimeout(function() {
			instance.renderItemInfo();
		}, 1000);
	}

	console.log('==run render==');
    instance.render();
}

NHToolbar.prototype.getHostName = function()
{
    return window.location.hostname;
}

NHToolbar.prototype.getWebsite = function()
{
    var hostname = this.getHostName();
    if (hostname.indexOf('taobao.com') >= 0) {
        return 'taobao.com';
    } else if (hostname.indexOf('1688.com') >= 0) {
        return '1688.com';
    } else if(hostname.indexOf('tmall.com') >= 0) {
        return 'tmall.com';
    } else if(hostname.indexOf('tmall.hk') >= 0) {
        return 'tmall.com';
    }
}

NHToolbar.prototype.getUrl = function()
{
    return window.location.href;
}

NHToolbar.prototype.isItemDetailPage = function()
{
    var url = this.getUrl();
	console.log('===url:',url);
    for(var i in this.itemDetailPatterns) {
        if (~url.indexOf(this.itemDetailPatterns[i])) {
            return true;
        }
    }
	
    return false;
}

NHToolbar.prototype.rmbToVnd = function(input) {
    var commi = 0;
    switch(this.website) {
        case '1688.com':
            commi = this.config.config.service_cost_1688;
            break;
        case 'taobao.com':
            commi = this.config.config.service_cost_taobao;
            break;
        case 'tmall.com':
        case 'tmall.tk':
            commi = this.config.config.service_cost_tmall;
            break;
    }
    commi = commi * 0.01;
    var amount = input * this.config.config.exchange_rate;

    amount = Math.ceil(amount);
    if (amount % 100 !== 0) {
        amount = amount + (100 - (amount % 100));
    }
    return amount;
}

var nhtb = new NHToolbar();
