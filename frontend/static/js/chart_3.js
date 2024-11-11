document.addEventListener("DOMContentLoaded", function() {
    if (typeof ratio !== 'undefined') {
        const data = {
            labels: Object.keys(ratio),  
            datasets: [{
                data: Object.values(ratio),  
                backgroundColor: ["#FF6384", "#36A2EB"],  
                hoverBackgroundColor: ["#FF6384", "#36A2EB"]
            }]
        };

        // Configuration du graphique
        const config = {
            type: 'doughnut',
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
        const myDoughnutChart = new Chart(
            document.getElementById('myDoughnutChart'),
            config
        );
    } else {
        console.error("Les données 'ratio' ne sont pas définies.");
    }
});
