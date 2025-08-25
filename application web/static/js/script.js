
    // --- GESTION DE L'HISTORIQUE ---
    async function updateHistory() {
        try {
            const response = await fetch('/history');
            const historyData = await response.json();
            const historyList = document.getElementById('history-list');
            historyList.innerHTML = '';

            if (historyData.length === 0) {
                historyList.innerHTML = `
                    <li>
                        <div>
                            <div class="name">Aucune reconnaissance récente</div>
                            <div class="confidence">L'historique apparaîtra ici</div>
                        </div>
                        <span class="timestamp">--:--</span>
                    </li>
                `;
            } else {
                historyData.forEach(item => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <div>
                            <div class="name">${item.name}</div>
                            <div class="confidence">Confiance: ${item.confidence}%</div>
                        </div>
                        <span class="timestamp">${item.timestamp}</span>
                    `;
                    historyList.appendChild(li);
                });
            }
        } catch (error) {
            console.error("Erreur historique:", error);
            const historyList = document.getElementById('history-list');
            historyList.innerHTML = `
                <li>
                    <div>
                        <div class="name">Erreur de chargement</div>
                        <div class="confidence">Impossible de récupérer l'historique</div>
                    </div>
                    <span class="timestamp">--:--</span>
                </li>
            `;
        }
    }

    // --- GESTION DE L'UPLOAD D'IMAGE ---
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const fileDisplay = document.getElementById('file-display');
    const resultContainer = document.getElementById('image-result');
    const loader = document.getElementById('loader');

    // Drag and drop functionality
    fileDisplay.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileDisplay.classList.add('drag-over');
    });

    fileDisplay.addEventListener('dragleave', () => {
        fileDisplay.classList.remove('drag-over');
    });

    fileDisplay.addEventListener('drop', (e) => {
        e.preventDefault();
        fileDisplay.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            updateFileDisplay(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            updateFileDisplay(e.target.files[0]);
        }
    });

    function updateFileDisplay(file) {
        fileDisplay.innerHTML = `
            <div>
                <div style="font-size: 2rem; margin-bottom: 10px;">✅</div>
                <div style="font-weight: 600;">${file.name}</div>
                <div style="font-size: 0.9rem; opacity: 0.7; margin-top: 5px;">
                    ${(file.size / 1024 / 1024).toFixed(2)} MB
                </div>
            </div>
        `;
    }

    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        if (fileInput.files.length === 0) {
            resultContainer.innerHTML = '<div class="error-message">⚠️ Veuillez sélectionner un fichier image.</div>';
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        // Afficher le loader et vider le résultat précédent
        loader.classList.add('show');
        resultContainer.innerHTML = '';
        
        // Ajouter l'état de chargement
        const card = uploadForm.closest('.card');
        card.classList.add('loading');

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                let predictionsHtml = '';
                if (data.predictions.length > 0) {
                    predictionsHtml = '<div class="results-grid">';
                    data.predictions.forEach(p => {
                        predictionsHtml += `
                            <div class="prediction-item">
                                <span class="prediction-name">${p.name}</span>
                                <span class="prediction-confidence">${p.confidence}%</span>
                            </div>
                        `;
                    });
                    predictionsHtml += '</div>';
                } else {
                    predictionsHtml = '<div class="error-message">❌ Aucun visage détecté dans l\'image.</div>';
                }

                resultContainer.innerHTML = `
                    <img src="${data.image_data}" alt="Image analysée" />
                    <div style="margin-top: 20px;">
                        <h3 style="margin-bottom: 15px; color: white;">🎯 Résultats de l'analyse</h3>
                        ${predictionsHtml}
                    </div>
                `;
            } else {
                resultContainer.innerHTML = `<div class="error-message">❌ Erreur: ${data.error}</div>`;
            }

        } catch (error) {
            console.error('Erreur upload:', error);
            resultContainer.innerHTML = `<div class="error-message">❌ Une erreur est survenue lors de l'analyse.</div>`;
        } finally {
            // Cacher le loader et retirer l'état de chargement
            loader.classList.remove('show');
            card.classList.remove('loading');
        }
    });

    // --- INITIALISATION ---
    document.addEventListener('DOMContentLoaded', () => {
        updateHistory();
        setInterval(updateHistory, 3000); // Rafraîchir toutes les 3 secondes
    });
