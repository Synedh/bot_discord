var logout_button = $('#logout');
var modal = document.getElementById('myModal');

function logout() {
    if (logout_button.hasClass('toggled')) {
    }
    else {
        logout_button.html('Déconnexion');
    }
    logout_button.toggleClass('toggled');
}


/* Cells behavior */
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


/* Hovering */
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

/* Modal */
// When the user clicks the button, open the modal 
function openModal(image_name, image_id) {
    modal.style.display = "block";
    $("#modal_text").html("Es tu sûr de vouloir effacer l'image \"" + image_name + "\" ?")
    $("#modal_ok").attr("href", '/delete/' + image_id)
}

// When the user clicks on <span> (x), close the modal
function closeModal() {
    modal.style.display = "none";
}

window.onclick = function(e) {
    if (logout_button.hasClass('toggled') && !logout_button.is(e.target) && logout_button.has(e.target).length === 0) {
        logout_button.removeClass('toggled');
        logout_button.html('&#8677;');
    }
    
    if (e.target == modal) {
        modal.style.display = "none";
    }
}