var stats = JSON.parse(appConfig.stats);

// Build RGB color from string
function hashCode(str) {
    var hash = 0;
    for (var i = 0; i < str.length; i++)
       hash = str.charCodeAt(i) + ((hash << 5) - hash);
    return hash;
} 

function intToRGB(i){
    var c = (i & 0x00FFFFFF).toString(16).toUpperCase();
    return "00000".substring(0, 6 - c.length) + c;
}

Chart.defaults.global.defaultFontColor = 'white';
var ctx = document.getElementById('chart').getContext('2d');
var chart = new Chart(ctx, {
    // The type of chart we want to create
    type: 'line',

    // The data for our dataset
    data: {
        labels: stats["labels"],
        datasets: []
    },

    // Configuration options go here
    options: {
        scales: {
            yAxes: [{
                stacked: true,
                gridLines:{
                    color:"rgba(255, 255, 255, 0.25)",
                    zeroLineColor:"rgba(255, 255, 255, 0.25)"
                }
            }],
            xAxes: [{
                gridLines:{
                    color:"rgba(255, 255, 255, 0.25)",
                    zeroLineColor:"rgba(255, 255, 255, 0.25)"
                }
            }]
        },
        tooltipTemplate: "<%=datasetLabel%> : <%= value %>"
    }
});

var datasets = function() {
    datasets = []
    data = stats['data'];
    for (var i = 0; i < data.length; i++) {
        color = "#" + intToRGB(hashCode(data[i]['label']));
        datasets.push({
            label: data[i]['label'],
            backgroundColor: color,
            borderColor: color,
            data: function() {
                set = []
                for (var j = 0; j < stats["labels"].length; j++) {
                    set.push(data[i]["content"][stats["labels"][j]])
                }
                console.log(set);
                return set;
            }(data[i])
        });
    }
    return datasets;
}

chart.data.datasets = datasets();
chart.update();