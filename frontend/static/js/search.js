document.getElementById('searchButton').addEventListener('click', function() {
    const fighterName = document.getElementById('fighter_name').value;
    if (fighterName.length < 2) {
        alert("Veuillez entrer au moins deux lettres.");
        return;
    }

    fetch(`/search?fighter_name=${encodeURIComponent(fighterName)}`)
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById('searchResults');
            resultsContainer.innerHTML = ''; // Clear previous results
            if (data.error) {
                resultsContainer.innerHTML = `<div class="error">${data.error}</div>`;
            } else {
                const table = document.createElement('table');
                table.innerHTML = `
                    <thead>
                        <tr>
                            <th>Nom</th>
                            <th>Genre</th>
                            <th>Taille (cm)</th>
                            <th>Stance</th>
                            <th>Poids (lbs)</th>
                            <th>DQ</th>
                            <th>KO/TKO</th>
                            <th>M-DEC</th>
                            <th>Overturned</th>
                            <th>S-DEC</th>
                            <th>SUB</th>
                            <th>U-DEC</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.results.map(fighter => `
                            <tr>
                                <td>${fighter.nom}</td>
                                <td>${fighter.gender}</td>
                                <td>${fighter.height_cms}</td>
                                <td>${fighter.stance}</td>
                                <td>${fighter.weight_lbs}</td>
                                <td>${fighter.DQ}</td>
                                <td>${fighter['KO/TKO']}</td>
                                <td>${fighter['M-DEC']}</td>
                                <td>${fighter.Overturned}</td>
                                <td>${fighter['S-DEC']}</td>
                                <td>${fighter.SUB}</td>
                                <td>${fighter['U-DEC']}</td>
                            </tr>`).join('')}
                    </tbody>`;
                resultsContainer.appendChild(table);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});
