var Ptgs = function() {
    "use-strict";
    document.addEventListener('DOMContentLoaded', function() {
        Ptgs.eventHandlers();
        Ptgs.openInfoContainers = [];
    });
};

Ptgs.prototype.eventHandlers = function() {
    function toggleInfoContainers(eve) {
        /* hide all image info containers except the current one */
        for(i=0; i<Ptgs.openInfoContainers.length; i++) {  
            elem = Ptgs.openInfoContainers[i];
            if (elem != eve.target.nextElementSibling) {
                $(elem).slideUp(80);
            };
        };

        $(eve.target.nextElementSibling).slideToggle(80);
        Ptgs.openInfoContainers.push(eve.target.nextElementSibling);
    };
    
    $('.show-hide-image-info').on('click', function(event) {
        toggleInfoContainers(event);
    });
    
    $('#menu-button-container').on('click', function(event) {
        $('nav').toggleClass('open');
        $('body').scrollTop(0); 
    });

    $('nav ul li').on('click', function(event) {
        var elem = event.target;
        var menuItems = elem.getElementsByTagName('ul');
        $(menuItems).toggleClass('visible');
    });

    $(document).scroll(function(event) {
        if ($('body').width() < 719 ) {
            var docPos = $('body').scrollTop();
            if (docPos > 325) {
                $('#up-button').fadeIn(55);
            } else {
                $('#up-button').fadeOut(55);
            };
        };
    });

    $('#up-button').on('click', function() {
       $('body').scrollTop(0); 
    });

    $('.description').on('click', function() {
        $(this).toggleClass('show-description');
    });

    if ($('body').width() >= 719 ) {
        $('.image img').on('click', function(event) {
            Ptgs.openViewer(this);
        });
    };
};

Ptgs.prototype.scaleViewerImage = function(img) {
    /* at least 25px padding inside canvas */
    var minPadding = 25;
    var imgWH = [parseInt(img.width), parseInt(img.height)];                                                                     
    
    var canv_wh = [parseInt(Ptgs.canv.width, 10), parseInt(Ptgs.canv.height, 10)];
    var canv_padded_wh = canv_wh.map(function(i) { return i-(minPadding*2) });
    
    /* OJO max allowed image size is the smallest canvas dimension */
    var max_scaled_dim = Math.min.apply(this, canv_padded_wh);

    var doScale = imgWH.some(function(val, ind, arr) { 
        return val > max_scaled_dim;
    });

    if (doScale) {
        var scaleRatio = max_scaled_dim / Math.max.apply(this, imgWH);  

        var imgWH = imgWH.map(function(val, ind, arr) {
            return Math.round(val * scaleRatio);
        }); 
    };

    /* position of image centered on canvas */
    var offset = [];
    for (i=0; i<2; i++) {
        offset.push((canv_wh[i] - imgWH[i]) / 2);
    };

    return {'imgPos': offset, 'scaledXY': imgWH};
};

Ptgs.prototype.loadViewerImageInfo = function() {
    $('#image-info .info-table-container').remove();
    var $infoTable = $('.info-table-container[data-order="%s"]'.replace('%s', Ptgs.currentViewerIndex)).clone();
    var $tableContainer = $('.viewer-container #image-info');
    $tableContainer.append($infoTable);

    /* get position of elements relative to parent */
    var canvPos = $(Ptgs.canv).position();
    var Xpos = $tableContainer.width();
    $tableContainer.css('left', canvPos.left-Xpos);
};

Ptgs.prototype.loadImageViewer = function(img) {
    Ptgs.currentViewerIndex = $(img).data('order');

    var ctx = Ptgs.canv.getContext("2d");
    var src = img.src.replace('thumbnails/', '');
    var image = new Image();
    image.src = src;

    image.onload = function() {
        var imgData = Ptgs.scaleViewerImage(image);    
        ctx.clearRect(0, 0, Ptgs.canv.width, Ptgs.canv.height);
        ctx.drawImage(image, imgData.imgPos[0], imgData.imgPos[1], imgData.scaledXY[0], imgData.scaledXY[1]);
        Ptgs.canv.style.backgroundColor = img.style.backgroundColor;
    };

    $('#current-count').html(Ptgs.currentViewerIndex);
    var lastImg = $('.image:last-of-type img')[0];
    Ptgs.lastViewerIndex = $(lastImg).data('order');
    $('#total-count').html(Ptgs.lastViewerIndex);

    Ptgs.loadViewerImageInfo();
};

Ptgs.prototype.advanceViewer = function(event) {
    event.stopImmediatePropagation();
    var nextImage = $('.image img[data-order="%s"]'.replace('%s', Ptgs.currentViewerIndex+1));

    if (nextImage.length) {
        Ptgs.loadImageViewer(nextImage[0]);
    } else {
        nextImage = $('.image img[data-order="1"]');
        Ptgs.loadImageViewer(nextImage[0]);
    };
};

Ptgs.prototype.reverseViewer = function(event) {
    event.stopImmediatePropagation();

    if (Ptgs.currentViewerIndex > 1) {
        /* order is a 1 based index */
        var prevImage = $('.image img[data-order="%s"]'.replace('%s', Ptgs.currentViewerIndex-1));
        Ptgs.loadImageViewer(prevImage[0]);
    } else {
        var lastImg = $('.image:last-of-type img');
        Ptgs.loadImageViewer(lastImg[0]);
    };
};

Ptgs.prototype.openViewer = function(thumbnail) {
    for (i=0; i<Ptgs.openInfoContainers.length; i++) {
        $(Ptgs.openInfoContainers[i]).slideUp(10);
    };

    var $container = $('.viewer-container');
    var $closeButton = $('#close-viewer');
    $('.viewer').show();
    /* contains canvas */
    $container.addClass('viewer-open');
    Ptgs.canv = document.getElementById('viewer-canvas');

    if (!Ptgs.canv.getContext) {
        console.log('canvas context does not exist');
        return null;
    };

    $closeButton.on('click', function(event) {
        $('.viewer').hide();
        $container.removeClass('viewer-open');
    });

    $('#forward-arrow-container').on('click', Ptgs.advanceViewer); 
    $('#back-arrow-container').on('click', Ptgs.reverseViewer); 
    
    /* set size of canvas to screen */
    Ptgs.canv.height = $('body').height() * 0.85; 
    Ptgs.canv.width = $('body').width() * .5; 

    Ptgs.loadImageViewer(thumbnail);
};

(function() {
    window.Ptgs = new Ptgs();
})();
