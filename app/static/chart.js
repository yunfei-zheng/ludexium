const ctx = document.getElementById('myChart');

new Chart(ctx, {
type: 'bar',
data: {
    labels: chartlabels,
    datasets: [{
    label: 'Playtime',
    data: chartdata,
    borderWidth: 1
    }]
},
options: {
    scales: {
        y: {
            beginAtZero: true
        }
    }
}
});