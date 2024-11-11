// Données
const data = {
    2010: 210, 
    2011: 295, 
    2012: 333, 
    2013: 376, 
    2014: 494, 
    2015: 464, 
    2016: 483, 
    2017: 440, 
    2018: 471, 
    2019: 507, 
    2020: 451, 
    2021: 372
};

// Extraire les années et les événements
const years = Object.keys(data);
const events = Object.values(data);

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
