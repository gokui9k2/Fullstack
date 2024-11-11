// Exécuter le code une fois le DOM chargé
document.addEventListener("DOMContentLoaded", function() {
    // Vérifie que `finish` est bien défini
    if (typeof finish !== 'undefined') {
        // Préparation des données du polar area chart
        const data = {
            labels: Object.keys(finish),  // ["U-DEC", "KO/TKO", "SUB", "S-DEC", "M-DEC", "DQ", "Overturned"]
            datasets: [{
                data: Object.values(finish),  // [36.315, 30.535, 17.442, ...]
                backgroundColor: [
                    "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40", "#C9CBCF"
                ],
                hoverBackgroundColor: [
                    "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40", "#C9CBCF"
                ]
            }]
        };

        // Configuration du graphique
        const config = {
            type: 'polarArea',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        enabled: true,
                    }
                }
            }
        };

        // Création du graphique
        const myPolarChart = new Chart(
            document.getElementById('myPolarChart'),
            config
        );
    } else {
        console.error("Les données 'finish' ne sont pas définies.");
    }
});
