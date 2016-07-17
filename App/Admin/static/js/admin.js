// Production steps of ECMA-262, Edition 6, 22.1.2.1
// Reference: https://people.mozilla.org/~jorendorff/es6-draft.html#sec-array.from
if (!Array.from) {
  Array.from = (function () {
    var toStr = Object.prototype.toString;
    var isCallable = function (fn) {
      return typeof fn === 'function' || toStr.call(fn) === '[object Function]';
    };
    var toInteger = function (value) {
      var number = Number(value);
      if (isNaN(number)) { return 0; }
      if (number === 0 || !isFinite(number)) { return number; }
      return (number > 0 ? 1 : -1) * Math.floor(Math.abs(number));
    };
    var maxSafeInteger = Math.pow(2, 53) - 1;
    var toLength = function (value) {
      var len = toInteger(value);
      return Math.min(Math.max(len, 0), maxSafeInteger);
    };

    // The length property of the from method is 1.
    return function from(arrayLike/*, mapFn, thisArg */) {
      // 1. Let C be the this value.
      var C = this;

      // 2. Let items be ToObject(arrayLike).
      var items = Object(arrayLike);

      // 3. ReturnIfAbrupt(items).
      if (arrayLike == null) {
        throw new TypeError("Array.from requires an array-like object - not null or undefined");
      }

      // 4. If mapfn is undefined, then let mapping be false.
      var mapFn = arguments.length > 1 ? arguments[1] : void undefined;
      var T;
      if (typeof mapFn !== 'undefined') {
        // 5. else      
        // 5. a If IsCallable(mapfn) is false, throw a TypeError exception.
        if (!isCallable(mapFn)) {
          throw new TypeError('Array.from: when provided, the second argument must be a function');
        }

        // 5. b. If thisArg was supplied, let T be thisArg; else let T be undefined.
        if (arguments.length > 2) {
          T = arguments[2];
        }
      }

      // 10. Let lenValue be Get(items, "length").
      // 11. Let len be ToLength(lenValue).
      var len = toLength(items.length);

      // 13. If IsConstructor(C) is true, then
      // 13. a. Let A be the result of calling the [[Construct]] internal method of C with an argument list containing the single item len.
      // 14. a. Else, Let A be ArrayCreate(len).
      var A = isCallable(C) ? Object(new C(len)) : new Array(len);

      // 16. Let k be 0.
      var k = 0;
      // 17. Repeat, while k < len… (also steps a - h)
      var kValue;
      while (k < len) {
        kValue = items[k];
        if (mapFn) {
          A[k] = typeof T === 'undefined' ? mapFn(kValue, k) : mapFn.call(T, kValue, k);
        } else {
          A[k] = kValue;
        }
        k += 1;
      }
      // 18. Let putStatus be Put(A, "length", len, true).
      A.length = len;
      // 20. Return A.
      return A;
    };
  }());
}

'use-strict'

var AdminController = function() {
    /*
      App scope
    */
    var App = this;
    App.name = 'AdminController';
    // App.debug = true;

    /* "global" objects */
    $('document').ready(function() {
        App.imagePreviewCanvas = document.getElementById("image-preview");
        App.addEventHandlers();

        /* AJAX setup */
        var csrfToken = $('input[name=csrf_token]').val();
        if (csrfToken) {
            $.ajaxSetup({
                headers:{'X-CSRFToken':csrfToken},
            });
        };

        var authToken = $('input[name=auth_token]').val();
        if (authToken) {
            $.ajaxSetup({
                headers:{'Authentication-Token':authToken},
            });
        };
    });
}; /* App init */

AdminController.prototype.eventHandlers = {
    /* There's a better way to register these functions */
    handleImageFile: function() {
        var imagePreviewFn = this.files[0].name;
        var imgUrl = window.URL.createObjectURL(this.files[0]);
        App.loadImagePreview(imgUrl, imagePreviewFn);        
    },
};

AdminController.prototype.addEventHandlers = function() {
    $('.ajax-submit').on('submit', function(event) { 
        event.preventDefault();
        App.submitForm(document.activeElement);
    });

    $('.confirm-submit').on('click', function(event) {
        event.preventDefault();
        App.confirmSubmit(event);
    });

    $('#image').on('change', function(event) {
        App.eventHandlers.handleImageFile.call(this);
    });

    $('#padding_color').on('change', function(event) {
        App.updatePreviewBackground(); 
    });

    $('#close-overlay').on('click', function(event) {
        $('#overlay').hide();
        $('#message-container').hide();
    });

    if (App.imagePreviewCanvas) {
        var imgSrc = App.imagePreviewCanvas.dataset.url;
    };

    if (imgSrc) {
        App.loadImagePreview(imgSrc, imgSrc);
    };

    $('#save-image-order').on('click', function(event) {
        App.saveImageOrder(event);
    });

    $('#show-images-for-series').on('click', function(event) {
        App.showImagesForSeries(); 
        $('#by-title').on('click', App.orderSeriesImagesByTitle);
        $('#by-display_order').on('click', App.orderSeriesImagesByOriginalOrder); 
        $('#by-date_added').on('click', App.orderSeriesImagesByDateAdded); 
        $('#by-date').on('click', App.orderSeriesImagesByDate); 
    });

    $('#images-in-grid').on('click', function(event) {
        var container = $('#series-image-container');
        App.containerItemsInRows(container);
    });

    $('#images-in-rows').on('click', function(event) {
        /* counter intuituve names */
        var container = $('#series-image-container');
        App.containerItemsInCols(container);
    });

    $('button[type=reset]').on('click', function(event) {  
         /*  only clears non-hidden elements
         *  so as not to lose csrf/auth tokens and such
         * */
        var skipTypes = ['hidden',]
        var $inputs = $(this.form).find(':input'); /* includes textarea */
        $inputs.each(function(ind, elem) { 
            console.log(elem);
            if (skipTypes.indexOf(elem.type) === -1) {
                elem.value = '';
                $(elem).removeClass('disabled');
                elem.disabled = false;
            };
        });
    });

    /* disable inputs on text/link form so you can't input both a text and a link at the same time */
    var $newTextInputs = [$('#text-form-container #title'), 
        $('#text-form-container #author'), 
        $('#text-form-container #date'),
        $('#text-form-container #body'),
    ];
    var $newLinkInputs = [$('#text-form-container #label'), 
        $('#text-form-container #link_target'),
        $('#text-form-container #description'),
    ];

    function disableInputs(inputs) {
        inputs.forEach(function(elem, ind) {
            elem[0].disabled = true;
            $(elem[0]).addClass('disabled');
        });
    };

    $newTextInputs.forEach(function(elem) { 
        elem.on('change', function() { 
            disableInputs($newLinkInputs)
        });
    });

    $newLinkInputs.forEach(function(elem) { 
        elem.on('change', function() { 
            disableInputs($newTextInputs)
        });
    });

    $('input#icon').on('change', App.showIconPreview);

    $('#series-list .up-order').on('click',   function(event) { App.reorderSeriesTable(event) });
    $('#series-list .down-order').on('click', function(event) { App.reorderSeriesTable(event) });

    /* debug */
    if (App.debug) {
        $('.admin-form').on('submit', function(event) {
            console.log(event);
        });
    };
}; // event handlers

AdminController.prototype.confirmSubmit = function(event) {
    var submitConfirmedForm = function() {
        /* fix formData processing */
        var data = new FormData(event.target.form);
        var url = event.target.formAction;

        $.ajax({
            url:url,
            data:data,
            processData: false,
            method:'post',
            xhrFields: {
                withCredentials: true,
            },
            success: function(data, textStatus, jqXHR) {
                var next = data['next'];
                location.replace(next);
                },
        });
    };


    this.modalDialog(
            {'message':'Are you sure?'},
            'no',
            'yes',
            submitConfirmedForm
            );
};

AdminController.prototype.populateForm =function(form, formData) {
    /* formdata must be an array of [name, value] pairs */ 
    for (i=0; i<formData.length; i++) {
        item = formData[i];
        name = item[0];
        value = item[1];
        selector = "[name="+name+"]";
        elem = document.querySelector(selector);
        elem.value = value;
    };
};

AdminController.prototype.closeDialog = function() {
        $('#message-container').hide();
        $('#overlay').hide();
    };

AdminController.prototype.modalDialog = function(message, close, confirm, callback, callbackArgs) {
    /*
       message should be an object with a message attribute, like jqXHR.responseJSON
       that should be a string or array
       args are used to determine type of dialog i.e. to show dialog options
       ...handle accept/reject somewhere
       close is handled in eventHandlers
       I don't know what will happen if callbackArgs is an array
    */

    if (App.debug) {
        console.log('[debug] modalDialog', arguments);
    };

    if (!message.message) {
        console.log('arg1 has no message attribute');
        return null;
    }

    var container = $('#message-container');
    container.find('ul').html('');
    var closeButton = $('#message-container #close');
    var confirmButton = $('#message-container #confirm')

    closeButton.html('');
    confirmButton.html('')

    var messageContainer = $('#message-container');
    messageContainer.show();
    $('#overlay').show()

    if (confirm) {
        if (typeof(confirm) === 'string') {
            var confirmMsg = confirm;
        } else {
            var confirmMsg = 'confirm';
        };

        confirmButton.html(confirmMsg);
    };

    var closeMsg = 'close';

    if (close) {
        if (typeof(close) === 'string') {
            var closeMsg = close;
        };
    };

    closeButton.html(closeMsg);
    closeButton.on('click', App.closeDialog);

    if (callback) {
        confirmButton.on('click', function() {
            App.closeDialog();
            callback.apply(App, callbackArgs);
        });
    } else {
        if (App.debug) {
            console.log('[debug] modalDialog has no callback', arguments);
        };
    };
    /* load messages */
    var messages = new Array()
    if (typeof(message.message) === 'string') {
        messages.push(message.message);
    } else {
	for (i=0; i<message.message.length; i++) {
	    messages.push(message.message[i]);
        };
    };

    messages.forEach(function(val, ind, arr) {
        var msgList = messageContainer.find('ul');
        msgList.empty();
        var msgStr = "<li>%s</li>".replace('%s', val);
        msgList.append(msgStr);
    });

    window.scroll(0, 0);
    $('#overlay').show();
    container.show();
};

AdminController.prototype.submitForm = function(elem) {
    /* generic function, populates form with recieved formData JSON */
    function sendReq() {
        if (App.debug) { console.log('[debug] sendReq', arguments); };

        var url = elem.formAction;
        var form = $($(elem).context.form);
        var formData = form.serializeArray();
        var data = JSON.stringify(formData);

        $.ajax({url:url,
            method:'post',
            dataType:'json',
            data:data,
            contentType:'application/json',
            success: function(jqXHR, status, response) {
            var json = response.responseJSON;

            if (!jqXHR.errors) {
                if (jqXHR.formData) {
                    App.populateForm(form, jqXHR.formData);
                };
                /* always show messages in dialog */
                if (App.debug) { console.log('form submitted', jqXHR, status, response); };
                App.modalDialog(jqXHR, true);
            } else {
                window.alert('show errors')
            };
        }, 
        error: function(jqXHR, status, error) {
            console.log(jqXHR.responseText);
        },
        });
    };

    var confirmActions = ['delete', 'confirm'];

    if (confirmActions.indexOf(elem.name) >= 0) {
        var msg = {'message':'really %s series?'.replace('%s', elem.name)}
        /* callback gets called from modalDialog */
        App.modalDialog(msg, 'no', 'yes', sendReq);
    } else {
        sendReq();
    };
};

AdminController.prototype.updatePreviewBackground = function() {
    var paddingColor = $('#padding_color').val() || '#ffffff';
    this.imagePreviewCanvas.style.backgroundColor = paddingColor;
    $('span#padding-color').html(paddingColor);
};

AdminController.prototype.showImageFilename = function(Filename) {
    $('#filename').html(Filename);
};

AdminController.prototype.loadImagePreview = function(imgURL, Filename) {
    /* called for image upload and when edit image loads existing image*/
    var canv = this.imagePreviewCanvas;
    var ctx = canv.getContext('2d');
    var img = new Image();

    img.src = imgURL;

    img.onload = function() {
        var imgXY = [parseInt(img.width), parseInt(img.height)];
        var imgMaxDim = Math.max(imgXY[0], imgXY[1]);
        var maxImgSize = 450; // this is the size images will be scaled TO
        /* 25px padding inside canvas */
        var minPadding = 25;
        var availSpace = Math.max(canv.width, canv.height)-(minPadding*2);
        if (imgMaxDim > maxImgSize) {
            /* scale image if it's bigger than 450px */
            var scaleRatio = imgMaxDim/availSpace;
            var scaledXY = imgXY.map(function(val, ind, arr) {
            return val/scaleRatio;
            });
        } else {
            var scaledXY = imgXY;
        }
        /* img position */
        var imgPos = scaledXY.map(function(val, ind, arr) {
            var padding = [canv.width, canv.height][ind]-val;
            return padding/2;
        });
    
        ctx.clearRect(0, 0, canv.width, canv.height);
        ctx.drawImage(img, imgPos[0], imgPos[1], scaledXY[0], scaledXY[1]);
        App.updatePreviewBackground();
        App.showImageFilename(Filename);
    };
};

AdminController.prototype.reorderSeriesTable = function(event) {
    // var action = event.target.innerText;
    // get action from class name

    if (event.target.classList.contains('up-order')) {
        action = 'up'
    };

    if (event.target.classList.contains('down-order')) {
        action = 'down';
    };

    if (!action) { return };

    var currentRow = event.target.parentElement;
    // var currentId = event.target.parentElement.dataset.seriesid;

    var seriesTable = document.querySelector('#series-list tbody');
    var seriesRows = Array.from(seriesTable.getElementsByTagName('tr'));

    // function getTitle(row) {
    //     titleCell = row.children[3];
    //     return titleCell.children[0].innerHTML;
    // };

    var alreadySorted = false;
    var sortedRows = Array.from(seriesRows);

    sortedRows.sort(function(a, b) {
        if (!alreadySorted && b == currentRow && action === 'up') {
            alreadySorted = true;
            return 1; // a before b
        };

        if (!alreadySorted && a == currentRow && action === 'down') {
            alreadySorted = true;
            return 1; // b before a
        };
        return 0;
    });

    for (i=0; i<seriesRows.length; i++) {
        seriesTable.appendChild(sortedRows[i]);
    };
};

AdminController.prototype.showImagesForSeries = function() {
    var container = $('#series-image-container');
    if (container.css('display') === 'none') {
        container.css('display', 'flex');
        $('.series-image-controller').css('display', 'block');
        $('#images_order_by').css('display', 'inline-block');
    } else {
        container.css('display', 'none');
        $('.series-image-controller').css('display', 'none');
    };
};

AdminController.prototype.containerItemsInRows = function(container) {
    /*  this changes the orientation of items in a flex box 
     *  cols or rows refers to flex-direction
    */
    $(container).css('flex-direction', 'row');
    var rows = container.find('.container');

    rows.each(function(ind, item) {
        $(item).removeClass('in-rows');

        if (ind%2 !== 0) {
            $(item).removeClass('odd');
        }
    });
};

AdminController.prototype.containerItemsInCols = function(container) {
    $(container).css('flex-direction', 'column');
    var rows = container.find('.container');

    rows.each(function(ind, item) {
        $(item).addClass('in-rows');

        if (ind%2 !== 0) {
            $(item).addClass('odd');
        }
    });
};

AdminController.prototype.orderSeriesImagesByDateAdded = function() {
    /* I think the other sort functions should be refactored following this model */
    /* There's probably a way to do this without iterating over the list twice */
    var containers = Array.from(document.getElementsByClassName('container'));

    containers.sort(function(a, b) {
        var aDateStr = a.querySelector('time').attributes.datetime.value;
        var bDateStr = b.querySelector('time').attributes.datetime.value;

        var aDate = aDateStr.split('.')[0].replace(' ', 'T');
        var bDate = bDateStr.split('.')[0].replace(' ', 'T');


        if (aDate < bDate) {
            return -1;
        };
    
        if (aDate > bDate) {
            return 1;
        };
        if (aDate === bDate) {
            return 0;
        };
    });

    for (i=0; i<containers.length; i++) {
        containers[i].style.order = i+1;
    };
};

AdminController.prototype.orderSeriesImagesByDate = function() {
    /* date refers to image date, not date_added to db */
    var containers = document.getElementsByClassName('container');
    var containerElems = []; 
    var savedOrder = [];

    for (i=0; i<containers.length; i++) {
        var elem = containers[i];
        var date = elem.getElementsByClassName('date')[0].textContent;
        containerElems.push({'date':parseInt(date), 'elem':elem});
        savedOrder.push(parseInt(elem.dataset.originalorder));
    };

    var firstOrder = savedOrder[0];

    containerElems.sort(function(a, b) {
        if (a.date > b.date) {
            return -1;
        }

        if (a.date < b.date) {
            return 1;
        } else {
            return 0;
        };
    });

    containerElems.forEach(function(i, ind, arr) {
        var newOrder = firstOrder+ind;
        i.elem.style.order = newOrder;
    });
};

AdminController.prototype.orderSeriesImagesByOriginalOrder = function() {
    /* use data attrib to restore images to order stored in the db */
    var containers = document.getElementsByClassName('container');

    for (i=0; i<containers.length; i++) {
        elem = containers[i];
        var db_order = elem.dataset.originalorder;
        elem.style.order = db_order;
    };
};

AdminController.prototype.orderSeriesImagesByTitle = function() {
    /* SPECIAL title sort for prisms, normal sort for other series
     * This will break if I change the format of the Prism titles...
     * */
    var containers = document.getElementsByClassName('container');
    var containerElems = [];
    var startIndex = 0;
    /* make this available to validate Prism titles */
    var prismRe = /(\d{2})(\d{2})\.?(\d{4})\.?(\d{2})\.?(\d{2})\.?(\d{2})/;

    function prismTitleSort() {
        /* this has no error checking for malformed titles! */
        containerElems.forEach(function(i, ind, arr) {
            var parsed = prismRe.exec(i.title); 
            var values = parsed.slice(1,7);
            var ymd = values.slice(0,3).reverse();
            var hms = values.slice(3,7);
            var ymd_hms = ymd.concat(hms);

            i.parsedTitle = ymd_hms.map(function(val, ind, arr) { return parseInt(val, 10) });
            /* get the lowest original order for containers */
            var oOrder = parseInt(i.elem.dataset.originalorder);
            if (startIndex === 0 || oOrder < startIndex) {
                startIndex = oOrder;
            };
        });

        containerElems.sort(function(a, b) {
            /* reverse sort */
            var a = a.parsedTitle;
            var b = b.parsedTitle;

            for (i=0; i<a.length; i++) {
                if (a[i] > b[i]) {
                    return -1;
                };

                if (a[i] < b[i]) {
                    return 1;
                };
            };
        });

        return containerElems;
    };

    function isPrismTitle(containers) {
        /* try to determine whether titles are prism titles */
        /* if the first one matches then ASSUME all titles  */
        var it = containers[0];
        var titleElem = it.getElementsByClassName('title')[0];
        var title = titleElem.textContent;
        return prismRe.test(title);
    };

    for (i=0; i<containers.length; i++) {
        /* Array of objects with elems and titles */
        var elem = containers[i];
        var title = elem.getElementsByClassName('title')[0].textContent;
        containerElems.push({'title':title, 'elem':elem});
    };

    if (isPrismTitle(containers)) {
        var sortedContainers = prismTitleSort();
    } else {
        containerElems.sort(function(a, b) {
            atitle = a.title;
            btitle = b.title;
            if (a.title > b.title) {
                return 1;
            } else {
                return -1;
            }
        });

        var sortedContainers = containerElems;
    };

    sortedContainers.forEach(function(item, ind, arr) {
        item.elem.style.order = ind;
    });
};

AdminController.prototype.saveImageOrder = function(event) {
    /* sends json to server with series id and images obj 
     * where image ids are keys and new order are values */
    var containers = document.getElementsByClassName('container');
    var data = {};

    var url = document.getElementById('save-image-order').dataset.url;
    var series_id = document.getElementById('save-image-order').dataset.seriesid;

    data['series_id'] = series_id;
    var image_data = {};

    for (i=0; i<containers.length; i++) {
        image_data[containers[i].dataset.imageid] = containers[i].style.order;
    };

    data['images'] = image_data;
    var json_data = JSON.stringify(data);

    $.ajax({
        url:url,
        method:'post',
        dataType:'json',
        data:json_data,
        contentType:'application/json',
        success: function(jqXHR, status, response) {
            App.modalDialog(jqXHR);
        },
        error: function(jqXHR, status, response) {
            App.modalDialog({
                'message':'There was a network error while updating the image order'
            });
        },
    });
};


AdminController.prototype.showIconPreview = function() {
    /* this is for the contact info icon file upload */
    var $img = $('p#file-upload img');
    var file = this.files[0];
    var allowedTypes = ['image/jpeg', 'image/jpg','image/png', 'image/gif'];
    if (allowedTypes.indexOf(file.type) < 0) {
        alert('Invalid File');
        return false;
    };

    $img.on('load', function() {
        var height = $img[0].naturalHeight;
        var width = $img[0].naturalWidth;
        $img.css('height', height);
        $img.css('width', width);

        if (height > 64 || width > 64) {
            window.alert('64px is the max image size');
            $img[0].src = '';
            $img.addClass('no-icon');
        } else { 
            $img.removeClass('no-icon');
        };
    });

    var url = window.URL.createObjectURL(this.files[0]);
    $img[0].src = url;
};


(function() {
    window.App = new AdminController();
})();
