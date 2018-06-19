var logout_button = $("#logout");
var image_loaded = false;

function logout() {
    if (logout_button.hasClass("toggled")) {
        $.ajax({
            method: "GET",
            url: "/disconnect",
            success: function(data) {
                if (data["success"]) { window.location.reload(); }
            }
        })
        logout_button.html("&#8677;");
    }
    else {
        logout_button.html("Déconnexion");
    }
    logout_button.toggleClass("toggled");
}

/* === Delete Image === */
function display_alert(id, content) {
    $("#" + id).html(content);
    $("#" + id).css({"display": "block"});
    $("#" + id).css({"opacity": "0.9"});
    setTimeout(function() {
        close_alert(id);
    }, 4000);
}

function close_alert(id) {
    $("#" + id).css({"opacity": "0"});
    setTimeout(function() {
        $("#" + id).css({"display": "none"});
    }, 500);
}

function delete_image(image_id) {
    $.ajax({
        method: "POST",
        url: "/delete",
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify({"image_id":image_id}),
        success: function(data) {
            $("#image_" + data["id"]).remove();
            display_alert("alert_danger", "Image \"" + data["name"] + "\" supprimée avec succès !");
            closeModal();
        }
    })
}


/* === Fav Image === */
function fav_image(user_id, image_id) {
    $.ajax({
        method: "POST",
        url: "/fav",
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify({"user_id": user_id, "image_id":image_id}),
        success: function(data) {
            var image_div = $("#image_" + data["image_id"])
            if (data["action"] == "add") {
                image_div.find(".fav")[0].classList.add("selected");
                $(".content-wrapper").prepend(image_div);

            }
            else if (data["action"] == "remove") {
                image_div.find(".fav")[0].classList.remove("selected");
                $(".content-wrapper").append(image_div);
            }
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

/* === Modals === */
// Delete Modal
function openDeleteModal(image_name, image_id) {
    document.getElementById("deleteModal").style.display = "block";
    $("#modal_text").html("Es tu sûr de vouloir effacer l'image \"" + image_name + "\" ?")
    $("#modal_ok").click(function () { delete_image(image_id); });
}

// Upload Modal
function openUploadModal(user_id) {
    document.getElementById("uploadModal").style.display = "block";
}

// When the user clicks on <span> (x), close modals
function closeModal() {
    document.getElementById("deleteModal").style.display = "none";
    document.getElementById("uploadModal").style.display = "none";
    $("#upload_url").val("");
    $("#upload_name").val("");
    $("#validator1").css("display", "none");
    $("#validator2").css("display", "none");
}

// Upload validators
function preview_image() {
    url = $("#upload_url").val();
    var regex = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
    var imageTypes = ["jpg", "bmp", "png", "gif"];
    var preview = $("#upload_image");
    if (regex.test(url) && imageTypes.indexOf(url.split(".")[url.split(".").length - 1]) > - 1) {
        preview
            .attr("src", url)
            .css("display", "block");
        $(".upload_image").css("background", "transparent");
        return true;
    }
    else {
        $(".upload_image").css("background", "#202527FF");
        preview.css("display", "none");
        return false;
    }
}

function set_valid(jquery_validator) {
    jquery_validator.attr("src", "static/img/valid_icon.png");
    jquery_validator.css("display", "block");
}

function set_unvalid(jquery_validator) {
    jquery_validator.attr("src", "static/img/fail_icon.png");
    jquery_validator.css("display", "block");
}

function validate_name() {
    var image_name = $("#upload_name").val();
    if (image_name != "" && image_name.split(" ").length == 1 ) {
        set_valid($("#validator1"));
        return true;
    }
    else {
        set_unvalid($("#validator1"));
        return false;
    }
}

function validate_url() {
    var url = $("#upload_url").val();
    var regex = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
    var imageTypes = ["jpg", "bmp", "png", "gif"];
    if (regex.test(url) 
        && imageTypes.indexOf(url.split(".")[url.split(".").length - 1]) > -1) {
        set_valid($("#validator2"));
        return true;
    }
    else {
        set_unvalid($("#validator2"));
        return false;
    }
}

function uploadImage(user_id) {
    var url = $("#upload_url").val();
    var image_name = $("#upload_name").val();

    if (validate_name() && validate_url() && image_loaded) {
        $.ajax({
            method: "POST",
            url: "/upload",
            contentType: "application/json;charset=UTF-8",
            data: JSON.stringify({"user_id": user_id, "image_name": image_name,"image_url": url}),
            success: function(data) {
                sessionStorage.setItem("validUpload", image_name);
                document.location.reload();
            }
        });
    }
}

$("#upload_name").keyup(function() { validate_name(); });
$("#upload_url").keyup(function() { validate_url(); preview_image(); });
$("#upload_image")
    .on("error", function() { 
        image_loaded=false;
        set_unvalid($("#validator2"));
        $(".upload_image").css("background", "#202527FF");
        $("#upload_image").css("display", "none");
}).on("load", function() { image_loaded=true; })

window.onclick = function(e) {
    if (logout_button.hasClass("toggled") && !logout_button.is(e.target) && logout_button.has(e.target).length === 0) {
        logout_button.removeClass("toggled");
        logout_button.html("&#8677;");
    }
    
    if (e.target == document.getElementById("deleteModal") 
        || e.target == document.getElementById("uploadModal")) {
        closeModal();
    }
}

window.onload = function() {
    var image_name = sessionStorage.getItem("validUpload");
    if (image_name) {
        sessionStorage.removeItem("validUpload");
        display_alert("alert_valid", "Image \"" + image_name + "\" envoyée avec succès !");
    }
}