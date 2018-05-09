/// <reference path="./lwd.d.ts" />

let discord = new LoginWithDiscord({
    cache: true
})

discord.onlogin = async() => {

    Array.from(document.getElementsByClassName('out')).forEach(x => {
        x.style.display = "none";
    })
    Array.from(document.getElementsByClassName('in')).forEach(x => {
        x.style.display = 'inline';
    })

    let user = await discord.fetchUser().catch(console.log);
    let guilds = await discord.fetchGuilds().catch(console.log);

    document.getElementById("profil").innerHTML = user.tag
    document.getElementById("avatar").src = user.avatarURL;

    console.log(user);
    console.log(guilds);
}

discord.onlogout = async() => {
    Array.from(document.getElementsByClassName('in')).forEach(x => {
        x.style.display = "none";
    });
    Array.from(document.getElementsByClassName('out')).forEach(x => {
        x.style.display = 'inline';
    });
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
