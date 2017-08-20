


// var sideBar = $("#sidebar");


// sideBar.scroll(function() {
//     sideBar.scrollTop($(this).scrollTop());
// });


var offset = $('.sidebar').offset().top;
$('#sidebar').affix({
  		offset: {
    		top: offset - 25,
    		bottom: 100
    	}
});
$( document ).ready(function() {

	
	var top = $('.header').outerHeight(true) + $('.breadcrumb').outerHeight(true) + $('.header title').outerHeight(true) + $('#top_page').outerHeight(true) + 100;
	var bottom = ($('section').outerHeight(true) - 100);
	var lastScrollTop = 0;
	$(window).on('scroll', function () {
		if($(window).width() > 992){
			if($('#sidebar').hasClass('affix')){
			var st = $(this).scrollTop();
			if($(window).scrollTop() > top && $(window).scrollTop() < bottom){
				var curScroll = $('#sidebar').scrollTop();
				if(st > lastScrollTop){
	    			$('#sidebar').scrollTop(curScroll + 10);
	    		} else{
	    			$('#sidebar').scrollTop(curScroll - 10);
	    		}
	    		lastScrollTop = st;
			}
			}
		}
	});

});
