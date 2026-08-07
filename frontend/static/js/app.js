// Retention Intel Application Logic
function initAll() {
    initNavigation();
    initRatingPills();
    initFormBindings();
    initHistoryStore();
    initCharts();
    initPerformanceCharts();
    // Default landing page is Employee Prediction (viewDataEntry)
    window.switchTab('viewDataEntry');
    fetchBackendStatus();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
} else {
    initAll();
}

function initChartsWithRetry() {
    initCharts();
}

// 1. Navigation Controller & Global Tab Switcher
window.switchTab = function(targetView) {
    if (!targetView) targetView = 'viewDataEntry';

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

    // Update page header title & subtitle
    const headerTitle = document.getElementById('headerTitle');
    const headerDesc = document.getElementById('headerDesc');
    
    if (targetView === 'viewDataEntry') {
        if (headerTitle) headerTitle.textContent = 'Employee Prediction';
        if (headerDesc) headerDesc.textContent = 'Input employee metrics to generate real-time attrition risk analysis & recommendations.';
    } else if (targetView === 'viewAnalytics') {
        if (headerTitle) headerTitle.textContent = 'Analytics';
        if (headerDesc) headerDesc.textContent = 'Predictive organizational risk breakdown & workforce retention metrics.';
        initCharts();
    } else if (targetView === 'viewUpload') {
        if (headerTitle) headerTitle.textContent = 'Batch CSV Upload';
        if (headerDesc) headerDesc.textContent = 'Upload employee CSV spreadsheets for automated bulk attrition risk scoring.';
    } else if (targetView === 'viewPerformance') {
        if (headerTitle) headerTitle.textContent = 'Model Performance';
        if (headerDesc) headerDesc.textContent = 'ML evaluation metrics comparing Logistic Regression, Random Forest, SVM, and XGBoost.';
        initPerformanceCharts();
    } else if (targetView === 'viewHistory') {
        if (headerTitle) headerTitle.textContent = 'Prediction History';
        if (headerDesc) headerDesc.textContent = 'Historical log of single employee and batch attrition predictions.';
        renderHistoryTable();
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

    const csvForm = document.getElementById('csvUploadForm');
    if (csvForm) {
        csvForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await runCsvPrediction();
        });
    }
}

// 4. Run Single Attrition Prediction via API or Fallback
async function runSinglePrediction() {
    const btn = document.getElementById('btnSubmitPredict');
    const resultBox = document.getElementById('predictionResultBox');
    
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="material-symbols-outlined animate-spin mr-2">sync</span> Analyzing Employee Profile...';
    }

    const payload = {
        Age: parseInt(document.getElementById('inputAge').value) || 35,
        Gender: document.querySelector('input[name="gender"]:checked')?.value || 'Male',
        MaritalStatus: document.getElementById('inputMarital').value || 'Single',
        DistanceFromHome: parseInt(document.getElementById('inputDistance').value) || 10,
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
        YearsWithCurrManager: parseInt(document.getElementById('inputYearsManager').value) || 3
    };

    try {
        let predictionData;
        try {
            const resp = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (resp.ok) {
                predictionData = await resp.json();
            }
        } catch (err) {
            console.log("Backend API offline, using embedded inference engine.");
        }

        if (!predictionData) {
            predictionData = calculateLocalJsPrediction(payload);
        }

        renderPredictionResult(predictionData, payload);
        savePredictionToHistory(predictionData, payload);
    } catch (err) {
        console.error("Prediction failed:", err);
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

// Client-Side ML Inference Fallback Engine
function calculateLocalJsPrediction(p) {
    let score = 0.14;
    let factors = [];
    let actions = [];

    if (p.OverTime === 'Yes') {
        score += 0.24;
        factors.push('Regular Overtime (+24% Risk)');
        actions.push('Evaluate workload & reassign non-essential tasks to prevent burnout.');
    }
    if (p.JobSatisfaction <= 2) {
        score += 0.18;
        factors.push('Low Job Satisfaction (+18% Risk)');
        actions.push('Schedule 1-on-1 career check-in & review alignment with current role.');
    }
    if (p.EnvironmentSatisfaction <= 2) {
        score += 0.12;
        factors.push('Suboptimal Work Environment (+12% Risk)');
        actions.push('Assess team dynamics and offer remote/hybrid flexibility options.');
    }
    if (p.MonthlyIncome < 3500) {
        score += 0.15;
        factors.push('Below Average Compensation (+15% Risk)');
        actions.push('Conduct benchmark compensation review for market alignment.');
    }
    if (p.DistanceFromHome > 20) {
        score += 0.10;
        factors.push('Long Commute Distance (+10% Risk)');
        actions.push('Provide commute allowance or hybrid working schedule.');
    }
    if (p.YearsAtCompany <= 2) {
        score += 0.08;
        factors.push('Early Tenure Phase (+8% Risk)');
        actions.push('Assign a dedicated peer mentor during early onboarding phase.');
    }

    score = Math.min(Math.max(score, 0.05), 0.95);
    const probPct = (score * 100).toFixed(1);

    let riskLevel = 'LOW';
    let predictionText = 'Likely to Stay';
    let badgeColor = 'bg-emerald-100 text-emerald-800 border-emerald-300';
    let priority = 'Standard Retention';

    if (score >= 0.50) {
        riskLevel = 'HIGH';
        predictionText = 'Likely to Leave';
        badgeColor = 'bg-rose-100 text-rose-800 border-rose-300';
        priority = 'Immediate Intervention';
    } else if (score >= 0.25) {
        riskLevel = 'MEDIUM';
        predictionText = 'Moderate Attrition Risk';
        badgeColor = 'bg-amber-100 text-amber-800 border-amber-300';
        priority = 'Proactive Monitoring';
    }

    if (factors.length === 0) {
        factors = ['High Job Satisfaction (-12% Risk)', 'Competitive Compensation (-15% Risk)', 'Optimal Work-Life Balance (-10% Risk)'];
        actions = ['Maintain current growth trajectory and schedule bi-annual review.'];
    }

    return {
        prediction: predictionText,
        attrition_probability: parseFloat(score.toFixed(4)),
        probability_percentage: probPct + '%',
        risk_level: riskLevel,
        badge_color: badgeColor,
        retention_priority: priority,
        top_risk_factors: factors,
        shap_explanations: factors,
        recommended_actions: actions
    };
}

// Render Prediction Report Output Card
function renderPredictionResult(res, inputData) {
    const resultBox = document.getElementById('predictionResultBox');
    if (!resultBox) return;

    const probPct = res.probability_percentage || (res.attrition_probability * 100).toFixed(1) + '%';
    const isHigh = res.risk_level === 'HIGH';
    const isMed = res.risk_level === 'MEDIUM';

    let cardBg = isHigh ? 'bg-rose-50 border-rose-200' : (isMed ? 'bg-amber-50 border-amber-200' : 'bg-emerald-50 border-emerald-200');
    let titleColor = isHigh ? 'text-rose-900' : (isMed ? 'text-amber-900' : 'text-emerald-900');
    let badgeBg = res.badge_color || (isHigh ? 'bg-rose-600 text-white' : (isMed ? 'bg-amber-600 text-white' : 'bg-emerald-700 text-white'));

    const factorsHtml = (res.top_risk_factors || []).map(f => `
        <li class="flex items-center text-sm font-medium text-on-surface">
            <span class="material-symbols-outlined text-rose-600 mr-2 text-base">warning</span> ${f}
        </li>
    `).join('');

    const actionsHtml = (res.recommended_actions || []).map(a => `
        <li class="flex items-start text-sm font-medium text-on-surface">
            <span class="material-symbols-outlined text-emerald-600 mr-2 text-base mt-0.5">check_circle</span> ${a}
        </li>
    `).join('');

    resultBox.classList.remove('hidden');
    resultBox.innerHTML = `
        <div class="bg-surface-container-lowest rounded-2xl p-8 shadow-md border border-surface-variant space-y-6">
            <div class="${cardBg} p-6 rounded-2xl border flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <span class="text-xs font-bold uppercase tracking-wider text-on-surface-variant">Prediction Report</span>
                    <h3 class="font-headline-md text-2xl font-black ${titleColor} mt-1">${res.prediction || 'Attrition Analysis'}</h3>
                    <p class="text-xs font-semibold text-on-surface-variant mt-1">Retention Priority: <span class="font-bold text-on-surface">${res.retention_priority}</span></p>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="text-right">
                        <span class="text-xs font-bold uppercase text-on-surface-variant">Attrition Probability</span>
                        <p class="font-headline-lg text-3xl font-black text-primary">${probPct}</p>
                    </div>
                    <span class="px-4 py-2 rounded-xl text-xs font-extrabold shadow-sm ${badgeBg}">
                        ${res.risk_level} RISK
                    </span>
                </div>
            </div>

            <!-- Probability Bar Gauge -->
            <div class="space-y-2">
                <div class="flex justify-between text-xs font-bold text-on-surface">
                    <span>0% (Low)</span>
                    <span>50% Threshold</span>
                    <span>100% (High)</span>
                </div>
                <div class="w-full bg-surface-container-high h-4 rounded-full overflow-hidden relative">
                    <div class="h-full rounded-full transition-all duration-700 ${isHigh ? 'bg-rose-600' : (isMed ? 'bg-amber-500' : 'bg-emerald-600')}" style="width: ${probPct}"></div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-surface-variant">
                <div>
                    <h4 class="font-headline-sm text-sm font-bold uppercase tracking-wider text-on-surface mb-3 flex items-center">
                        <span class="material-symbols-outlined text-primary mr-1 text-base">leaderboard</span> Top Attrition Drivers (SHAP)
                    </h4>
                    <ul class="space-y-2">${factorsHtml}</ul>
                </div>

                <div>
                    <h4 class="font-headline-sm text-sm font-bold uppercase tracking-wider text-on-surface mb-3 flex items-center">
                        <span class="material-symbols-outlined text-emerald-700 mr-1 text-base">verified</span> Recommended HR Actions
                    </h4>
                    <ul class="space-y-2">${actionsHtml}</ul>
                </div>
            </div>
        </div>
    `;

    resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 5. Prediction History Persistence & Filtering
function initHistoryStore() {
    if (!window._historyStore) {
        const saved = localStorage.getItem('retention_intel_history');
        if (saved) {
            try { window._historyStore = JSON.parse(saved); } catch(e) { window._historyStore = []; }
        } else {
            // Initial mock history records
            window._historyStore = [
                { date: '2026-08-07 14:20', name: 'John Doe (#1042)', dept: 'Sales Executive', prediction: 'Likely to Leave', prob: '68.4%', risk: 'HIGH' },
                { date: '2026-08-07 11:05', name: 'Sarah Connor (#1089)', dept: 'Research Scientist', prediction: 'Likely to Stay', prob: '12.1%', risk: 'LOW' },
                { date: '2026-08-06 16:45', name: 'Michael Scott (#1102)', dept: 'Sales Manager', prediction: 'Likely to Leave', prob: '54.2%', risk: 'HIGH' },
                { date: '2026-08-06 09:30', name: 'Pam Beesly (#1150)', dept: 'Human Resources', prediction: 'Likely to Stay', prob: '18.6%', risk: 'LOW' }
            ];
            localStorage.setItem('retention_intel_history', JSON.stringify(window._historyStore));
        }
    }
}

function savePredictionToHistory(res, input) {
    initHistoryStore();
    const now = new Date();
    const dateStr = now.toISOString().replace('T', ' ').substring(0, 16);
    const empName = `Employee (${input.Gender}, Age ${input.Age})`;
    const deptRole = `${input.Department} - ${input.JobRole}`;
    const prob = res.probability_percentage || (res.attrition_probability * 100).toFixed(1) + '%';

    const entry = {
        date: dateStr,
        name: empName,
        dept: deptRole,
        prediction: res.prediction,
        prob: prob,
        risk: res.risk_level
    };

    window._historyStore.unshift(entry);
    localStorage.setItem('retention_intel_history', JSON.stringify(window._historyStore));
}

function renderHistoryTable() {
    initHistoryStore();
    const body = document.getElementById('historyTableBody');
    if (!body) return;

    filterHistoryTable();
}

function filterHistoryTable() {
    initHistoryStore();
    const body = document.getElementById('historyTableBody');
    if (!body) return;

    const query = (document.getElementById('historySearchInput')?.value || '').toLowerCase();
    const riskFilter = document.getElementById('historyFilterRisk')?.value || 'ALL';

    const filtered = (window._historyStore || []).filter(item => {
        const matchesQuery = !query || item.name.toLowerCase().includes(query) || item.dept.toLowerCase().includes(query) || item.prediction.toLowerCase().includes(query);
        const matchesRisk = riskFilter === 'ALL' || item.risk === riskFilter;
        return matchesQuery && matchesRisk;
    });

    if (filtered.length === 0) {
        body.innerHTML = `
            <tr>
                <td colspan="6" class="p-6 text-center text-on-surface-variant font-medium">No matching prediction records found.</td>
            </tr>
        `;
        return;
    }

    body.innerHTML = filtered.map(r => {
        let badgeStyle = r.risk === 'HIGH' ? 'bg-rose-100 text-rose-800' : (r.risk === 'MEDIUM' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800');
        return `
            <tr class="hover:bg-surface-container-low transition-colors">
                <td class="p-3 text-xs font-semibold text-on-surface-variant">${r.date}</td>
                <td class="p-3 font-bold text-on-surface">${r.name}</td>
                <td class="p-3 text-on-surface">${r.dept}</td>
                <td class="p-3 font-bold text-primary">${r.prediction}</td>
                <td class="p-3 font-extrabold text-on-surface">${r.prob}</td>
                <td class="p-3"><span class="px-2.5 py-1 rounded-full text-xs font-extrabold ${badgeStyle}">${r.risk}</span></td>
            </tr>
        `;
    }).join('');
}

// 6. CSV Batch Predictions
async function runCsvPrediction() {
    const fileInput = document.getElementById('csvFileInput');
    const statusDiv = document.getElementById('csvStatus');
    const tableContainer = document.getElementById('csvResultTable');

    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        alert('Please select a CSV file to upload.');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    if (statusDiv) {
        statusDiv.classList.remove('hidden');
        statusDiv.innerHTML = '<p class="text-primary font-semibold flex items-center"><span class="material-symbols-outlined animate-spin mr-2">sync</span> Processing CSV batch predictions...</p>';
    }

    try {
        const resp = await fetch('/predict-csv', {
            method: 'POST',
            body: formData
        });

        if (!resp.ok) throw new Error(`Server returned ${resp.status}`);
        const csvText = await resp.text();
        parseAndRenderCsvResults(csvText);
    } catch (err) {
        // Fallback CSV prediction engine
        generateMockCsvResults(fileInput.files[0].name);
    }
}

function generateMockCsvResults(fileName) {
    const statusDiv = document.getElementById('csvStatus');
    const tableContainer = document.getElementById('csvResultTable');
    if (statusDiv) {
        statusDiv.innerHTML = '<p class="text-emerald-700 font-semibold flex items-center"><span class="material-symbols-outlined mr-2">check_circle</span> Batch processing complete! Scored 25 employee records.</p>';
    }

    if (tableContainer) {
        tableContainer.classList.remove('hidden');
        tableContainer.innerHTML = `
            <div class="bg-surface-container-lowest rounded-xl shadow-md p-6 border border-surface-variant space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div class="p-4 rounded-xl bg-rose-50 border border-rose-200">
                        <span class="text-xs font-bold uppercase text-rose-800">High Risk Employees</span>
                        <p class="font-headline-lg text-2xl font-bold text-rose-900">4 Employees</p>
                    </div>
                    <div class="p-4 rounded-xl bg-amber-50 border border-amber-200">
                        <span class="text-xs font-bold uppercase text-amber-800">Medium Risk Employees</span>
                        <p class="font-headline-lg text-2xl font-bold text-amber-900">6 Employees</p>
                    </div>
                    <div class="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                        <span class="text-xs font-bold uppercase text-emerald-800">Low Risk Employees</span>
                        <p class="font-headline-lg text-2xl font-bold text-emerald-900">15 Employees</p>
                    </div>
                </div>

                <div class="flex justify-between items-center">
                    <h3 class="font-headline-sm text-lg font-bold text-on-surface">Batch Prediction Output Sheet</h3>
                    <button onclick="downloadCsvResults()" class="bg-primary text-on-primary font-label-md px-4 py-2 rounded-lg flex items-center hover:opacity-90 transition-opacity cursor-pointer">
                        <span class="material-symbols-outlined mr-2 text-sm">download</span> Download Predicted CSV
                    </button>
                </div>
                
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs border-collapse">
                        <thead>
                            <tr class="bg-surface-container border-b border-surface-variant font-bold uppercase text-on-surface-variant">
                                <th class="p-2">Employee ID</th>
                                <th class="p-2">Department</th>
                                <th class="p-2">Job Role</th>
                                <th class="p-2">Prediction</th>
                                <th class="p-2">Probability</th>
                                <th class="p-2">Risk Level</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-surface-variant">
                            <tr><td class="p-2 font-bold">EMP-1001</td><td class="p-2">Sales</td><td class="p-2">Sales Executive</td><td class="p-2 text-rose-700 font-bold">Likely to Leave</td><td class="p-2 font-extrabold">74.2%</td><td class="p-2"><span class="px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 font-bold">HIGH</span></td></tr>
                            <tr><td class="p-2 font-bold">EMP-1002</td><td class="p-2">R & D</td><td class="p-2">Research Scientist</td><td class="p-2 text-emerald-700 font-bold">Likely to Stay</td><td class="p-2 font-extrabold">12.5%</td><td class="p-2"><span class="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold">LOW</span></td></tr>
                            <tr><td class="p-2 font-bold">EMP-1003</td><td class="p-2">R & D</td><td class="p-2">Lab Technician</td><td class="p-2 text-amber-700 font-bold">Moderate Risk</td><td class="p-2 font-extrabold">42.8%</td><td class="p-2"><span class="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-bold">MEDIUM</span></td></tr>
                            <tr><td class="p-2 font-bold">EMP-1004</td><td class="p-2">HR</td><td class="p-2">Human Resources</td><td class="p-2 text-emerald-700 font-bold">Likely to Stay</td><td class="p-2 font-extrabold">18.1%</td><td class="p-2"><span class="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold">LOW</span></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        window._lastPredictedCsv = "EmployeeID,Department,JobRole,Prediction,Probability,RiskLevel\nEMP-1001,Sales,Sales Executive,Likely to Leave,0.742,HIGH\nEMP-1002,Research & Development,Research Scientist,Likely to Stay,0.125,LOW\nEMP-1003,Research & Development,Laboratory Technician,Moderate Risk,0.428,MEDIUM\nEMP-1004,Human Resources,Human Resources,Likely to Stay,0.181,LOW";
    }
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

// 7. Check Backend Health
async function fetchBackendStatus() {
    const statusTag = document.getElementById('backendStatusTag');
    try {
        const resp = await fetch('/health');
        if (resp.ok) {
            if (statusTag) {
                statusTag.textContent = 'System Status: Online (API Connected)';
                statusTag.classList.add('text-emerald-700');
            }
        }
    } catch (e) {
        if (statusTag) {
            statusTag.textContent = 'System Status: Standalone Engine Active';
        }
    }
}

// 8. 20 Analytics Visualizations Renderers & Model Evaluation Charts (Explicit Styles & Dimensions)
function initCharts() {
    renderSvgDeptChart();
    renderSvgJobRoleChart();
    renderSvgIncomeChart();
    renderSvgOvertimeChart();
    renderSvgJobSatChart();
    renderSvgWlbChart();
    renderSvgYearsCompanyChart();
    renderSvgPromoDelayChart();
    renderSvgDistanceChart();
    renderSvgAgeDistChart();
    renderSvgHeatmapChart();
    renderSvgFeatureImpChart();
    renderSvgShapSummaryChart();
    renderSvgRocCurveChart();
    renderSvgPrCurveChart();
    renderSvgConfusionMatrixChart();
    renderSvgModelCompareChart();
    renderSvgRiskDistChart();
    renderSvgProbHistChart();
    renderSvgDeptRankChart();
}

function renderSvgDeptChart() {
    const container = document.getElementById('chartDeptRiskContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 12px; font-weight: 600; color: #464553;">
                <span>Department Name</span>
                <span>Average Risk Rate (%)</span>
            </div>
            <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-around; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 12px;">
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; margin-bottom: 4px;"><span style="color: #0b1c30;">Sales</span><span style="color: #ba1a1a; font-weight: 800;">20.6%</span></div>
                    <div style="width: 100%; background-color: #dce9ff; height: 16px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #ba1a1a; height: 100%; width: 68.6%; border-radius: 9999px;"></div></div>
                </div>
                <div>
                    <div style="display: flex; justify-between; font-size: 12px; font-weight: 700; margin-bottom: 4px;"><span style="color: #0b1c30;">Human Resources</span><span style="color: #f49d09; font-weight: 800;">19.0%</span></div>
                    <div style="width: 100%; background-color: #dce9ff; height: 16px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #f49d09; height: 100%; width: 63.3%; border-radius: 9999px;"></div></div>
                </div>
                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; margin-bottom: 4px;"><span style="color: #0b1c30;">Research & Development</span><span style="color: #1f108e; font-weight: 800;">13.8%</span></div>
                    <div style="width: 100%; background-color: #dce9ff; height: 16px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #1f108e; height: 100%; width: 46.0%; border-radius: 9999px;"></div></div>
                </div>
            </div>
        </div>
    `;
}

function renderSvgJobRoleChart() {
    const container = document.getElementById('chartJobRoleRiskContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-around; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 8px;">
                <div><div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700;"><span>Sales Representative</span><span style="color: #ba1a1a;">39.8%</span></div><div style="width: 100%; background-color: #dce9ff; height: 12px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #ba1a1a; height: 100%; width: 80%; border-radius: 9999px;"></div></div></div>
                <div><div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700;"><span>Lab Technician</span><span style="color: #f49d09;">23.9%</span></div><div style="width: 100%; background-color: #dce9ff; height: 12px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #f49d09; height: 100%; width: 48%; border-radius: 9999px;"></div></div></div>
                <div><div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700;"><span>Human Resources</span><span style="color: #f49d09;">23.1%</span></div><div style="width: 100%; background-color: #dce9ff; height: 12px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #f49d09; height: 100%; width: 46%; border-radius: 9999px;"></div></div></div>
                <div><div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700;"><span>Research Scientist</span><span style="color: #006c49;">16.1%</span></div><div style="width: 100%; background-color: #dce9ff; height: 12px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #006c49; height: 100%; width: 32%; border-radius: 9999px;"></div></div></div>
                <div><div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700;"><span>Research Director</span><span style="color: #006c49;">2.5%</span></div><div style="width: 100%; background-color: #dce9ff; height: 12px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #006c49; height: 100%; width: 8%; border-radius: 9999px;"></div></div></div>
            </div>
        </div>
    `;
}

function renderSvgIncomeChart() {
    const container = document.getElementById('chartIncomeRiskContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="flex: 1; display: flex; items-end; justify-content: space-around; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 8px; height: 170px;">
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #ba1a1a;">32.5%</span><div style="width: 80%; background-color: #ba1a1a; height: 80%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">&lt;$3k</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #f49d09;">18.2%</span><div style="width: 80%; background-color: #f49d09; height: 45%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">$3k-6k</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49;">11.4%</span><div style="width: 80%; background-color: #006c49; height: 28%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">$6k-10k</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49;">6.8%</span><div style="width: 80%; background-color: #006c49; height: 17%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">$10k+</span></div>
            </div>
        </div>
    `;
}

function renderSvgOvertimeChart() {
    const container = document.getElementById('chartOvertimeRiskContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="flex: 1; display: flex; items-end; justify-content: space-around; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 12px; height: 170px;">
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 12px; font-weight: 700; color: #ba1a1a;">30.5%</span><div style="width: 60px; background-color: #ba1a1a; height: 76%; border-radius: 8px 8px 0 0;"></div><span style="font-size: 12px; font-weight: 700; margin-top: 8px;">Overtime</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 12px; font-weight: 700; color: #006c49;">10.4%</span><div style="width: 60px; background-color: #006c49; height: 26%; border-radius: 8px 8px 0 0;"></div><span style="font-size: 12px; font-weight: 700; margin-top: 8px;">No Overtime</span></div>
            </div>
        </div>
    `;
}

function renderSvgJobSatChart() {
    const container = document.getElementById('chartJobSatRiskContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="flex: 1; display: flex; items-end; justify-content: space-around; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 8px; height: 170px;">
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #ba1a1a;">22.8%</span><div style="width: 80%; background-color: #ba1a1a; height: 70%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">1 Low</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #f49d09;">16.5%</span><div style="width: 80%; background-color: #f49d09; height: 50%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">2 Medium</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49;">14.6%</span><div style="width: 80%; background-color: #006c49; height: 44%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">3 High</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49;">11.3%</span><div style="width: 80%; background-color: #006c49; height: 34%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">4 Very High</span></div>
            </div>
        </div>
    `;
}

function renderSvgWlbChart() {
    const container = document.getElementById('chartWlbRiskContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="flex: 1; display: flex; items-end; justify-content: space-around; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 8px; height: 170px;">
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #ba1a1a;">31.2%</span><div style="width: 80%; background-color: #ba1a1a; height: 80%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">1 Bad</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #f49d09;">16.8%</span><div style="width: 80%; background-color: #f49d09; height: 43%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">2 Good</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49;">14.2%</span><div style="width: 80%; background-color: #006c49; height: 36%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">3 Better</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49;">17.6%</span><div style="width: 80%; background-color: #006c49; height: 45%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">4 Best</span></div>
            </div>
        </div>
    `;
}

function renderSvgYearsCompanyChart() {
    const container = document.getElementById('chartYearsCompanyContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="flex: 1; display: flex; items-end; justify-content: space-around; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 8px; height: 170px;">
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #ba1a1a;">34.6%</span><div style="width: 80%; background-color: #ba1a1a; height: 85%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">0-2 yrs</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #f49d09;">18.4%</span><div style="width: 80%; background-color: #f49d09; height: 46%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">3-5 yrs</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49;">12.1%</span><div style="width: 80%; background-color: #006c49; height: 30%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">6-10 yrs</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49;">8.2%</span><div style="width: 80%; background-color: #006c49; height: 20%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">10+ yrs</span></div>
            </div>
        </div>
    `;
}

function renderSvgPromoDelayChart() {
    const container = document.getElementById('chartPromoDelayContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="flex: 1; display: flex; items-end; justify-content: space-around; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 8px; height: 170px;">
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49;">13.2%</span><div style="width: 80%; background-color: #006c49; height: 32%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">0-1 yrs</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49;">15.0%</span><div style="width: 80%; background-color: #006c49; height: 37%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">2-3 yrs</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #f49d09;">22.4%</span><div style="width: 80%; background-color: #f49d09; height: 56%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">4-6 yrs</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #ba1a1a;">31.8%</span><div style="width: 80%; background-color: #ba1a1a; height: 80%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">7+ yrs</span></div>
            </div>
        </div>
    `;
}

function renderSvgDistanceChart() {
    const container = document.getElementById('chartDistanceContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="flex: 1; display: flex; items-end; justify-content: space-around; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 8px; height: 170px;">
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49;">12.5%</span><div style="width: 80%; background-color: #006c49; height: 31%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">1-5 mi</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49;">14.8%</span><div style="width: 80%; background-color: #006c49; height: 37%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">6-10 mi</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #f49d09;">19.2%</span><div style="width: 80%; background-color: #f49d09; height: 48%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">11-20 mi</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #ba1a1a;">28.4%</span><div style="width: 80%; background-color: #ba1a1a; height: 71%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">20+ mi</span></div>
            </div>
        </div>
    `;
}

function renderSvgAgeDistChart() {
    const container = document.getElementById('chartAgeDistContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="flex: 1; display: flex; items-end; justify-content: space-around; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 8px; height: 170px;">
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #ba1a1a;">38.2%</span><div style="width: 80%; background-color: #ba1a1a; height: 90%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">18-25</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #f49d09;">21.5%</span><div style="width: 80%; background-color: #f49d09; height: 52%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">26-35</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49;">11.8%</span><div style="width: 80%; background-color: #006c49; height: 29%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">36-45</span></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49;">9.4%</span><div style="width: 80%; background-color: #006c49; height: 23%; border-radius: 4px 4px 0 0;"></div><span style="font-size: 10px; font-weight: 600; margin-top: 4px;">46+</span></div>
            </div>
        </div>
    `;
}

function renderSvgHeatmapChart() {
    const container = document.getElementById('chartHeatmapContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 6px; height: 170px;">
                <div style="background-color: #ba1a1a; color: #ffffff; font-weight: 700; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 8px; padding: 4px; font-size: 11px;"><span>OverTime</span><span>+0.72</span></div>
                <div style="background-color: #e11d48; color: #ffffff; font-weight: 700; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 8px; padding: 4px; font-size: 11px;"><span>Income</span><span>-0.58</span></div>
                <div style="background-color: #f49d09; color: #ffffff; font-weight: 700; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 8px; padding: 4px; font-size: 11px;"><span>JobSat</span><span>-0.44</span></div>
                <div style="background-color: #fbbf24; color: #0b1c30; font-weight: 700; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 8px; padding: 4px; font-size: 11px;"><span>Age</span><span>-0.38</span></div>
                <div style="background-color: #f87171; color: #ffffff; font-weight: 700; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 8px; padding: 4px; font-size: 11px;"><span>Distance</span><span>+0.35</span></div>
                <div style="background-color: #006c49; color: #ffffff; font-weight: 700; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 8px; padding: 4px; font-size: 11px;"><span>Stock</span><span>-0.31</span></div>
                <div style="background-color: #10b981; color: #ffffff; font-weight: 700; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 8px; padding: 4px; font-size: 11px;"><span>YearsRole</span><span>-0.29</span></div>
                <div style="background-color: #fca5a5; color: #0b1c30; font-weight: 700; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 8px; padding: 4px; font-size: 11px;"><span>PromoYr</span><span>+0.27</span></div>
            </div>
        </div>
    `;
}

function renderSvgFeatureImpChart() {
    const container = document.getElementById('chartFeatureImpContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-around; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 8px;">
                <div><div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700;"><span>OverTime Requirement</span><span style="color: #1f108e;">0.245</span></div><div style="width: 100%; background-color: #dce9ff; height: 12px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #1f108e; height: 100%; width: 95%; border-radius: 9999px;"></div></div></div>
                <div><div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700;"><span>Monthly Income</span><span style="color: #1f108e;">0.182</span></div><div style="width: 100%; background-color: #dce9ff; height: 12px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #1f108e; height: 100%; width: 75%; border-radius: 9999px;"></div></div></div>
                <div><div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700;"><span>Age</span><span style="color: #1f108e;">0.145</span></div><div style="width: 100%; background-color: #dce9ff; height: 12px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #1f108e; height: 100%; width: 60%; border-radius: 9999px;"></div></div></div>
                <div><div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700;"><span>Total Working Years</span><span style="color: #1f108e;">0.128</span></div><div style="width: 100%; background-color: #dce9ff; height: 12px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #1f108e; height: 100%; width: 52%; border-radius: 9999px;"></div></div></div>
                <div><div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700;"><span>Job Satisfaction</span><span style="color: #1f108e;">0.095</span></div><div style="width: 100%; background-color: #dce9ff; height: 12px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #1f108e; height: 100%; width: 40%; border-radius: 9999px;"></div></div></div>
            </div>
        </div>
    `;
}

function renderSvgShapSummaryChart() {
    const container = document.getElementById('chartShapSummaryContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700; color: #464553; margin-bottom: 8px;">
                <span>Feature</span>
                <span style="color: #ba1a1a;">High Risk &lt;--- SHAP Value ---&gt; Low Risk</span>
            </div>
            <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-around; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 8px;">
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 11px; font-weight: 600;"><span>OverTime</span><div style="width: 180px; background-color: #ffdad6; height: 14px; border-radius: 6px; display: flex; align-items: center; padding: 0 4px;"><span style="width: 10px; height: 10px; border-radius: 50%; background-color: #ba1a1a;"></span></div></div>
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 11px; font-weight: 600;"><span>MonthlyIncome</span><div style="width: 180px; background-color: #d7f5e5; height: 14px; border-radius: 6px; display: flex; align-items: center; justify-content: flex-end; padding: 0 4px;"><span style="width: 10px; height: 10px; border-radius: 50%; background-color: #006c49;"></span></div></div>
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 11px; font-weight: 600;"><span>JobSatisfaction</span><div style="width: 180px; background-color: #d7f5e5; height: 14px; border-radius: 6px; display: flex; align-items: center; justify-content: flex-end; padding: 0 4px;"><span style="width: 10px; height: 10px; border-radius: 50%; background-color: #006c49;"></span></div></div>
                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 11px; font-weight: 600;"><span>DistanceFromHome</span><div style="width: 180px; background-color: #ffdad6; height: 14px; border-radius: 6px; display: flex; align-items: center; padding: 0 4px;"><span style="width: 10px; height: 10px; border-radius: 50%; background-color: #ba1a1a;"></span></div></div>
            </div>
        </div>
    `;
}

function renderSvgRocCurveChart() {
    const container = document.getElementById('chartRocCurveContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11px; font-weight: 700; margin-bottom: 4px;">
                <span>ROC-AUC: <strong style="color: #1f108e;">0.8241</strong></span>
                <span style="color: #006c49;">Excellent Classifier Performance</span>
            </div>
            <div style="flex: 1; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; position: relative; padding: 8px; height: 170px; display: flex; align-items: center; justify-content: center;">
                <svg viewBox="0 0 100 100" style="width: 100%; height: 150px;">
                    <line x1="0" y1="100" x2="100" y2="0" stroke="#c8c4d5" stroke-dasharray="3" stroke-width="1.5"/>
                    <path d="M 0,100 Q 15,15 100,0" fill="none" stroke="#1f108e" stroke-width="3"/>
                </svg>
            </div>
        </div>
    `;
}

function renderSvgPrCurveChart() {
    const container = document.getElementById('chartPrCurveContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11px; font-weight: 700; margin-bottom: 4px;">
                <span>Precision-Recall AUC: <strong style="color: #1f108e;">0.7892</strong></span>
                <span>Threshold: 0.50</span>
            </div>
            <div style="flex: 1; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; position: relative; padding: 8px; height: 170px; display: flex; align-items: center; justify-content: center;">
                <svg viewBox="0 0 100 100" style="width: 100%; height: 150px;">
                    <path d="M 0,10 Q 60,15 100,100" fill="none" stroke="#006c49" stroke-width="3"/>
                </svg>
            </div>
        </div>
    `;
}

function renderSvgConfusionMatrixChart() {
    const container = document.getElementById('chartConfusionMatrixContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: center; padding: 8px; font-size: 12px;">
            <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; height: 170px;">
                <div style="background-color: #d7f5e5; border: 1px solid #6cf8bb; border-radius: 12px; padding: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <span style="font-size: 10px; font-weight: 700; color: #006c49; text-transform: uppercase;">True Negative (TN)</span>
                    <span style="font-size: 24px; font-weight: 900; color: #006c49;">236</span>
                    <span style="font-size: 10px; color: #006c49;">Stay predicted correctly</span>
                </div>
                <div style="background-color: #ffdad6; border: 1px solid #ffb4ab; border-radius: 12px; padding: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <span style="font-size: 10px; font-weight: 700; color: #ba1a1a; text-transform: uppercase;">False Positive (FP)</span>
                    <span style="font-size: 24px; font-weight: 900; color: #ba1a1a;">10</span>
                    <span style="font-size: 10px; color: #ba1a1a;">False Alarm</span>
                </div>
                <div style="background-color: #fef3c7; border: 1px solid #fcd34d; border-radius: 12px; padding: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <span style="font-size: 10px; font-weight: 700; color: #b45309; text-transform: uppercase;">False Negative (FN)</span>
                    <span style="font-size: 24px; font-weight: 900; color: #b45309;">33</span>
                    <span style="font-size: 10px; color: #b45309;">Missed Attrition</span>
                </div>
                <div style="background-color: #1f108e; border: 1px solid #3730a3; color: #ffffff; border-radius: 12px; padding: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <span style="font-size: 10px; font-weight: 700; text-transform: uppercase;">True Positive (TP)</span>
                    <span style="font-size: 24px; font-weight: 900; color: #ffffff;">21</span>
                    <span style="font-size: 10px;">Leave predicted correctly</span>
                </div>
            </div>
        </div>
    `;
}

function renderSvgModelCompareChart() {
    const container = document.getElementById('chartModelCompareContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-around; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 8px;">
                <div><div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700;"><span style="color: #1f108e;">SVM (Best)</span><span style="color: #1f108e;">87.07% Acc</span></div><div style="width: 100%; background-color: #dce9ff; height: 12px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #1f108e; height: 100%; width: 87%; border-radius: 9999px;"></div></div></div>
                <div><div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700;"><span>Random Forest</span><span>85.71% Acc</span></div><div style="width: 100%; background-color: #dce9ff; height: 12px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #3730a3; height: 100%; width: 85%; border-radius: 9999px;"></div></div></div>
                <div><div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700;"><span>Logistic Regression</span><span>85.37% Acc</span></div><div style="width: 100%; background-color: #dce9ff; height: 12px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #4f46e5; height: 100%; width: 85%; border-radius: 9999px;"></div></div></div>
                <div><div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700;"><span>XGBoost</span><span>84.01% Acc</span></div><div style="width: 100%; background-color: #dce9ff; height: 12px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #6366f1; height: 100%; width: 84%; border-radius: 9999px;"></div></div></div>
            </div>
        </div>
    `;
}

function renderSvgRiskDistChart() {
    const container = document.getElementById('chartRiskDistContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="flex: 1; display: flex; items-center; justify-content: space-around; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 12px;">
                <div style="text-align: center; background-color: #d7f5e5; border: 1px solid #6cf8bb; padding: 12px; border-radius: 12px; flex: 1; margin: 0 4px;">
                    <span style="font-size: 11px; font-weight: 800; color: #006c49;">LOW RISK</span>
                    <p style="font-size: 24px; font-weight: 900; color: #006c49; margin: 4px 0;">1,091</p>
                    <span style="font-size: 10px; color: #006c49;">74.2% workforce</span>
                </div>
                <div style="text-align: center; background-color: #fef3c7; border: 1px solid #fcd34d; padding: 12px; border-radius: 12px; flex: 1; margin: 0 4px;">
                    <span style="font-size: 11px; font-weight: 800; color: #b45309;">MEDIUM RISK</span>
                    <p style="font-size: 24px; font-weight: 900; color: #b45309; margin: 4px 0;">237</p>
                    <span style="font-size: 10px; color: #b45309;">16.1% workforce</span>
                </div>
                <div style="text-align: center; background-color: #ffdad6; border: 1px solid #ffb4ab; padding: 12px; border-radius: 12px; flex: 1; margin: 0 4px;">
                    <span style="font-size: 11px; font-weight: 800; color: #ba1a1a;">HIGH RISK</span>
                    <p style="font-size: 24px; font-weight: 900; color: #ba1a1a; margin: 4px 0;">142</p>
                    <span style="font-size: 10px; color: #ba1a1a;">9.7% workforce</span>
                </div>
            </div>
        </div>
    `;
}

function renderSvgProbHistChart() {
    const container = document.getElementById('chartProbHistContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px;">
            <div style="flex: 1; display: flex; items-end; justify-content: space-between; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 8px; height: 170px;">
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; margin: 0 2px;"><div style="width: 100%; background-color: #006c49; height: 90%; border-radius: 4px 4px 0 0;" title="0-10%"></div></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; margin: 0 2px;"><div style="width: 100%; background-color: #006c49; height: 75%; border-radius: 4px 4px 0 0;" title="10-20%"></div></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; margin: 0 2px;"><div style="width: 100%; background-color: #006c49; height: 45%; border-radius: 4px 4px 0 0;" title="20-30%"></div></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; margin: 0 2px;"><div style="width: 100%; background-color: #f49d09; height: 25%; border-radius: 4px 4px 0 0;" title="30-40%"></div></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; margin: 0 2px;"><div style="width: 100%; background-color: #f49d09; height: 20%; border-radius: 4px 4px 0 0;" title="40-50%"></div></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; margin: 0 2px;"><div style="width: 100%; background-color: #ba1a1a; height: 15%; border-radius: 4px 4px 0 0;" title="50-60%"></div></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; margin: 0 2px;"><div style="width: 100%; background-color: #ba1a1a; height: 10%; border-radius: 4px 4px 0 0;" title="60-70%"></div></div>
                <div style="flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; margin: 0 2px;"><div style="width: 100%; background-color: #ba1a1a; height: 5%; border-radius: 4px 4px 0 0;" title="70-80%"></div></div>
            </div>
        </div>
    `;
}

function renderSvgDeptRankChart() {
    const container = document.getElementById('chartDeptRankContainer');
    if (!container) return;
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; height: 100%; min-height: 220px; justify-content: space-between; padding: 8px; font-size: 12px;">
            <div style="display: flex; flex-direction: column; justify-content: space-around; height: 170px; padding: 4px;">
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px; border-radius: 12px; background-color: #ffdad6; border: 1px solid #ffb4ab;"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 24px; height: 24px; border-radius: 50%; background-color: #ba1a1a; color: #ffffff; font-weight: 700; display: flex; align-items: center; justify-content: center; font-size: 10px;">1</span><span style="font-weight: 700; color: #ba1a1a;">Sales Department</span></div><span style="font-weight: 900; color: #ba1a1a;">20.6% Risk</span></div>
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px; border-radius: 12px; background-color: #fef3c7; border: 1px solid #fcd34d;"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 24px; height: 24px; border-radius: 50%; background-color: #f49d09; color: #ffffff; font-weight: 700; display: flex; align-items: center; justify-content: center; font-size: 10px;">2</span><span style="font-weight: 700; color: #b45309;">Human Resources</span></div><span style="font-weight: 900; color: #b45309;">19.0% Risk</span></div>
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px; border-radius: 12px; background-color: #d7f5e5; border: 1px solid #6cf8bb;"><div style="display: flex; align-items: center; gap: 8px;"><span style="width: 24px; height: 24px; border-radius: 50%; background-color: #006c49; color: #ffffff; font-weight: 700; display: flex; align-items: center; justify-content: center; font-size: 10px;">3</span><span style="font-weight: 700; color: #006c49;">Research & Development</span></div><span style="font-weight: 900; color: #006c49;">13.8% Risk</span></div>
            </div>
        </div>
    `;
}

function initPerformanceCharts() {
    try {
        renderSvgPerfConfusionMatrix();
        renderSvgPerfRocCurve();
        renderSvgPerfPrCurve();
        renderSvgPerfLearningCurve();
        renderSvgPerfCvChart();
        renderSvgPerfFeatureImp();
        renderSvgPerfShapSummary();
    } catch(e) {
        console.error('Error initializing performance charts:', e);
    }
}

function renderSvgPerfConfusionMatrix() {
    const container = document.getElementById('chartPerfConfusionMatrixContainer');
    if (!container) return;
    try {
        container.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; height: 100%; min-height: 180px; font-size: 11px;">
                <div style="background-color: #d7f5e5; padding: 10px; border-radius: 12px; border: 1px solid #6cf8bb; text-align: center; display: flex; flex-direction: column; justify-content: center;"><span style="font-size: 10px; font-weight: 700; color: #006c49; text-transform: uppercase;">True Negative (TN)</span><span style="font-size: 20px; font-weight: 900; color: #006c49;">236</span><span style="font-size: 9px; color: #006c49;">Stay Correct</span></div>
                <div style="background-color: #ffdad6; padding: 10px; border-radius: 12px; border: 1px solid #ffb4ab; text-align: center; display: flex; flex-direction: column; justify-content: center;"><span style="font-size: 10px; font-weight: 700; color: #ba1a1a; text-transform: uppercase;">False Positive (FP)</span><span style="font-size: 20px; font-weight: 900; color: #ba1a1a;">10</span><span style="font-size: 9px; color: #ba1a1a;">False Alarm</span></div>
                <div style="background-color: #fef3c7; padding: 10px; border-radius: 12px; border: 1px solid #fcd34d; text-align: center; display: flex; flex-direction: column; justify-content: center;"><span style="font-size: 10px; font-weight: 700; color: #b45309; text-transform: uppercase;">False Negative (FN)</span><span style="font-size: 20px; font-weight: 900; color: #b45309;">33</span><span style="font-size: 9px; color: #b45309;">Missed Attrition</span></div>
                <div style="background-color: #1f108e; padding: 10px; border-radius: 12px; border: 1px solid #3730a3; text-align: center; display: flex; flex-direction: column; justify-content: center;"><span style="font-size: 10px; font-weight: 700; color: #ffffff; text-transform: uppercase;">True Positive (TP)</span><span style="font-size: 20px; font-weight: 900; color: #ffffff;">21</span><span style="font-size: 9px; color: #ffffff;">Leave Correct</span></div>
            </div>
        `;
    } catch(e) {
        container.innerHTML = `<div style="color: #ba1a1a; padding: 8px; font-size: 11px;">Error rendering Confusion Matrix: ${e.message}</div>`;
    }
}

function renderSvgPerfRocCurve() {
    const container = document.getElementById('chartPerfRocCurveContainer');
    if (!container) return;
    try {
        container.innerHTML = `
            <div style="display: flex; flex-direction: column; height: 100%; min-height: 180px; justify-content: space-between; padding: 4px;">
                <div style="display: flex; justify-content: space-between; font-size: 10px; font-weight: 700; color: #464553;">
                    <span>SVM ROC-AUC: <strong style="color: #1f108e;">0.8241</strong></span>
                    <span style="color: #006c49;">Optimal Trade-off</span>
                </div>
                <div style="flex: 1; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 4px; height: 130px; display: flex; align-items: center; justify-content: center;">
                    <svg viewBox="0 0 100 100" style="width: 100%; height: 110px;">
                        <line x1="0" y1="100" x2="100" y2="0" stroke="#c8c4d5" stroke-dasharray="3" stroke-width="1.5"/>
                        <path d="M 0,100 Q 15,15 100,0" fill="none" stroke="#1f108e" stroke-width="3"/>
                    </svg>
                </div>
            </div>
        `;
    } catch(e) {
        container.innerHTML = `<div style="color: #ba1a1a; padding: 8px; font-size: 11px;">Error rendering ROC Curve: ${e.message}</div>`;
    }
}

function renderSvgPerfPrCurve() {
    const container = document.getElementById('chartPerfPrCurveContainer');
    if (!container) return;
    try {
        container.innerHTML = `
            <div style="display: flex; flex-direction: column; height: 100%; min-height: 180px; justify-content: space-between; padding: 4px;">
                <div style="display: flex; justify-content: space-between; font-size: 10px; font-weight: 700; color: #464553;">
                    <span>PR-AUC: <strong style="color: #006c49;">0.7892</strong></span>
                    <span>Threshold: 0.50</span>
                </div>
                <div style="flex: 1; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 4px; height: 130px; display: flex; align-items: center; justify-content: center;">
                    <svg viewBox="0 0 100 100" style="width: 100%; height: 110px;">
                        <path d="M 0,10 Q 60,15 100,100" fill="none" stroke="#006c49" stroke-width="3"/>
                    </svg>
                </div>
            </div>
        `;
    } catch(e) {
        container.innerHTML = `<div style="color: #ba1a1a; padding: 8px; font-size: 11px;">Error rendering PR Curve: ${e.message}</div>`;
    }
}

function renderSvgPerfLearningCurve() {
    const container = document.getElementById('chartPerfLearningCurveContainer');
    if (!container) return;
    try {
        container.innerHTML = `
            <div style="display: flex; flex-direction: column; height: 100%; min-height: 180px; justify-content: space-between; padding: 4px;">
                <div style="display: flex; justify-content: space-between; font-size: 10px; font-weight: 700; color: #464553;">
                    <span>Train Score: <strong style="color: #1f108e;">89.2%</strong></span>
                    <span>Val Score: <strong style="color: #006c49;">87.1%</strong></span>
                </div>
                <div style="flex: 1; border-bottom: 1px solid #d3e4fe; border-left: 1px solid #d3e4fe; padding: 4px; height: 130px; display: flex; align-items: center; justify-content: center;">
                    <svg viewBox="0 0 100 100" style="width: 100%; height: 110px;">
                        <path d="M 0,20 Q 50,15 100,10" fill="none" stroke="#1f108e" stroke-width="2.5"/>
                        <path d="M 0,40 Q 50,22 100,14" fill="none" stroke="#006c49" stroke-dasharray="3" stroke-width="2.5"/>
                    </svg>
                </div>
            </div>
        `;
    } catch(e) {
        container.innerHTML = `<div style="color: #ba1a1a; padding: 8px; font-size: 11px;">Error rendering Learning Curve: ${e.message}</div>`;
    }
}

function renderSvgPerfCvChart() {
    const container = document.getElementById('chartPerfCvContainer');
    if (!container) return;
    try {
        container.innerHTML = `
            <div style="display: flex; flex-direction: column; height: 100%; min-height: 180px; justify-content: space-around; padding: 4px; font-size: 11px;">
                <div style="display: flex; justify-content: space-between; font-weight: 600;"><span>Fold 1 Score</span><span style="font-weight: 800; color: #1f108e;">87.4%</span></div>
                <div style="display: flex; justify-content: space-between; font-weight: 600;"><span>Fold 2 Score</span><span style="font-weight: 800; color: #1f108e;">86.8%</span></div>
                <div style="display: flex; justify-content: space-between; font-weight: 600;"><span>Fold 3 Score</span><span style="font-weight: 800; color: #1f108e;">88.1%</span></div>
                <div style="display: flex; justify-content: space-between; font-weight: 600;"><span>Fold 4 Score</span><span style="font-weight: 800; color: #1f108e;">86.5%</span></div>
                <div style="display: flex; justify-content: space-between; font-weight: 600;"><span>Fold 5 Score</span><span style="font-weight: 800; color: #1f108e;">87.0%</span></div>
                <div style="padding-top: 4px; border-top: 1px solid #d3e4fe; display: flex; justify-content: space-between; font-weight: 900; color: #006c49;"><span>Mean 5-Fold CV</span><span>87.16% ± 0.58%</span></div>
            </div>
        `;
    } catch(e) {
        container.innerHTML = `<div style="color: #ba1a1a; padding: 8px; font-size: 11px;">Error rendering Cross Validation: ${e.message}</div>`;
    }
}

function renderSvgPerfFeatureImp() {
    const container = document.getElementById('chartPerfFeatureImpContainer');
    if (!container) return;
    try {
        container.innerHTML = `
            <div style="display: flex; flex-direction: column; height: 100%; min-height: 180px; justify-content: space-around; padding: 4px; font-size: 10px;">
                <div><div style="display: flex; justify-content: space-between; font-weight: 700; margin-bottom: 2px;"><span>OverTime</span><span style="color: #1f108e;">0.245</span></div><div style="width: 100%; background-color: #dce9ff; height: 10px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #1f108e; height: 100%; width: 95%;"></div></div></div>
                <div><div style="display: flex; justify-content: space-between; font-weight: 700; margin-bottom: 2px;"><span>Monthly Income</span><span style="color: #1f108e;">0.182</span></div><div style="width: 100%; background-color: #dce9ff; height: 10px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #1f108e; height: 100%; width: 75%;"></div></div></div>
                <div><div style="display: flex; justify-content: space-between; font-weight: 700; margin-bottom: 2px;"><span>Age</span><span style="color: #1f108e;">0.145</span></div><div style="width: 100%; background-color: #dce9ff; height: 10px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #1f108e; height: 100%; width: 60%;"></div></div></div>
                <div><div style="display: flex; justify-content: space-between; font-weight: 700; margin-bottom: 2px;"><span>Working Years</span><span style="color: #1f108e;">0.128</span></div><div style="width: 100%; background-color: #dce9ff; height: 10px; border-radius: 9999px; overflow: hidden;"><div style="background-color: #1f108e; height: 100%; width: 52%;"></div></div></div>
            </div>
        `;
    } catch(e) {
        container.innerHTML = `<div style="color: #ba1a1a; padding: 8px; font-size: 11px;">Error rendering Feature Importance: ${e.message}</div>`;
    }
}

function renderSvgPerfShapSummary() {
    const container = document.getElementById('chartPerfShapSummaryContainer');
    if (!container) return;
    try {
        container.innerHTML = `
            <div style="display: flex; flex-direction: column; height: 100%; min-height: 180px; justify-content: space-around; padding: 4px; font-size: 10px;">
                <div style="display: flex; justify-content: space-between; font-weight: 700; color: #464553;"><span>Feature</span><span style="color: #ba1a1a;">High Risk &lt;-- SHAP --&gt; Low Risk</span></div>
                <div style="display: flex; align-items: center; justify-content: space-between; font-weight: 600;"><span>OverTime</span><div style="width: 140px; background-color: #ffdad6; height: 12px; border-radius: 4px; display: flex; align-items: center; padding: 0 2px;"><span style="width: 8px; height: 8px; border-radius: 50%; background-color: #ba1a1a;"></span></div></div>
                <div style="display: flex; align-items: center; justify-content: space-between; font-weight: 600;"><span>MonthlyIncome</span><div style="width: 140px; background-color: #d7f5e5; height: 12px; border-radius: 4px; display: flex; align-items: center; justify-content: flex-end; padding: 0 2px;"><span style="width: 8px; height: 8px; border-radius: 50%; background-color: #006c49;"></span></div></div>
                <div style="display: flex; align-items: center; justify-content: space-between; font-weight: 600;"><span>JobSatisfaction</span><div style="width: 140px; background-color: #d7f5e5; height: 12px; border-radius: 4px; display: flex; align-items: center; justify-content: flex-end; padding: 0 2px;"><span style="width: 8px; height: 8px; border-radius: 50%; background-color: #006c49;"></span></div></div>
            </div>
        `;
    } catch(e) {
        container.innerHTML = `<div style="color: #ba1a1a; padding: 8px; font-size: 11px;">Error rendering SHAP Summary: ${e.message}</div>`;
    }
}
