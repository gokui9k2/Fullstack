document.addEventListener('DOMContentLoaded', function () {
    try {
        // --- Graphique Heatmap pour les données féminines ---
        console.log('Data received for female:', heatmapFemaleData);
        
        // Vérifiez si les données sont bien définies et ont la structure attendue
        if (!heatmapFemaleData || !heatmapFemaleData.heatmap_data) {
            throw new Error('Structure de données invalide pour heatmapFemaleData');
        }
        
        const femaleWeightClasses = heatmapFemaleData.heatmap_data.weight_class;
        const femaleStrikePercentages = heatmapFemaleData.heatmap_data.avg_SIG_STR_pct.map(value => value * 100);
        
        if (!femaleWeightClasses || !femaleStrikePercentages) {
            throw new Error('Données manquantes pour female weight_class ou avg_SIG_STR_pct');
        }

        const femaleCanvas = document.getElementById('heatmapFemaleChart');
        if (femaleCanvas) {
            const ctxFemale = femaleCanvas.getContext('2d');
            
            // Trouver l'indice de la barre avec la valeur maximale
            const maxPercentage = Math.max(...femaleStrikePercentages);
            const maxIndex = femaleStrikePercentages.indexOf(maxPercentage);

            // Appliquer une couleur différente à la barre maximale
            const backgroundColors = femaleStrikePercentages.map((value, index) => {
                if (index === maxIndex) {
                    return 'rgba(255, 99, 132, 1)'; // Couleur différente pour la barre la plus grande
                } else {
                    const intensity = Math.min(1, value / 100);
                    return `rgba(0, 128, 0, ${intensity})`; // Couleur pour les autres barres
                }
            });

            new Chart(ctxFemale, {
                type: 'bar',
                data: {
                    labels: femaleWeightClasses,
                    datasets: [{
                        label: 'Significant Strike Percentage',
                        data: femaleStrikePercentages,
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
                            text: 'Significant Strike Percentage by Weight Class (Female)',
                            font: {
                                size: 16
                            }
                        }
                    }
                }
            });
        } else {
            throw new Error("Canvas element with id 'heatmapFemaleChart' not found.");
        }

    } catch (error) {
        console.error("Erreur lors du rendu du graphique : ", error);
        document.getElementById('errorDisplay').textContent = "Erreur lors du rendu du graphique : " + error.message;
    }
});
