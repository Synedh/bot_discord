/// <reference path="./lwd.d.ts" />

let discord = new LoginWithDiscord({
    cache: true
})

// Get the logout button
var logout_button = $('#logout');

// Get the modal
var modal = document.getElementById('myModal');

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];


/* Discord connection */
discord.onlogin = async() => {

    Array.from(document.getElementsByClassName('out')).forEach(x => {
        x.style.display = "none";
    })
    Array.from(document.getElementsByClassName('in')).forEach(x => {
        x.style.display = 'initial';
    })

    let user = await discord.fetchUser().catch(console.log);
    let guilds = await discord.fetchGuilds().catch(console.log);

    document.getElementById("profil").innerHTML = user.tag
    document.getElementById("avatar").src = user.avatarURL;
}

discord.onlogout = async() => {
    if (logout_button.hasClass('toggled')) {
        Array.from(document.getElementsByClassName('in')).forEach(x => {
            x.style.display = "none";
        });
        Array.from(document.getElementsByClassName('out')).forEach(x => {
            x.style.display = 'initial';
        });
        logout_button.html('&#8677;');
    }
    else {
        logout_button.html('Déconnexion');
    }
    logout_button.toggleClass('toggled');
}

window.onload = () => {
    discord.init();
}

async function login() {
    await discord.login('443757232476258304', Scope.Identify, Scope.Guilds);
}

async function logout() {
    await discord.logout();
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
    $('#modal_text').html("Es tu sûr de vouloir effacer l'image \"" + image_name + "\" ?")
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