document.addEventListener('DOMContentLoaded', () => {
    // === EXTRACTION PAGE LOGIC ===
    const dropZone = document.getElementById('drop-zone');

    if (dropZone) {
        initExtractionPage(dropZone);
    }

    // === GENERATION PAGE LOGIC ===
    const generateForm = document.getElementById('generateForm');

    if (generateForm) {
        initGenerationPage(generateForm);
    }

    // === DIRECT FILL PAGE LOGIC ===
    const directFillForm = document.getElementById('directFillForm');

    if (directFillForm) {
        initDirectFillPage(directFillForm);
    }
});

function initExtractionPage(dropZone) {
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');
    const extractBtn = document.getElementById('extract-btn');
    const resultsArea = document.getElementById('results-area');
    const resultsTable = document.getElementById('results-table');
    const downloadBtn = document.getElementById('download-btn');
    const spinner = document.querySelector('.loading-spinner');
    const btnText = extractBtn.querySelector('span');

    let selectedFiles = [];
    let extractedData = [];

    // Drag & Drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    function handleFiles(files) {
        const newFiles = Array.from(files).filter(file => file.type === 'application/pdf');

        if (newFiles.length === 0 && files.length > 0) {
            alert('Only PDF files are allowed.');
            return;
        }

        selectedFiles = [...selectedFiles, ...newFiles];
        updateFileList();
        updateButtonState();
    }

    function updateFileList() {
        fileList.innerHTML = '';
        selectedFiles.forEach((file, index) => {
            const item = document.createElement('div');
            item.className = 'file-item';
            item.innerHTML = `
                <span>${file.name}</span>
                <span class="remove-file" data-index="${index}">×</span>
            `;
            fileList.appendChild(item);
        });

        // Add event listeners to remove buttons
        document.querySelectorAll('.remove-file').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.getAttribute('data-index'));
                selectedFiles.splice(index, 1);
                updateFileList();
                updateButtonState();
            });
        });
    }

    function updateButtonState() {
        extractBtn.disabled = selectedFiles.length === 0;
    }

    // Extraction
    extractBtn.addEventListener('click', async () => {
        if (selectedFiles.length === 0) return;

        // UI Loading State
        extractBtn.disabled = true;
        btnText.textContent = 'Processing...';
        spinner.classList.remove('hidden');
        resultsArea.classList.add('hidden');

        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await fetch('/extract', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Extraction failed');

            const data = await response.json();
            extractedData = data.results;
            renderTable(extractedData);
            resultsArea.classList.remove('hidden');

        } catch (error) {
            console.error(error);
            alert('An error occurred during extraction.');
        } finally {
            // Reset UI State
            extractBtn.disabled = false;
            btnText.textContent = 'Extract Data';
            spinner.classList.add('hidden');
        }
    });

    function renderTable(data) {
        const thead = resultsTable.querySelector('thead');
        const tbody = resultsTable.querySelector('tbody');

        thead.innerHTML = '';
        tbody.innerHTML = '';

        if (data.length === 0) return;

        // Collect all unique field keys across all documents to build headers
        const allKeys = new Set();
        data.forEach(doc => {
            if (doc.fields) {
                Object.keys(doc.fields).forEach(key => allKeys.add(key));
            }
        });

        const headers = ['Filename', ...Array.from(allKeys)];

        // Create Header Row
        const trHead = document.createElement('tr');
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            trHead.appendChild(th);
        });
        thead.appendChild(trHead);

        // Create Body Rows
        data.forEach(doc => {
            const tr = document.createElement('tr');

            // Filename Cell
            const tdName = document.createElement('td');
            tdName.textContent = doc.filename;
            tr.appendChild(tdName);

            // Field Cells
            headers.slice(1).forEach(key => {
                const td = document.createElement('td');
                td.textContent = (doc.fields && doc.fields[key]) ? doc.fields[key] : '';
                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });
    }

    // CSV Download
    downloadBtn.addEventListener('click', () => {
        if (extractedData.length === 0) return;

        // Regenerate headers and rows similar to renderTable logic
        const allKeys = new Set();
        extractedData.forEach(doc => {
            if (doc.fields) {
                Object.keys(doc.fields).forEach(key => allKeys.add(key));
            }
        });
        const headers = ['Filename', ...Array.from(allKeys)];

        let csvContent = headers.join(',') + '\n';

        extractedData.forEach(doc => {
            const row = [doc.filename];
            headers.slice(1).forEach(key => {
                let val = (doc.fields && doc.fields[key]) ? doc.fields[key] : '';

                // Prevent Excel from auto-converting numerical/fractional values to dates
                // Rule: If field name doesn't contain "date" AND value looks numeric/fractional
                const isDateColumn = key.toLowerCase().includes('date');
                const isNumericLike = /^[\d\s\/\.\-]+$/.test(val) && /\d/.test(val);

                if (!isDateColumn && isNumericLike) {
                    val = val.replace(/"/g, '""');
                    val = `="${val}"`;
                } else {
                    val = val.replace(/"/g, '""');
                    if (val.includes(',') || val.includes('"') || val.includes('\n')) {
                        val = `"${val}"`;
                    }
                }
                row.push(val);
            });
            csvContent += row.join(',') + '\n';
        });

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', 'extracted_data.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
}

function initGenerationPage(form) {
    const inputs = ['demographics', 'clinical', 'template'];
    const generateBtn = document.getElementById('generateBtn');
    const loader = generateBtn.querySelector('.loader');
    const btnText = generateBtn.querySelector('.btn-text');
    const statusMsg = document.getElementById('statusMessage');

    // File input listeners for name display
    inputs.forEach(id => {
        const input = document.getElementById(id);
        const nameDisplay = document.getElementById(id + '-name');

        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                nameDisplay.textContent = e.target.files[0].name;
                nameDisplay.style.color = 'var(--accent)';
            } else {
                nameDisplay.textContent = 'No file chosen';
                nameDisplay.style.color = 'var(--text-secondary)';
            }
        });
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Reset UI
        generateBtn.disabled = true;
        btnText.textContent = 'Generating...';
        loader.classList.remove('hidden');
        statusMsg.classList.add('hidden');
        statusMsg.className = 'status-message hidden'; // remove success/error classes

        const formData = new FormData(form);

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const text = await response.text();
                let errorMsg = 'Generation failed';
                try {
                    const errData = JSON.parse(text);
                    errorMsg = errData.error || errorMsg;
                } catch (e) {
                    // Not JSON, analyze text
                    if (text.includes('<!DOCTYPE html>')) {
                        const match = text.match(/<title>(.*?)<\/title>/i);
                        if (match) errorMsg = `Server Error: ${match[1]}`;
                        else errorMsg = `Server Error: ${response.status} ${response.statusText}`;
                    } else {
                        errorMsg = text.substring(0, 100) || `Server Error: ${response.status}`;
                    }
                }
                throw new Error(errorMsg);
            }

            // Handle ZIP download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'generated_patients.zip';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

            showStatus('Successfully generated and downloaded ZIP!', 'success');

        } catch (error) {
            console.error('Generation Error:', error);
            showStatus(error.message, 'error');
        } finally {
            generateBtn.disabled = false;
            btnText.textContent = 'Generate & Download ZIP';
            loader.classList.add('hidden');
        }
    });

    function showStatus(msg, type) {
        statusMsg.textContent = msg;
        statusMsg.classList.remove('hidden');
        statusMsg.classList.add('status-' + type);
    }
}

function initDirectFillPage(form) {
    const inputs = ['csv_file', 'template'];
    const generateBtn = document.getElementById('directFillBtn');
    const loader = generateBtn.querySelector('.loader');
    const btnText = generateBtn.querySelector('.btn-text');
    const statusMsg = document.getElementById('statusMessage');

    // File input listeners for name display
    inputs.forEach(id => {
        const input = document.getElementById(id);
        if (!input) return;

        const nameDisplay = document.getElementById(id.replace('_', '-') + '-name') || document.getElementById(id + '-name');

        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                nameDisplay.textContent = e.target.files[0].name;
                nameDisplay.style.color = 'var(--accent)';
            } else {
                nameDisplay.textContent = 'No file chosen';
                nameDisplay.style.color = 'var(--text-secondary)';
            }
        });
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Reset UI
        generateBtn.disabled = true;
        btnText.textContent = 'Processing...';
        loader.classList.remove('hidden');
        statusMsg.classList.add('hidden');
        statusMsg.className = 'status-message hidden';

        const formData = new FormData(form);

        try {
            const response = await fetch('/direct-fill', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const text = await response.text();
                let errorMsg = 'Fill failed';
                try {
                    const errData = JSON.parse(text);
                    errorMsg = errData.error || errorMsg;
                } catch (e) {
                    // Not JSON, analyze text
                    if (text.includes('<!DOCTYPE html>')) {
                        const match = text.match(/<title>(.*?)<\/title>/i);
                        if (match) errorMsg = `Server Error: ${match[1]}`;
                        else errorMsg = `Server Error: ${response.status} ${response.statusText}`;
                    } else {
                        errorMsg = text.substring(0, 100) || `Server Error: ${response.status}`;
                    }
                }
                throw new Error(errorMsg);
            }

            // Handle ZIP download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'filled_forms.zip';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

            showStatus('Successfully filled and downloaded ZIP!', 'success');

        } catch (error) {
            console.error('Fill Error:', error);
            showStatus(error.message, 'error');
        } finally {
            generateBtn.disabled = false;
            btnText.textContent = 'Fill & Download ZIP';
            loader.classList.add('hidden');
        }
    });

    function showStatus(msg, type) {
        statusMsg.textContent = msg;
        statusMsg.classList.remove('hidden');
        statusMsg.classList.add('status-' + type);
    }
}
