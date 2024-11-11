document.addEventListener('DOMContentLoaded', function () {
    try {
        // Vérification des données pour le graphique en ligne
        console.log('Data received for line chart (male and female):', lineplotMaleData, lineplotFemaleData);

        // Vérification des données
        if (!lineplotMaleData || !lineplotFemaleData) {
            throw new Error('Données manquantes pour lineplotMaleData ou lineplotFemaleData');
        }

        // Vérification de la présence des propriétés nécessaires dans les données
        if (!lineplotMaleData.Age || !lineplotMaleData.data) {
            throw new Error('Données manquantes pour les âges ou les valeurs de strikes moyens (male)');
        }
        if (!lineplotFemaleData.Age || !lineplotFemaleData.data) {
            throw new Error('Données manquantes pour les âges ou les valeurs de strikes moyens (female)');
        }

        const lineChartCanvas = document.getElementById('lineChart');
        if (!lineChartCanvas) {
            throw new Error("Canvas element with id 'lineChart' not found.");
        }

        const ctxLineChart = lineChartCanvas.getContext('2d');
        new Chart(ctxLineChart, {
            type: 'line',
            data: {
                labels: lineplotMaleData.Age,  // Âges des combattants (les mêmes pour les deux genres)
                datasets: [
                    {
                        label: 'MALE - Average SIG STR',
                        data: lineplotMaleData.data,
                        borderColor: 'rgba(54, 162, 235, 1)',  // Couleur des lignes pour les hommes
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        fill: true,
                        tension: 0.1
                    },
                    {
                        label: 'FEMALE - Average SIG STR',
                        data: lineplotFemaleData.data,
                        borderColor: 'rgba(255, 99, 132, 1)',  // Couleur des lignes pour les femmes
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        fill: true,
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Average Significant Strikes Landed by Age and Gender'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Age'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Average SIG STR Landed'
                        },
                        beginAtZero: true
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error:', error);
        
        // Afficher l'erreur dans la console et dans l'élément HTML
        const errorDisplay = document.getElementById('errorDisplay');
        if (errorDisplay) {
            errorDisplay.textContent = 'Erreur lors du chargement du graphique : ' + error.message;
        }
    }
});
