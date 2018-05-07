var $cells = $(".filter");

$("#search").keyup(function() {
    var val = $.trim(this.value).toUpperCase();
    console.log(val);
    if (val === "")
        $cells.parent().show();
    else {
        $cells.parent().hide();
        $cells.filter(function() {
            return -1 != $(this).text().toUpperCase().indexOf(val); }).parent().show();
    }
});

$(document).mousemove(function(e) {
    $(".hovering_image").css({left:e.pageX + 1 , top:e.pageY + 1 });
});

function hovering(image) {
    $(".hovering_image").css({'background-image': 'url(' + image + ')', 'display': 'block'});
}

function outhovering() {
    $(".hovering_image").css({'display': 'none'});
}

function toClipboard(name) {
    var copyText = document.getElementById('command');
    copyText.value += name;
    $("#command").css({'display': 'block'});
    copyText.select();
    status = document.execCommand("copy");
    copyText.value = "!image ";
    $("#command").css({'display': 'none'});
}
