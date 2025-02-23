document.addEventListener('DOMContentLoaded', function () {
    // Create grid lines
    createGridLines();

    // Elements
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    const previewContainer = document.getElementById('previewContainer');
    const resetBtn = document.getElementById('resetBtn');
    const stitchBtn = document.getElementById('stitchBtn');
    const loading = document.getElementById('loading');
    const resultImg = document.getElementById('resultImg');
    const downloadBtn = document.getElementById('downloadBtn');
    const emptyState = document.getElementById('emptyState');
    const processSection = document.getElementById('processSection');
    const processTimeline = document.getElementById('processTimeline');

    // Files array
    let selectedFiles = [];

    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('highlight');
    }

    function unhighlight() {
        dropZone.classList.remove('highlight');
    }

    // Handle drop
    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Browse button
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    // Process files
    function handleFiles(files) {
        files = [...files];
        files.forEach(previewFile);
        checkStitchButton();
    }

    function previewFile(file) {
        if (!file.type.match('image.*')) {
            return;
        }

        // Add to files array
        selectedFiles.push(file);

        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function () {
            const previewItem = document.createElement('div');
            previewItem.className = 'preview-item';
            previewItem.innerHTML = `
                <img src="${reader.result}" class="preview-img" alt="${file.name}">
                <div class="remove-btn"><i class="fas fa-times"></i></div>
            `;

            const removeBtn = previewItem.querySelector('.remove-btn');
            removeBtn.addEventListener('click', function () {
                const index = selectedFiles.indexOf(file);
                if (index > -1) {
                    selectedFiles.splice(index, 1);
                }
                previewItem.remove();
                checkStitchButton();

                // Show empty state if no images
                if (selectedFiles.length === 0) {
                    previewContainer.style.display = 'none';
                }
            });

            previewContainer.appendChild(previewItem);

            // Hide empty state when images are ajoutées
            if (selectedFiles.length > 0) {
                previewContainer.style.display = 'grid';
            }
        }
    }

    // Check if stitch button should be enabled
    function checkStitchButton() {
        stitchBtn.disabled = selectedFiles.length < 2;
    }

    // Reset
    resetBtn.addEventListener('click', function () {
        selectedFiles = [];
        previewContainer.innerHTML = '';
        previewContainer.style.display = 'none';
        resultImg.style.display = 'none';
        downloadBtn.style.display = 'none';
        emptyState.style.display = 'flex';
        processSection.classList.add('hidden');
        processTimeline.innerHTML = '';
        checkStitchButton();
    });

    // Fonction pour afficher les étapes du processus
    function displayProcessSteps(processSteps) {
        const processTimeline = document.getElementById("processTimeline");
        processTimeline.innerHTML = "";
    
        processSteps.forEach(item => {
            // Créer un conteneur pour chaque étape
            const stepContainer = document.createElement("div");
            stepContainer.classList.add("process-step");
    
            // Créer et ajouter le titre de l'étape
            const stepTitle = document.createElement("h3");
            stepTitle.textContent = item.step;
            stepContainer.appendChild(stepTitle);
    
            // Créer l'image et lui ajouter la classe "step-image"
            const stepImage = document.createElement("img");
            stepImage.classList.add("step-image"); 
            stepImage.src = `data:image/jpeg;base64,${item.image}`;
            stepImage.alt = item.step;
            stepContainer.appendChild(stepImage);
    
            // Ajouter le conteneur de l'étape à la timeline
            processTimeline.appendChild(stepContainer);
        });
    
        // Afficher la section si elle est cachée
        document.getElementById("processSection").classList.remove("hidden");
    }
    

    // Create panorama
    stitchBtn.addEventListener('click', async function () {
        if (selectedFiles.length < 2) {
            alert('Veuillez sélectionner au moins 2 images');
            return;
        }

        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('images', file);
        });

        loading.style.display = 'flex';
        resultImg.style.display = 'none';
        downloadBtn.style.display = 'none';
        emptyState.style.display = 'none';
        processSection.classList.add('hidden');
        processTimeline.innerHTML = "";

        try {
            const response = await fetch('/stitch', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            const data = await response.json();
            
            // Afficher l'image résultante
            resultImg.src = data.result_path;
            resultImg.style.display = 'block';
            downloadBtn.style.display = 'inline-block';

            // Afficher les étapes du processus si disponibles
            if (data.process_steps && data.process_steps.length > 0) {
                displayProcessSteps(data.process_steps);
            }

            // Configure download button
            downloadBtn.addEventListener('click', function () {
                const a = document.createElement('a');
                a.href = data.result_path;
                a.download = 'panorama.jpg';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            });

        } catch (error) {
            alert('Erreur: ' + error.message);
            emptyState.style.display = 'flex';
        } finally {
            loading.style.display = 'none';
        }
    });

    // Create grid lines
    function createGridLines() {
        const horizontalLines = document.getElementById('horizontalLines');
        const verticalLines = document.getElementById('verticalLines');

        const numHorizontalLines = 20;
        const numVerticalLines = 20;

        for (let i = 0; i < numHorizontalLines; i++) {
            const line = document.createElement('div');
            line.className = 'line horizontal-line';
            line.style.top = `${(i / numHorizontalLines) * 100}%`;
            line.style.animationDelay = `${i * 0.1}s`;
            horizontalLines.appendChild(line);
        }

        for (let i = 0; i < numVerticalLines; i++) {
            const line = document.createElement('div');
            line.className = 'line vertical-line';
            line.style.left = `${(i / numVerticalLines) * 100}%`;
            line.style.animationDelay = `${i * 0.1}s`;
            verticalLines.appendChild(line);
        }
    }
});
