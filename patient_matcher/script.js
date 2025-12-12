// State to hold uploaded data
let demographicsData = null;
let clinicalData = null;
let matchedData = [];

// DOM Elements
const dropZoneDemographics = document.getElementById('drop-zone-demographics');
const dropZoneClinical = document.getElementById('drop-zone-clinical');
const inputDemographics = document.getElementById('input-demographics');
const inputClinical = document.getElementById('input-clinical');
const statusDemographics = document.getElementById('status-demographics');
const statusClinical = document.getElementById('status-clinical');
const btnMatch = document.getElementById('btn-match');
const btnDownload = document.getElementById('btn-download');
const btnMock = document.getElementById('btn-mock');
const resultsArea = document.getElementById('results-area');

// Event Listeners for File Inputs
inputDemographics.addEventListener('change', (e) => handleFileSelect(e, 'demographics'));
inputClinical.addEventListener('change', (e) => handleFileSelect(e, 'clinical'));

// Drag and Drop Logic
setupDragAndDrop(dropZoneDemographics, inputDemographics);
setupDragAndDrop(dropZoneClinical, inputClinical);

// Button Listeners
btnMatch.addEventListener('click', generateMatches);
btnDownload.addEventListener('click', downloadCSV);
btnMock.addEventListener('click', useMockData);

// Function to handle Drag & Drop setup
function setupDragAndDrop(dropZone, inputElement) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-over'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-over'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            inputElement.files = files;
            // Trigger change event manually
            const event = new Event('change');
            inputElement.dispatchEvent(event);
        }
    });
}

function handleFileSelect(event, type) {
    const file = event.target.files[0];
    if (!file) return;

    Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: function (results) {
            if (type === 'demographics') {
                demographicsData = results.data;
                statusDemographics.textContent = `Loaded ${demographicsData.length} records`;
                dropZoneDemographics.classList.add('loaded');
            } else {
                clinicalData = results.data;
                statusClinical.textContent = `Loaded ${clinicalData.length} records`;
                dropZoneClinical.classList.add('loaded');
            }
            checkReadyState();
        },
        error: function (err) {
            console.error("CSV Error:", err);
            alert("Error parsing CSV file.");
        }
    });
}

function checkReadyState() {
    if (demographicsData && demographicsData.length > 0 &&
        clinicalData && clinicalData.length > 0) {
        btnMatch.removeAttribute('disabled');
    }
}

function generateMatches() {
    resultsArea.innerHTML = '';
    resultsArea.classList.remove('hidden');

    // Deep copy to avoid mutating original source if re-run
    const patients = [...demographicsData];
    const originalClinical = [...clinicalData];

    // Shuffle Clinical Data to randomize matches
    const shuffledClinical = shuffleArray(originalClinical);

    // Determine the number of matches (min length of both arrays)
    const matchCount = Math.min(patients.length, shuffledClinical.length);

    matchedData = []; // Clear previous matches

    for (let i = 0; i < matchCount; i++) {
        // Merge objects for storage
        const mergedRecord = { ...patients[i], ...shuffledClinical[i] };
        matchedData.push(mergedRecord);
        createResultCard(patients[i], shuffledClinical[i]);
    }

    // Enable download button
    btnDownload.removeAttribute('disabled');

    // Scroll to results
    resultsArea.scrollIntoView({ behavior: 'smooth' });
}

function createResultCard(patient, clinical) {
    const card = document.createElement('div');
    card.className = 'result-card';

    // Combine keys for display, filtering out empty ones
    const patientKeys = Object.keys(patient).filter(k => patient[k]);
    const clinicalKeys = Object.keys(clinical).filter(k => clinical[k]);

    let html = `<h3>Match Found</h3>`;

    html += `<div class="section-title" style="margin-top:0.5rem; font-size:0.8rem; text-transform:uppercase; color:var(--primary);">Demographics</div>`;
    patientKeys.forEach(key => {
        html += `
            <div class="data-row">
                <span class="data-label">${key}</span>
                <span class="data-value">${patient[key]}</span>
            </div>
        `;
    });

    html += `<div class="section-title" style="margin-top:1rem; font-size:0.8rem; text-transform:uppercase; color:var(--success);">Clinical Details</div>`;
    clinicalKeys.forEach(key => {
        html += `
            <div class="data-row">
                <span class="data-label">${key}</span>
                <span class="data-value">${clinical[key]}</span>
            </div>
        `;
    });

    card.innerHTML = html;
    resultsArea.appendChild(card);
}

// Fisher-Yates Shuffle
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

function downloadCSV() {
    if (!matchedData || matchedData.length === 0) return;

    // Create a deep copy and sanitize for Excel
    const exportData = matchedData.map(row => {
        const newRow = { ...row };
        Object.keys(newRow).forEach(key => {
            let val = newRow[key];
            // If header does NOT contain 'date' (case-insensitive)
            if (key.toLowerCase().indexOf('date') === -1) {
                // Check for values that Excel aggressively converts to dates (e.g., "6/6", "1-2", "Sep-20")
                // Strategy: Wrap in ="VALUE" to force string interpretation
                if (val && typeof val === 'string' && (/^\d+[\/\-]\d+/.test(val) || /^[a-zA-Z]{3}-\d+/.test(val))) {
                    newRow[key] = `="${val}"`;
                }
                // Fallback for other numeric strings starting with digits using tab if simpler
                else if (val && typeof val === 'string' && /^\d/.test(val) && val.includes('/')) {
                    newRow[key] = `="${val}"`;
                }
            }
        });
        return newRow;
    });

    const csv = Papa.unparse(exportData);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'matched_patient_data.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Mock Data Generator
function useMockData() {
    const mockPatients = [
        { "ID": "P001", "Name": "John Doe", "Age": "45", "Gender": "M" },
        { "ID": "P002", "Name": "Jane Smith", "Age": "32", "Gender": "F" },
        { "ID": "P003", "Name": "Bob Johnson", "Age": "58", "Gender": "M" },
        { "ID": "P004", "Name": "Alice Brown", "Age": "27", "Gender": "F" },
        { "ID": "P005", "Name": "Charlie Davis", "Age": "64", "Gender": "M" }
    ];

    const mockClinical = [
        { "Diagnosis": "Hypertension", "Treatment": "Lisinopril", "Status": "Stable" },
        { "Diagnosis": "Type 2 Diabetes", "Treatment": "Metformin", "Status": "Monitoring" },
        { "Diagnosis": "Asthma", "Treatment": "Albuterol", "Status": "Controlled" },
        { "Diagnosis": "Migraine", "Treatment": "Sumatriptan", "Status": "Recurring" },
        { "Diagnosis": "Hyperlipidemia", "Treatment": "Atorvastatin", "Status": "Improved" }
    ];

    demographicsData = mockPatients;
    clinicalData = mockClinical;

    statusDemographics.textContent = "Loaded 5 Mock Records";
    statusClinical.textContent = "Loaded 5 Mock Records";

    checkReadyState();

    // Provide visual feedback
    btnMock.textContent = "Mock Data Loaded";
    setTimeout(() => btnMock.textContent = "Use Mock Data", 2000);
}
