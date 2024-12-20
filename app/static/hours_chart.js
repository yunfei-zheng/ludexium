new Chart(
    document.getElementById('playtimeChart'),
    {
    type: 'bar',
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        },
        plugins: {
            autocolors: {
                mode: 'labels' //important
            }
        }
    },
    data: {
        labels: chartlabels,
        datasets: [{
            label: 'Playtime',
            data: chartdata,
            borderWidth: 1
        }]
    }
});