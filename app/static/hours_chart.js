const hoursChart = new Chart(
    document.getElementById('playtimeChart'),
    {
    type: 'bar',
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true
            }
        },
        plugins: {
            autocolors: {
                mode: 'labels' //important
            },
            legend: {
                display: false // This hides all text in the legend and also the labels.
            }
        }
    },
    data: {
        labels: chartlabels,
        datasets: [{
            label: 'Playtime',
            data: chartdata,
        }]
    }
});

const playtimeContainer = document.getElementById('playtimeContainer');
const totalLabels = hoursChart.data.labels.length;
if (totalLabels > 3) {
    const newWidth = 500 + ((totalLabels - 3) * 300); // can change that number for the width
    playtimeContainer.style.width = `${newWidth}px`;
}
