// Extraire les années et les événements
const years = Object.keys(ufc_popularity);
const events = Object.values(ufc_popularity);

// Récupérer le contexte du canvas pour Chart.js
const ctx = document.getElementById('lineChartYear').getContext('2d');

// Créer le graphique
const lineChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: years,
        datasets: [{
            label: 'UFC Events',
            data: events,
            borderColor: '#ff6b6b',
            fill: true,
            backgroundColor: 'rgba(255, 107, 107, 0.5)',
            tension: 0.1,
            pointRadius: 4, // Ajout des points sur la courbe
            pointBackgroundColor: '#ff6b6b', // Couleur des points
            pointBorderColor: '#fff', // Couleur de la bordure des points
            pointBorderWidth: 2 // Largeur de la bordure des points
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Year'
                },
                grid: {
                    display: false
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Number of Events'
                },
                grid: {
                    display: false
                }
            }
        }
    }
});
