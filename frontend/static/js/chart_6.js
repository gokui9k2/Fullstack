// Extraire les années et les événements
const years = Object.keys(ufc_popularity);
const events = Object.values(ufc_popularity);

// Récupérer le contexte du canvas pour Chart.js
const ctx = document.getElementById('lineChartYear').getContext('2d');

// Créer le graphique
const lineChart = new Chart(ctx, {
    type: 'line', // Type du graphique
    data: {
        labels: years, // Labels sur l'axe X (années)
        datasets: [{
            label: 'UFC Events',
            data: events, // Données pour l'axe Y (nombre d'événements)
            borderColor: 'blue', // Couleur de la ligne
            fill: false, // Pas de remplissage sous la ligne
            tension: 0.1, // Courbure de la ligne
            pointBackgroundColor: 'blue' // Couleur des points
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Year'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Number of Events'
                }
            }
        }
    }
});