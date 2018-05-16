var logout_button = $('#logout');

function logout() {
    if (logout_button.hasClass('toggled')) {
        logout_button.html('&#8677;');
    }
    else {
        logout_button.html('Déconnexion');
    }
    logout_button.toggleClass('toggled');
}

/* === Delete Image === */
function display_alert(id, content) {
    $('#' + id).html(content);
    $('#' + id).css({'opacity': '0.9'});
    setTimeout(function() {
        $('#' + id).css({'opacity': '0'});
    }, 5000);
}

function close_alert(id) {
    $('#' + id).css({'opacity': '0'});
}

function delete_image(image_id) {
    $.ajax({
        method: "POST",
        url: "/delete/" + image_id,
        data: {},
        success: function(data) {
            $("#image_" + data['id']).remove();
            display_alert("alert_danger", "Image \"" + data["name"] + "\" supprimée avec succès !");
            closeModal();
        }
    })
}


/* === Fav Image === */
function fav_image(user_id, image_id) {
    $.ajax({
        method: "POST",
        url: "/fav/" + user_id + "/" + image_id,
        data: {},
        success: function(data) {
            var image_div = $("#image_" + data['image_id'])
            if (data['action'] == 'add') {
                image_div.find(".fav")[0].classList.add('selected');
                $(".content-wrapper").prepend(image_div);

            }
            else if (data['action'] == 'remove') {
                image_div.find(".fav")[0].classList.remove('selected');
                $(".content-wrapper").append(image_div);
            }
            console.log(data);
        }
    })
}


/* === Cells behavior === */
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


/* === Hovering === */
$(document).mousemove(function(e) {
    $(".hovering_image").css({left:e.pageX + 1 , top:e.pageY + 1 });
});

function hovering(image) {
    $(".hovering_image").css({"background-image": "url(" + image + ")", "display": "block"});
}

function outhovering() {
    $(".hovering_image").css({"display": "none"});
}

function toClipboard(name) {
    var copyText = document.getElementById("command");
    copyText.value += name;
    $("#command").css({"display": "block"});
    copyText.select();
    status = document.execCommand("copy");
    copyText.value = "!image ";
    $("#command").css({"display": "none"});
}

/* === Delete Modal === */
// When the user clicks the button, open the modal 
function openDeleteModal(image_name, image_id) {
    document.getElementById('deleteModal').style.display = "block";
    $("#modal_text").html("Es tu sûr de vouloir effacer l'image \"" + image_name + "\" ?")
    $("#modal_ok").click(function () { delete_image(image_id); });
}

function openUploadModal() {
    document.getElementById('uploadModal').style.display = "block";
}

// When the user clicks on <span> (x), close the modal
function closeModal() {
    document.getElementById('deleteModal').style.display = "none";
    document.getElementById('uploadModal').style.display = "none";
}

function send_image() {
    var url = $("#load_url").val();
    var regex = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
    if (regex.test(url))
        console.log(url);
}

window.onclick = function(e) {
    if (logout_button.hasClass('toggled') && !logout_button.is(e.target) && logout_button.has(e.target).length === 0) {
        logout_button.removeClass('toggled');
        logout_button.html('&#8677;');
    }
    
    if (e.target == document.getElementById('deleteModal')) {
        document.getElementById('deleteModal').style.display = "none";
    }
    if (e.target == document.getElementById('uploadModal')) {
        document.getElementById('uploadModal').style.display = "none";
    }
}