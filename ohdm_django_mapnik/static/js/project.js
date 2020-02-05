/* set map height */
function setLayoutSize() {
    let navHeight = $("nav").outerHeight();
    console.log(navHeight);
    let mapHeight = $(window).height() - navHeight;

    $("#mapid").css('height', mapHeight);
}

setLayoutSize();
$(window).on('resize', function () {
    setLayoutSize();
});


let ohdmMap = null;

function setMapView() {
    // get date from datepicker
    let dateArray = $("#datepicker").val().split("/");
    // tile server url /tile/YYYY/MM/DD/z/x/y/tile.png
    ohdmMap = L.map('mapid').setView([52.520008, 13.404954], 13);
    L.tileLayer('/tile/' + dateArray[2] + '/' + dateArray[0] + '/' + dateArray[1] + '/{z}/{x}/{y}/tile.png', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a></a>',
        maxZoom: 18,
    }).addTo(ohdmMap);
}

setMapView();

$('#datepicker').datepicker({
    endDate: new Date(),
    startView: 2,
    todayHighlight: true
});

$("#datepicker-save-btn").button().click(function () {
    ohdmMap.off();
    ohdmMap.remove();
    setMapView();
});

