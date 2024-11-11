// Vérifiez que les données sont disponibles
if (typeof coordinatesData !== 'undefined') {
    const ctx = document.getElementById('geoMapChart').getContext('2d');

    // Fonction pour déterminer la taille de la bulle en fonction de la valeur de "count"
    const calculateRadius = (count) => {
        return Math.sqrt(count) * 2; // Ajustez le multiplicateur pour que les bulles restent proportionnelles
    };

    // Préparation des données pour le graphique
    const bubbleData = coordinatesData.map(location => ({
        x: location.longitude,
        y: location.latitude,
        r: calculateRadius(location.count),
        location: location.location,  // Ajout de la ville
        count: location.count
    }));

    // Création du graphique
    new Chart(ctx, {
        type: 'bubble',
        data: {
            datasets: [{
                label: 'Location',
                data: bubbleData,
                backgroundColor: 'rgba(0, 123, 255, 0.5)', // Couleur des bulles
                borderColor: '#007bff',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Longitude'
                    },
                    min: -180,
                    max: 180,
                    ticks: {
                        stepSize: 30
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Latitude'
                    },
                    min: -90,
                    max: 90,
                    ticks: {
                        stepSize: 15
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const { location, count } = context.raw;
                            return `${location}: ${count} occurrences`;
                        }
                    }
                }
            }
        }
    });
} else {
    console.error("Les données de coordonnées ne sont pas définies.");
}
