$('.tooltip-container').on("touchstart", function (e) {
    "use strict"; //satisfy the code inspectors
    var link = $(this); //preselect the link
    if (link.hasClass('hasHover')) {
        return true;
    } else {
        link.addClass("hasHover");
        $('.tooltip-container').not(this).removeClass("hasHover");
        e.preventDefault();
        return false; //extra, and to make sure the function has consistent return points
    }
});

$("html").on("touchstart", function (e) {
    "use strict";
    if ($(e.target).hasClass(".tooltip-container")) {
        return false;
    }
    $(".tooltip-container").removeClass("hasHover");
    return true;
});

