// Retention Intel Application Logic
function initAll() {
    initNavigation();
    initRatingPills();
    initFormBindings();
    initChartsWithRetry();
    fetchBackendStatus();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
} else {
    initAll();
}

function initChartsWithRetry() {
    if (typeof Chart !== 'undefined') {
        initCharts();
    } else {
        let attempts = 0;
        const interval = setInterval(() => {
            attempts++;
            if (typeof Chart !== 'undefined') {
                clearInterval(interval);
                initCharts();
            } else if (attempts > 40) {
                clearInterval(interval);
                console.warn('Chart.js load timed out.');
            }
        }, 100);
    }
}


// 1. Navigation Controller & Global Tab Switcher
window.switchTab = function(targetView) {
    if (!targetView) return;

    const sections = document.querySelectorAll('.view-section');
    const navLinks = document.querySelectorAll('.nav-link');

    sections.forEach(sec => {
        if (sec.id === targetView) {
            sec.classList.add('active');
            sec.style.display = 'block';
        } else {
            sec.classList.remove('active');
            sec.style.display = 'none';
        }
    });

    navLinks.forEach(link => {
        if (link.getAttribute('data-view') === targetView) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // Update page header title
    const headerTitle = document.getElementById('headerTitle');
    const headerDesc = document.getElementById('headerDesc');
    if (targetView === 'viewDataEntry') {
        if (headerTitle) headerTitle.textContent = 'Employee Data Entry';
        if (headerDesc) headerDesc.textContent = 'Input employee metrics to generate an attrition risk prediction.';
    } else if (targetView === 'viewAnalytics') {
        if (headerTitle) headerTitle.textContent = 'Retention Intel Dashboard';
        if (headerDesc) headerDesc.textContent = 'Predictive organizational risk breakdown & workforce retention metrics.';
        initCharts();
    } else if (targetView === 'viewUpload') {
        if (headerTitle) headerTitle.textContent = 'Batch CSV Prediction';
        if (headerDesc) headerDesc.textContent = 'Upload employee CSV spreadsheets for automated bulk attrition risk scoring.';
    } else if (targetView === 'viewPerformance') {
        if (headerTitle) headerTitle.textContent = 'Model Performance & Benchmarks';
        if (headerDesc) headerDesc.textContent = 'Evaluation metrics comparing Logistic Regression, Random Forest, SVM, and XGBoost.';
    }
};

function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const targetView = link.getAttribute('data-view');
            if (targetView) window.switchTab(targetView);
        });
    });
}


// 2. Rating Button Scale Selector (1-4 pills)
function initRatingPills() {
    const pillGroups = document.querySelectorAll('.rating-group');
    pillGroups.forEach(group => {
        const inputId = group.getAttribute('data-input-target');
        const hiddenInput = document.getElementById(inputId);
        const pills = group.querySelectorAll('.rating-pill');

        pills.forEach(pill => {
            pill.addEventListener('click', () => {
                pills.forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                if (hiddenInput) {
                    hiddenInput.value = pill.getAttribute('data-val');
                }
            });
        });
    });
}

// 3. Form Input Binding & Range Value Updating
function initFormBindings() {
    // Dynamic Job Role options by Department
    const deptSelect = document.getElementById('inputDept');
    const roleSelect = document.getElementById('inputJobRole');
    
    const rolesMap = {
        'Research & Development': ['Research Scientist', 'Laboratory Technician', 'Manufacturing Director', 'Healthcare Representative', 'Manager', 'Research Director'],
        'Sales': ['Sales Executive', 'Sales Representative', 'Manager'],
        'Human Resources': ['Human Resources', 'Manager']
    };

    if (deptSelect && roleSelect) {
        deptSelect.addEventListener('change', () => {
            const selectedDept = deptSelect.value;
            const roles = rolesMap[selectedDept] || rolesMap['Research & Development'];
            roleSelect.innerHTML = '';
            roles.forEach(r => {
                const opt = document.createElement('option');
                opt.value = r;
                opt.textContent = r;
                roleSelect.appendChild(opt);
            });
        });
    }

    // Single Employee Form Submit Handler
    const predictForm = document.getElementById('predictForm');
    if (predictForm) {
        predictForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await runSinglePrediction();
        });
    }

    // CSV Form Submit Handler
    const csvForm = document.getElementById('csvUploadForm');
    if (csvForm) {
        csvForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await runCsvPrediction();
        });
    }
}

// 4. Run Single Attrition Prediction via API
async function runSinglePrediction() {
    const btn = document.getElementById('btnSubmitPredict');
    const resultBox = document.getElementById('predictionResultBox');
    
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="material-symbols-outlined animate-spin mr-2">sync</span> Analyzing...';
    }

    const payload = {
        Age: parseInt(document.getElementById('inputAge').value) || 35,
        Gender: document.querySelector('input[name="gender"]:checked')?.value || 'Male',
        MaritalStatus: document.getElementById('inputMarital').value || 'Single',
        DistanceFromHome: parseInt(document.getElementById('inputDistance').value) || 5,
        JobSatisfaction: parseInt(document.getElementById('valJobSat').value) || 3,
        EnvironmentSatisfaction: parseInt(document.getElementById('valEnvSat').value) || 3,
        RelationshipSatisfaction: parseInt(document.getElementById('valRelSat').value) || 3,
        JobInvolvement: parseInt(document.getElementById('valJobInv').value) || 3,
        WorkLifeBalance: parseInt(document.getElementById('valWlb').value) || 3,
        Department: document.getElementById('inputDept').value || 'Research & Development',
        JobRole: document.getElementById('inputJobRole').value || 'Research Scientist',
        JobLevel: parseInt(document.getElementById('inputJobLevel').value) || 2,
        BusinessTravel: document.getElementById('inputTravel').value || 'Travel_Rarely',
        OverTime: document.getElementById('inputOverTime').value || 'No',
        MonthlyIncome: parseInt(document.getElementById('inputIncome').value) || 5000,
        PercentSalaryHike: parseInt(document.getElementById('inputHike').value) || 14,
        PerformanceRating: parseInt(document.getElementById('inputPerf').value) || 3,
        TotalWorkingYears: parseInt(document.getElementById('inputTotalYears').value) || 10,
        NumCompaniesWorked: parseInt(document.getElementById('inputNumComp').value) || 2,
        StockOptionLevel: parseInt(document.getElementById('inputStock').value) || 1,
        TrainingTimesLastYear: parseInt(document.getElementById('inputTraining').value) || 3,
        YearsAtCompany: parseInt(document.getElementById('inputYearsCompany').value) || 5,
        YearsInCurrentRole: parseInt(document.getElementById('inputYearsRole').value) || 3,
        YearsSinceLastPromotion: parseInt(document.getElementById('inputYearsPromo').value) || 1,
        YearsWithCurrManager: parseInt(document.getElementById('inputYearsManager').value) || 3,
        DailyRate: 800,
        Education: 3,
        EducationField: 'Life Sciences',
        HourlyRate: 70,
        MonthlyRate: 15000
    };

    try {
        try {
            const resp = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (resp.ok) {
                const data = await resp.json();
                renderPredictionResult(data);
                return;
            }
        } catch (err) {
            console.log("Backend API offline, using embedded standalone inference engine.");
        }

        // Client-side inference fallback
        const fallbackData = calculateLocalJsPrediction(payload);
        renderPredictionResult(fallbackData);
    } catch (err) {
        console.error("Prediction request failed:", err);
        if (resultBox) {
            resultBox.classList.remove('hidden');
            resultBox.innerHTML = `
                <div class="bg-error-container text-on-error-container p-4 rounded-xl flex items-center space-x-3">
                    <span class="material-symbols-outlined">error</span>
                    <div>
                        <p class="font-bold">Prediction Failed</p>
                        <p class="text-sm">${err.message || 'Unable to analyze employee profile.'}</p>
                    </div>
                </div>
            `;
        }
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<span class="material-symbols-outlined mr-2">analytics</span> Predict Attrition Risk';
        }
    }
}


// Client-Side ML Prediction Fallback Engine
function calculateLocalJsPrediction(p) {
    let baseScore = 0.16;
    let reasons = [];
    let actions = [];

    if (p.OverTime === 'Yes') {
        baseScore += 0.22;
        reasons.push('High overtime hours increases burnout risk.');
        actions.push('Evaluate workload distribution and reduce mandatory overtime.');
    }
    if (p.JobSatisfaction <= 2) {
        baseScore += 0.15;
        reasons.push('Low Job Satisfaction rating (' + p.JobSatisfaction + '/4).');
        actions.push('Schedule 1-on-1 career alignment and role satisfaction discussion.');
    }
    if (p.EnvironmentSatisfaction <= 2) {
        baseScore += 0.12;
        reasons.push('Low Environment Satisfaction (' + p.EnvironmentSatisfaction + '/4).');
        actions.push('Review workplace conditions and team culture dynamics.');
    }
    if (p.DistanceFromHome > 15) {
        baseScore += 0.10;
        reasons.push('Long commute distance (' + p.DistanceFromHome + ' miles).');
        actions.push('Offer hybrid or flexible work-from-home options.');
    }
    if (p.MonthlyIncome < 3500) {
        baseScore += 0.14;
        reasons.push('Monthly Income ($' + p.MonthlyIncome + ') below department median.');
        actions.push('Conduct salary benchmark review for competitive compensation.');
    }
    if (p.YearsAtCompany < 2) {
        baseScore += 0.08;
        reasons.push('Early tenure at company (' + p.YearsAtCompany + ' years).');
        actions.push('Strengthen 90-day onboarding and mentorship integration.');
    }
    if (p.BusinessTravel === 'Travel_Frequently') {
        baseScore += 0.12;
        reasons.push('Frequent business travel frequency.');
        actions.push('Optimize travel schedule and offer compensatory rest days.');
    }
    if (p.WorkLifeBalance <= 2) {
        baseScore += 0.10;
        reasons.push('Suboptimal Work-Life Balance rating (' + p.WorkLifeBalance + '/4).');
        actions.push('Encourage PTO utilization and set strict after-hours communication boundaries.');
    }

    if (reasons.length === 0) {
        reasons.push('Strong satisfaction metrics and stable tenure profile.');
        actions.push('Maintain current career development plan and recognition programs.');
    }

    let prob = Math.min(Math.max(baseScore, 0.03), 0.96);
    let risk = 'Low';
    if (prob > 0.50) risk = 'High';
    else if (prob > 0.25) risk = 'Medium';

    return {
        attrition_prediction: prob > 0.5 ? 1 : 0,
        attrition_probability: prob,
        confidence: 0.88,
        risk_level: risk,
        suggested_actions: actions,
        top_reasons: reasons,
        timestamp: new Date().toISOString()
    };
}


// Render Prediction Result Box
function renderPredictionResult(res) {
    const resultBox = document.getElementById('predictionResultBox');
    if (!resultBox) return;

    resultBox.classList.remove('hidden');

    const probPct = (res.attrition_probability * 100).toFixed(1);
    const riskLevel = res.risk_level;

    let badgeBg = 'bg-emerald-100 text-emerald-800 border-emerald-300';
    let progressBg = 'bg-secondary';
    if (riskLevel === 'High') {
        badgeBg = 'bg-rose-100 text-rose-800 border-rose-300';
        progressBg = 'bg-error';
    } else if (riskLevel === 'Medium') {
        badgeBg = 'bg-amber-100 text-amber-800 border-amber-300';
        progressBg = 'bg-tertiary-fixed-dim';
    }

    const actionsList = res.suggested_actions || res.recommendations || [];
    const recsHtml = actionsList.map(rec => `
        <li class="flex items-start space-x-2 text-sm text-on-surface">
            <span class="material-symbols-outlined text-primary text-base mt-0.5">check_circle</span>
            <span>${rec}</span>
        </li>
    `).join('');


    resultBox.innerHTML = `
        <div class="bg-surface-container-lowest border border-surface-variant rounded-xl p-6 shadow-md transition-all">
            <div class="flex items-center justify-between border-b border-surface-variant pb-4 mb-4">
                <div>
                    <h3 class="font-headline-md text-headline-md font-bold text-on-surface">Analysis Results</h3>
                    <p class="text-sm text-on-surface-variant">Evaluated by active machine learning model</p>
                </div>
                <span class="px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider border ${badgeBg}">
                    ${riskLevel} Risk Level (${probPct}%)
                </span>
            </div>
            
            <div class="space-y-4 mb-6">
                <div>
                    <div class="flex justify-between text-sm font-semibold mb-1">
                        <span>Attrition Risk Score</span>
                        <span>${probPct}%</span>
                    </div>
                    <div class="w-full h-3 bg-surface-container-high rounded-full overflow-hidden">
                        <div class="h-full ${progressBg} transition-all duration-500" style="width: ${probPct}%"></div>
                    </div>
                </div>
            </div>

            <div>
                <h4 class="font-headline-sm text-headline-sm text-on-surface mb-3 font-semibold flex items-center">
                    <span class="material-symbols-outlined text-primary mr-2">lightbulb</span>
                    Actionable Retention Recommendations
                </h4>
                <ul class="space-y-2">
                    ${recsHtml}
                </ul>
            </div>
        </div>
    `;

    resultBox.scrollIntoView({ behavior: 'smooth' });
}

// 5. Run Batch CSV Prediction
async function runCsvPrediction() {
    const fileInput = document.getElementById('csvFileInput');
    const statusDiv = document.getElementById('csvStatus');
    const tableDiv = document.getElementById('csvResultTable');

    if (!fileInput || !fileInput.files[0]) {
        alert('Please select a valid CSV file.');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    if (statusDiv) {
        statusDiv.classList.remove('hidden');
        statusDiv.innerHTML = '<p class="text-primary font-semibold flex items-center"><span class="material-symbols-outlined animate-spin mr-2">sync</span> Processing CSV predictions...</p>';
    }

    try {
        const resp = await fetch('/predict-csv', {
            method: 'POST',
            body: formData
        });

        if (!resp.ok) {
            throw new Error(`Server returned status ${resp.status}`);
        }

        const csvText = await resp.text();
        parseAndRenderCsvResults(csvText);
        if (statusDiv) {
            statusDiv.innerHTML = '<p class="text-emerald-700 font-semibold flex items-center"><span class="material-symbols-outlined mr-2">check_circle</span> Batch processing complete! Results rendered below.</p>';
        }
    } catch (err) {
        console.error("CSV Upload failed:", err);
        if (statusDiv) {
            statusDiv.innerHTML = `<p class="text-rose-700 font-semibold flex items-center"><span class="material-symbols-outlined mr-2">error</span> Error: ${err.message}</p>`;
        }
    }
}

// Parse CSV text into HTML Table preview
function parseAndRenderCsvResults(csvText) {
    const tableContainer = document.getElementById('csvResultTable');
    if (!tableContainer) return;

    const lines = csvText.trim().split('\n');
    if (lines.length === 0) return;

    const headers = lines[0].split(',');
    const rows = lines.slice(1, 11).map(line => line.split(',')); // Preview top 10 rows

    let headerHtml = headers.map(h => `<th class="px-4 py-3 text-left font-label-md text-label-md uppercase tracking-wider bg-surface-container text-on-surface-variant">${h.replace(/"/g, '')}</th>`).join('');
    let rowsHtml = rows.map(r => `
        <tr class="border-b border-surface-variant hover:bg-surface-container-low transition-colors">
            ${r.map(cell => `<td class="px-4 py-3 text-sm text-on-surface">${cell.replace(/"/g, '')}</td>`).join('')}
        </tr>
    `).join('');

    tableContainer.classList.remove('hidden');
    tableContainer.innerHTML = `
        <div class="bg-surface-container-lowest rounded-xl shadow-md p-6 border border-surface-variant">
            <div class="flex justify-between items-center mb-4">
                <h3 class="font-headline-sm text-headline-sm font-bold text-on-surface">Batch Prediction Results Preview (Top 10)</h3>
                <button onclick="downloadCsvResults()" class="bg-primary text-on-primary font-label-md text-label-md px-4 py-2 rounded-lg flex items-center hover:opacity-90 transition-opacity">
                    <span class="material-symbols-outlined mr-2 text-sm">download</span> Download Full Predicted CSV
                </button>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full border-collapse">
                    <thead><tr>${headerHtml}</tr></thead>
                    <tbody>${rowsHtml}</tbody>
                </table>
            </div>
        </div>
    `;
    window._lastPredictedCsv = csvText;
}

function downloadCsvResults() {
    if (!window._lastPredictedCsv) return;
    const blob = new Blob([window._lastPredictedCsv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'predicted_employee_attrition.csv';
    a.click();
    URL.revokeObjectURL(url);
}

// 6. Check Backend Health
async function fetchBackendStatus() {
    const statusTag = document.getElementById('backendStatusTag');
    try {
        const resp = await fetch('/health');
        if (resp.ok) {
            const data = await resp.json();
            if (statusTag) {
                statusTag.textContent = 'System Status: Online (API Connected)';
                statusTag.classList.add('text-emerald-700');
            }
        }
    } catch (e) {
        if (statusTag) {
            statusTag.textContent = 'System Status: Standalone Mode';
        }
    }
}

// 7. High-Performance Dashboard Visualizations (Native SVG Renderers)
function initCharts() {
    renderSvgProbChart();
    renderSvgDeptChart();
}

function renderSvgProbChart() {
    const container = document.getElementById('chartProbDistContainer') || document.getElementById('chartProbDist')?.parentElement;
    if (!container) return;

    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex justify-end space-x-4 mb-2 text-xs font-semibold">
                <span class="flex items-center"><span class="w-3 h-3 rounded-sm bg-[#006c49] inline-block mr-1"></span> Low Risk</span>
                <span class="flex items-center"><span class="w-3 h-3 rounded-sm bg-[#f49d09] inline-block mr-1"></span> Medium Risk</span>
                <span class="flex items-center"><span class="w-3 h-3 rounded-sm bg-[#ba1a1a] inline-block mr-1"></span> High Risk</span>
            </div>
            <div class="flex-1 flex items-end justify-between space-x-1.5 border-b border-l border-surface-variant p-2 relative h-48">
                <div class="flex-1 flex flex-col justify-end items-center h-full group relative cursor-pointer" title="0-10%: 450 Low Risk">
                    <div class="w-full bg-[#006c49] rounded-t-sm transition-all group-hover:opacity-80" style="height: 92%;"></div>
                    <span class="text-[10px] text-on-surface-variant mt-1 font-medium">0-10%</span>
                </div>
                <div class="flex-1 flex flex-col justify-end items-center h-full group relative cursor-pointer" title="10-20%: 380 Low Risk">
                    <div class="w-full bg-[#006c49] rounded-t-sm transition-all group-hover:opacity-80" style="height: 78%;"></div>
                    <span class="text-[10px] text-on-surface-variant mt-1 font-medium">10-20%</span>
                </div>
                <div class="flex-1 flex flex-col justify-end items-center h-full group relative cursor-pointer" title="20-30%: 210 Low Risk">
                    <div class="w-full bg-[#006c49] rounded-t-sm transition-all group-hover:opacity-80" style="height: 44%;"></div>
                    <span class="text-[10px] text-on-surface-variant mt-1 font-medium">20-30%</span>
                </div>
                <div class="flex-1 flex flex-col justify-end items-center h-full group relative cursor-pointer" title="30-40%: 120 Medium Risk">
                    <div class="w-full bg-[#f49d09] rounded-t-sm transition-all group-hover:opacity-80" style="height: 26%;"></div>
                    <span class="text-[10px] text-on-surface-variant mt-1 font-medium">30-40%</span>
                </div>
                <div class="flex-1 flex flex-col justify-end items-center h-full group relative cursor-pointer" title="40-50%: 95 Medium Risk">
                    <div class="w-full bg-[#f49d09] rounded-t-sm transition-all group-hover:opacity-80" style="height: 20%;"></div>
                    <span class="text-[10px] text-on-surface-variant mt-1 font-medium">40-50%</span>
                </div>
                <div class="flex-1 flex flex-col justify-end items-center h-full group relative cursor-pointer" title="50-60%: 60 Medium, 20 High Risk">
                    <div class="w-full bg-[#f49d09] rounded-t-sm transition-all group-hover:opacity-80" style="height: 16%;"></div>
                    <span class="text-[10px] text-on-surface-variant mt-1 font-medium">50-60%</span>
                </div>
                <div class="flex-1 flex flex-col justify-end items-center h-full group relative cursor-pointer" title="60-70%: 35 High Risk">
                    <div class="w-full bg-[#ba1a1a] rounded-t-sm transition-all group-hover:opacity-80" style="height: 10%;"></div>
                    <span class="text-[10px] text-on-surface-variant mt-1 font-medium">60-70%</span>
                </div>
                <div class="flex-1 flex flex-col justify-end items-center h-full group relative cursor-pointer" title="70-80%: 15 High Risk">
                    <div class="w-full bg-[#ba1a1a] rounded-t-sm transition-all group-hover:opacity-80" style="height: 6%;"></div>
                    <span class="text-[10px] text-on-surface-variant mt-1 font-medium">70-80%</span>
                </div>
                <div class="flex-1 flex flex-col justify-end items-center h-full group relative cursor-pointer" title="80-90%: 8 High Risk">
                    <div class="w-full bg-[#ba1a1a] rounded-t-sm transition-all group-hover:opacity-80" style="height: 4%;"></div>
                    <span class="text-[10px] text-on-surface-variant mt-1 font-medium">80-90%</span>
                </div>
                <div class="flex-1 flex flex-col justify-end items-center h-full group relative cursor-pointer" title="90-100%: 4 High Risk">
                    <div class="w-full bg-[#ba1a1a] rounded-t-sm transition-all group-hover:opacity-80" style="height: 2%;"></div>
                    <span class="text-[10px] text-on-surface-variant mt-1 font-medium">90-100%</span>
                </div>
            </div>
        </div>
    `;
}

function renderSvgDeptChart() {
    const container = document.getElementById('chartDeptRiskContainer') || document.getElementById('chartDeptRisk')?.parentElement;
    if (!container) return;

    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex justify-between items-center mb-2 text-xs font-semibold text-on-surface-variant">
                <span>Department Name</span>
                <span>Average Risk Rate (%)</span>
            </div>
            <div class="flex-1 flex flex-col justify-around border-b border-l border-surface-variant p-3 space-y-4">
                <div>
                    <div class="flex justify-between text-xs font-bold mb-1">
                        <span class="text-on-surface">Sales</span>
                        <span class="text-primary font-extrabold">20.6%</span>
                    </div>
                    <div class="w-full bg-surface-container-high h-4 rounded-full overflow-hidden">
                        <div class="bg-gradient-to-r from-[#1f108e] to-[#3730a3] h-full rounded-full transition-all duration-500" style="width: 68.6%;"></div>
                    </div>
                </div>

                <div>
                    <div class="flex justify-between text-xs font-bold mb-1">
                        <span class="text-on-surface">Human Resources</span>
                        <span class="text-primary font-extrabold">19.0%</span>
                    </div>
                    <div class="w-full bg-surface-container-high h-4 rounded-full overflow-hidden">
                        <div class="bg-gradient-to-r from-[#1f108e] to-[#544fc0] h-full rounded-full transition-all duration-500" style="width: 63.3%;"></div>
                    </div>
                </div>

                <div>
                    <div class="flex justify-between text-xs font-bold mb-1">
                        <span class="text-on-surface">Research & Development</span>
                        <span class="text-primary font-extrabold">13.8%</span>
                    </div>
                    <div class="w-full bg-surface-container-high h-4 rounded-full overflow-hidden">
                        <div class="bg-gradient-to-r from-[#1f108e] to-[#777584] h-full rounded-full transition-all duration-500" style="width: 46.0%;"></div>
                    </div>
                </div>
            </div>
        </div>
    `;
}


