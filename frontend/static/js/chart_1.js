document.addEventListener('DOMContentLoaded', function () {
    try {
        // Vérification des données pour le graphique des hommes
        console.log('Data received for male:', heatmapMaleData);

        if (!heatmapMaleData || !heatmapMaleData.heatmap_data) {
            throw new Error('Structure de données invalide pour heatmapMaleData');
        }

        const maleWeightClasses = heatmapMaleData.heatmap_data.weight_class;
        const maleStrikePercentages = heatmapMaleData.heatmap_data.avg_SIG_STR_pct.map(value => value * 100);

        if (!maleWeightClasses || !maleStrikePercentages) {
            throw new Error('Données manquantes pour male weight_class ou avg_SIG_STR_pct');
        }

        // Récupération du canvas pour le graphique
        const maleCanvas = document.getElementById('heatmapMaleChart');
        if (!maleCanvas) {
            throw new Error("Canvas element with id 'heatmapMaleChart' not found.");
        }

        const ctxMale = maleCanvas.getContext('2d');

        // Trouver l'indice de la barre avec la valeur maximale
        const maxPercentage = Math.max(...maleStrikePercentages);
        const maxIndex = maleStrikePercentages.indexOf(maxPercentage);

        // Appliquer une couleur différente à la barre maximale
        const backgroundColors = maleStrikePercentages.map((value, index) => {
            if (index === maxIndex) {
                return 'rgba(255, 99, 132, 1)'; // Couleur différente pour la barre la plus grande
            } else {
                const intensity = Math.min(1, value / 100);
                return `rgba(0, 128, 0, ${intensity})`; // Couleur pour les autres barres
            }
        });

        new Chart(ctxMale, {
            type: 'bar',
            data: {
                labels: maleWeightClasses,
                datasets: [{
                    label: 'Significant Strike Percentage',
                    data: maleStrikePercentages,
                    backgroundColor: backgroundColors,
                    borderColor: 'rgba(0, 128, 0, 0.8)',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Significant Strike Percentage (%)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Weight Class'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Significant Strike Percentage by Weight Class (Male)',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });

    } catch (error) {
        // Affiche une erreur dans la console et sur la page web
        console.error("Erreur lors du rendu du graphique pour les données masculines :", error);
        const errorDisplay = document.getElementById('errorDisplay');
        if (errorDisplay) {
            errorDisplay.textContent = "Erreur lors du rendu du graphique masculin : " + error.message;
        }
    }
});
