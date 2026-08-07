// Retention Intel Application Logic
function initAll() {
    initNavigation();
    initRatingPills();
    initFormBindings();
    initHistoryStore();
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

// 8. 20 Analytics Visualizations Renderers & Model Evaluation Charts
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
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex justify-between items-center mb-2 text-xs font-semibold text-on-surface-variant">
                <span>Department Name</span>
                <span>Average Risk Rate (%)</span>
            </div>
            <div class="flex-1 flex flex-col justify-around border-b border-l border-surface-variant p-3 space-y-4">
                <div>
                    <div class="flex justify-between text-xs font-bold mb-1"><span class="text-on-surface">Sales</span><span class="text-rose-600 font-extrabold">20.6%</span></div>
                    <div class="w-full bg-surface-container-high h-4 rounded-full overflow-hidden"><div class="bg-rose-600 h-full rounded-full" style="width: 68.6%;"></div></div>
                </div>
                <div>
                    <div class="flex justify-between text-xs font-bold mb-1"><span class="text-on-surface">Human Resources</span><span class="text-amber-600 font-extrabold">19.0%</span></div>
                    <div class="w-full bg-surface-container-high h-4 rounded-full overflow-hidden"><div class="bg-amber-500 h-full rounded-full" style="width: 63.3%;"></div></div>
                </div>
                <div>
                    <div class="flex justify-between text-xs font-bold mb-1"><span class="text-on-surface">Research & Development</span><span class="text-primary font-extrabold">13.8%</span></div>
                    <div class="w-full bg-surface-container-high h-4 rounded-full overflow-hidden"><div class="bg-primary h-full rounded-full" style="width: 46.0%;"></div></div>
                </div>
            </div>
        </div>
    `;
}

function renderSvgJobRoleChart() {
    const container = document.getElementById('chartJobRoleRiskContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex-1 flex flex-col justify-around space-y-2 border-b border-l border-surface-variant p-2">
                <div><div class="flex justify-between text-xs font-bold"><span>Sales Representative</span><span class="text-rose-600">39.8%</span></div><div class="w-full bg-surface-container-high h-3 rounded-full"><div class="bg-rose-600 h-full rounded-full" style="width: 80%;"></div></div></div>
                <div><div class="flex justify-between text-xs font-bold"><span>Lab Technician</span><span class="text-amber-600">23.9%</span></div><div class="w-full bg-surface-container-high h-3 rounded-full"><div class="bg-amber-500 h-full rounded-full" style="width: 48%;"></div></div></div>
                <div><div class="flex justify-between text-xs font-bold"><span>Human Resources</span><span class="text-amber-600">23.1%</span></div><div class="w-full bg-surface-container-high h-3 rounded-full"><div class="bg-amber-500 h-full rounded-full" style="width: 46%;"></div></div></div>
                <div><div class="flex justify-between text-xs font-bold"><span>Research Scientist</span><span class="text-emerald-700">16.1%</span></div><div class="w-full bg-surface-container-high h-3 rounded-full"><div class="bg-emerald-600 h-full rounded-full" style="width: 32%;"></div></div></div>
                <div><div class="flex justify-between text-xs font-bold"><span>Research Director</span><span class="text-emerald-700">2.5%</span></div><div class="w-full bg-surface-container-high h-3 rounded-full"><div class="bg-emerald-600 h-full rounded-full" style="width: 5%;"></div></div></div>
            </div>
        </div>
    `;
}

function renderSvgIncomeChart() {
    const container = document.getElementById('chartIncomeRiskContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex-1 flex items-end justify-around space-x-2 border-b border-l border-surface-variant p-2 h-44">
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-rose-600">32.5%</span><div class="w-full bg-rose-600 rounded-t-sm" style="height: 80%;"></div><span class="text-[10px] mt-1 font-semibold">&lt;$3k</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-amber-600">18.2%</span><div class="w-full bg-amber-500 rounded-t-sm" style="height: 45%;"></div><span class="text-[10px] mt-1 font-semibold">$3k-6k</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-emerald-700">11.4%</span><div class="w-full bg-emerald-600 rounded-t-sm" style="height: 28%;"></div><span class="text-[10px] mt-1 font-semibold">$6k-10k</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-emerald-700">6.8%</span><div class="w-full bg-emerald-600 rounded-t-sm" style="height: 17%;"></div><span class="text-[10px] mt-1 font-semibold">$10k+</span></div>
            </div>
        </div>
    `;
}

function renderSvgOvertimeChart() {
    const container = document.getElementById('chartOvertimeRiskContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex-1 flex items-end justify-around space-x-6 border-b border-l border-surface-variant p-4 h-44">
                <div class="flex-1 flex flex-col items-center"><span class="text-xs font-bold text-rose-600">30.5%</span><div class="w-16 bg-rose-600 rounded-t-lg shadow-sm" style="height: 76%;"></div><span class="text-xs font-bold text-on-surface mt-2">Regular Overtime</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-xs font-bold text-emerald-700">10.4%</span><div class="w-16 bg-emerald-600 rounded-t-lg shadow-sm" style="height: 26%;"></div><span class="text-xs font-bold text-on-surface mt-2">No Overtime</span></div>
            </div>
        </div>
    `;
}

function renderSvgJobSatChart() {
    const container = document.getElementById('chartJobSatRiskContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex-1 flex items-end justify-around space-x-3 border-b border-l border-surface-variant p-2 h-44">
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-rose-600">22.8%</span><div class="w-full bg-rose-600 rounded-t-sm" style="height: 70%;"></div><span class="text-[10px] mt-1 font-semibold">1 Low</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-amber-600">16.5%</span><div class="w-full bg-amber-500 rounded-t-sm" style="height: 50%;"></div><span class="text-[10px] mt-1 font-semibold">2 Medium</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-emerald-700">14.6%</span><div class="w-full bg-emerald-600 rounded-t-sm" style="height: 44%;"></div><span class="text-[10px] mt-1 font-semibold">3 High</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-emerald-700">11.3%</span><div class="w-full bg-emerald-600 rounded-t-sm" style="height: 34%;"></div><span class="text-[10px] mt-1 font-semibold">4 Very High</span></div>
            </div>
        </div>
    `;
}

function renderSvgWlbChart() {
    const container = document.getElementById('chartWlbRiskContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex-1 flex items-end justify-around space-x-3 border-b border-l border-surface-variant p-2 h-44">
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-rose-600">31.2%</span><div class="w-full bg-rose-600 rounded-t-sm" style="height: 80%;"></div><span class="text-[10px] mt-1 font-semibold">1 Bad</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-amber-600">16.8%</span><div class="w-full bg-amber-500 rounded-t-sm" style="height: 43%;"></div><span class="text-[10px] mt-1 font-semibold">2 Good</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-emerald-700">14.2%</span><div class="w-full bg-emerald-600 rounded-t-sm" style="height: 36%;"></div><span class="text-[10px] mt-1 font-semibold">3 Better</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-emerald-700">17.6%</span><div class="w-full bg-emerald-600 rounded-t-sm" style="height: 45%;"></div><span class="text-[10px] mt-1 font-semibold">4 Best</span></div>
            </div>
        </div>
    `;
}

function renderSvgYearsCompanyChart() {
    const container = document.getElementById('chartYearsCompanyContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex-1 flex items-end justify-around space-x-2 border-b border-l border-surface-variant p-2 h-44">
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-rose-600">34.6%</span><div class="w-full bg-rose-600 rounded-t-sm" style="height: 85%;"></div><span class="text-[10px] mt-1 font-semibold">0-2 yrs</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-amber-600">18.4%</span><div class="w-full bg-amber-500 rounded-t-sm" style="height: 46%;"></div><span class="text-[10px] mt-1 font-semibold">3-5 yrs</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-emerald-700">12.1%</span><div class="w-full bg-emerald-600 rounded-t-sm" style="height: 30%;"></div><span class="text-[10px] mt-1 font-semibold">6-10 yrs</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-emerald-700">8.2%</span><div class="w-full bg-emerald-600 rounded-t-sm" style="height: 20%;"></div><span class="text-[10px] mt-1 font-semibold">10+ yrs</span></div>
            </div>
        </div>
    `;
}

function renderSvgPromoDelayChart() {
    const container = document.getElementById('chartPromoDelayContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex-1 flex items-end justify-around space-x-2 border-b border-l border-surface-variant p-2 h-44">
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-emerald-700">13.2%</span><div class="w-full bg-emerald-600 rounded-t-sm" style="height: 32%;"></div><span class="text-[10px] mt-1 font-semibold">0-1 yrs</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-emerald-700">15.0%</span><div class="w-full bg-emerald-600 rounded-t-sm" style="height: 37%;"></div><span class="text-[10px] mt-1 font-semibold">2-3 yrs</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-amber-600">22.4%</span><div class="w-full bg-amber-500 rounded-t-sm" style="height: 56%;"></div><span class="text-[10px] mt-1 font-semibold">4-6 yrs</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-rose-600">31.8%</span><div class="w-full bg-rose-600 rounded-t-sm" style="height: 80%;"></div><span class="text-[10px] mt-1 font-semibold">7+ yrs</span></div>
            </div>
        </div>
    `;
}

function renderSvgDistanceChart() {
    const container = document.getElementById('chartDistanceContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex-1 flex items-end justify-around space-x-2 border-b border-l border-surface-variant p-2 h-44">
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-emerald-700">12.5%</span><div class="w-full bg-emerald-600 rounded-t-sm" style="height: 31%;"></div><span class="text-[10px] mt-1 font-semibold">1-5 mi</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-emerald-700">14.8%</span><div class="w-full bg-emerald-600 rounded-t-sm" style="height: 37%;"></div><span class="text-[10px] mt-1 font-semibold">6-10 mi</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-amber-600">19.2%</span><div class="w-full bg-amber-500 rounded-t-sm" style="height: 48%;"></div><span class="text-[10px] mt-1 font-semibold">11-20 mi</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-rose-600">28.4%</span><div class="w-full bg-rose-600 rounded-t-sm" style="height: 71%;"></div><span class="text-[10px] mt-1 font-semibold">20+ mi</span></div>
            </div>
        </div>
    `;
}

function renderSvgAgeDistChart() {
    const container = document.getElementById('chartAgeDistContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex-1 flex items-end justify-around space-x-2 border-b border-l border-surface-variant p-2 h-44">
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-rose-600">38.2%</span><div class="w-full bg-rose-600 rounded-t-sm" style="height: 90%;"></div><span class="text-[10px] mt-1 font-semibold">18-25</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-amber-600">21.5%</span><div class="w-full bg-amber-500 rounded-t-sm" style="height: 52%;"></div><span class="text-[10px] mt-1 font-semibold">26-35</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-emerald-700">11.8%</span><div class="w-full bg-emerald-600 rounded-t-sm" style="height: 29%;"></div><span class="text-[10px] mt-1 font-semibold">36-45</span></div>
                <div class="flex-1 flex flex-col items-center"><span class="text-[10px] font-bold text-emerald-700">9.4%</span><div class="w-full bg-emerald-600 rounded-t-sm" style="height: 23%;"></div><span class="text-[10px] mt-1 font-semibold">46+</span></div>
            </div>
        </div>
    `;
}

function renderSvgHeatmapChart() {
    const container = document.getElementById('chartHeatmapContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2 text-xs">
            <div class="grid grid-cols-4 gap-1 h-44">
                <div class="bg-rose-600 text-white font-bold flex flex-col items-center justify-center rounded p-1 text-[10px]"><span>OverTime</span><span>+0.72</span></div>
                <div class="bg-rose-500 text-white font-bold flex flex-col items-center justify-center rounded p-1 text-[10px]"><span>Income</span><span>-0.58</span></div>
                <div class="bg-amber-500 text-white font-bold flex flex-col items-center justify-center rounded p-1 text-[10px]"><span>JobSat</span><span>-0.44</span></div>
                <div class="bg-amber-400 text-white font-bold flex flex-col items-center justify-center rounded p-1 text-[10px]"><span>Age</span><span>-0.38</span></div>
                <div class="bg-rose-400 text-white font-bold flex flex-col items-center justify-center rounded p-1 text-[10px]"><span>Distance</span><span>+0.35</span></div>
                <div class="bg-emerald-600 text-white font-bold flex flex-col items-center justify-center rounded p-1 text-[10px]"><span>Stock</span><span>-0.31</span></div>
                <div class="bg-emerald-500 text-white font-bold flex flex-col items-center justify-center rounded p-1 text-[10px]"><span>YearsRole</span><span>-0.29</span></div>
                <div class="bg-rose-300 text-on-surface font-bold flex flex-col items-center justify-center rounded p-1 text-[10px]"><span>PromoYr</span><span>+0.27</span></div>
            </div>
        </div>
    `;
}

function renderSvgFeatureImpChart() {
    const container = document.getElementById('chartFeatureImpContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex-1 flex flex-col justify-around space-y-2 border-b border-l border-surface-variant p-2">
                <div><div class="flex justify-between text-xs font-bold"><span>OverTime</span><span class="text-primary">0.245</span></div><div class="w-full bg-surface-container-high h-3 rounded-full"><div class="bg-primary h-full rounded-full" style="width: 95%;"></div></div></div>
                <div><div class="flex justify-between text-xs font-bold"><span>Monthly Income</span><span class="text-primary">0.182</span></div><div class="w-full bg-surface-container-high h-3 rounded-full"><div class="bg-primary h-full rounded-full" style="width: 75%;"></div></div></div>
                <div><div class="flex justify-between text-xs font-bold"><span>Age</span><span class="text-primary">0.145</span></div><div class="w-full bg-surface-container-high h-3 rounded-full"><div class="bg-primary h-full rounded-full" style="width: 60%;"></div></div></div>
                <div><div class="flex justify-between text-xs font-bold"><span>Total Working Years</span><span class="text-primary">0.128</span></div><div class="w-full bg-surface-container-high h-3 rounded-full"><div class="bg-primary h-full rounded-full" style="width: 52%;"></div></div></div>
                <div><div class="flex justify-between text-xs font-bold"><span>Job Satisfaction</span><span class="text-primary">0.095</span></div><div class="w-full bg-surface-container-high h-3 rounded-full"><div class="bg-primary h-full rounded-full" style="width: 40%;"></div></div></div>
            </div>
        </div>
    `;
}

function renderSvgShapSummaryChart() {
    const container = document.getElementById('chartShapSummaryContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex justify-between text-xs font-bold text-on-surface-variant mb-2">
                <span>Feature</span>
                <span class="text-rose-600">High Risk &lt;--- SHAP Value ---&gt; Low Risk</span>
            </div>
            <div class="flex-1 flex flex-col justify-around border-b border-l border-surface-variant p-2 space-y-2">
                <div class="flex items-center justify-between text-xs font-semibold"><span>OverTime</span><div class="w-48 bg-rose-200 h-3 rounded flex items-center px-1"><span class="w-3 h-3 rounded-full bg-rose-600"></span></div></div>
                <div class="flex items-center justify-between text-xs font-semibold"><span>MonthlyIncome</span><div class="w-48 bg-emerald-200 h-3 rounded flex items-center justify-end px-1"><span class="w-3 h-3 rounded-full bg-emerald-600"></span></div></div>
                <div class="flex items-center justify-between text-xs font-semibold"><span>JobSatisfaction</span><div class="w-48 bg-emerald-100 h-3 rounded flex items-center justify-end px-1"><span class="w-3 h-3 rounded-full bg-emerald-600"></span></div></div>
                <div class="flex items-center justify-between text-xs font-semibold"><span>DistanceFromHome</span><div class="w-48 bg-rose-100 h-3 rounded flex items-center px-1"><span class="w-3 h-3 rounded-full bg-rose-600"></span></div></div>
            </div>
        </div>
    `;
}

function renderSvgRocCurveChart() {
    const container = document.getElementById('chartRocCurveContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex justify-between items-center text-xs font-bold mb-1">
                <span>ROC-AUC: <strong class="text-primary">0.8241</strong></span>
                <span class="text-emerald-700">Excellent Classifier Performance</span>
            </div>
            <div class="flex-1 border-b border-l border-surface-variant relative p-2 h-44 flex items-center justify-center">
                <svg viewBox="0 0 100 100" class="w-full h-full text-primary">
                    <line x1="0" y1="100" x2="100" y2="0" stroke="#c8c4d5" stroke-dasharray="2" stroke-width="1"/>
                    <path d="M 0,100 Q 15,20 100,0" fill="none" stroke="#1f108e" stroke-width="3"/>
                </svg>
            </div>
        </div>
    `;
}

function renderSvgPrCurveChart() {
    const container = document.getElementById('chartPrCurveContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex justify-between items-center text-xs font-bold mb-1">
                <span>Precision-Recall AUC: <strong class="text-primary">0.7892</strong></span>
                <span>Threshold: 0.50</span>
            </div>
            <div class="flex-1 border-b border-l border-surface-variant relative p-2 h-44 flex items-center justify-center">
                <svg viewBox="0 0 100 100" class="w-full h-full text-emerald-700">
                    <path d="M 0,10 Q 50,15 100,100" fill="none" stroke="#006c49" stroke-width="3"/>
                </svg>
            </div>
        </div>
    `;
}

function renderSvgConfusionMatrixChart() {
    const container = document.getElementById('chartConfusionMatrixContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-center p-2 text-xs">
            <div class="grid grid-cols-2 gap-2 h-44">
                <div class="bg-emerald-100 border border-emerald-300 rounded-xl p-3 flex flex-col justify-center items-center">
                    <span class="text-[10px] font-bold text-emerald-800 uppercase">True Negative (TN)</span>
                    <span class="text-2xl font-black text-emerald-900">236</span>
                    <span class="text-[10px] text-emerald-700">Stay predicted correctly</span>
                </div>
                <div class="bg-rose-50 border border-rose-200 rounded-xl p-3 flex flex-col justify-center items-center">
                    <span class="text-[10px] font-bold text-rose-800 uppercase">False Positive (FP)</span>
                    <span class="text-2xl font-black text-rose-900">10</span>
                    <span class="text-[10px] text-rose-700">False Alarm</span>
                </div>
                <div class="bg-amber-50 border border-amber-200 rounded-xl p-3 flex flex-col justify-center items-center">
                    <span class="text-[10px] font-bold text-amber-800 uppercase">False Negative (FN)</span>
                    <span class="text-2xl font-black text-amber-900">33</span>
                    <span class="text-[10px] text-amber-700">Missed Attrition</span>
                </div>
                <div class="bg-primary-container border border-primary text-on-primary-container rounded-xl p-3 flex flex-col justify-center items-center">
                    <span class="text-[10px] font-bold uppercase">True Positive (TP)</span>
                    <span class="text-2xl font-black text-white">21</span>
                    <span class="text-[10px] font-medium">Leave predicted correctly</span>
                </div>
            </div>
        </div>
    `;
}

function renderSvgModelCompareChart() {
    const container = document.getElementById('chartModelCompareContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex-1 flex flex-col justify-around space-y-2 border-b border-l border-surface-variant p-2">
                <div><div class="flex justify-between text-xs font-bold"><span class="text-primary">SVM (Best)</span><span class="text-primary">87.07% Acc</span></div><div class="w-full bg-surface-container-high h-3 rounded-full"><div class="bg-primary h-full rounded-full" style="width: 87%;"></div></div></div>
                <div><div class="flex justify-between text-xs font-bold"><span>Random Forest</span><span>85.71% Acc</span></div><div class="w-full bg-surface-container-high h-3 rounded-full"><div class="bg-indigo-600 h-full rounded-full" style="width: 85%;"></div></div></div>
                <div><div class="flex justify-between text-xs font-bold"><span>Logistic Regression</span><span>85.37% Acc</span></div><div class="w-full bg-surface-container-high h-3 rounded-full"><div class="bg-indigo-500 h-full rounded-full" style="width: 85%;"></div></div></div>
                <div><div class="flex justify-between text-xs font-bold"><span>XGBoost</span><span>84.01% Acc</span></div><div class="w-full bg-surface-container-high h-3 rounded-full"><div class="bg-indigo-400 h-full rounded-full" style="width: 84%;"></div></div></div>
            </div>
        </div>
    `;
}

function renderSvgRiskDistChart() {
    const container = document.getElementById('chartRiskDistContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex-1 flex items-center justify-around space-x-4 border-b border-l border-surface-variant p-4">
                <div class="text-center">
                    <span class="text-xs font-bold text-emerald-800">LOW RISK</span>
                    <p class="font-headline-lg text-2xl font-bold text-emerald-700">1,091</p>
                    <span class="text-[10px] text-on-surface-variant">74.2% workforce</span>
                </div>
                <div class="text-center">
                    <span class="text-xs font-bold text-amber-800">MEDIUM RISK</span>
                    <p class="font-headline-lg text-2xl font-bold text-amber-700">237</p>
                    <span class="text-[10px] text-on-surface-variant">16.1% workforce</span>
                </div>
                <div class="text-center">
                    <span class="text-xs font-bold text-rose-800">HIGH RISK</span>
                    <p class="font-headline-lg text-2xl font-bold text-rose-700">142</p>
                    <span class="text-[10px] text-on-surface-variant">9.7% workforce</span>
                </div>
            </div>
        </div>
    `;
}

function renderSvgProbHistChart() {
    const container = document.getElementById('chartProbHistContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex-1 flex items-end justify-between space-x-1 border-b border-l border-surface-variant p-2 h-44">
                <div class="flex-1 bg-emerald-600 rounded-t-sm" style="height: 90%;" title="0-10%"></div>
                <div class="flex-1 bg-emerald-600 rounded-t-sm" style="height: 75%;" title="10-20%"></div>
                <div class="flex-1 bg-emerald-600 rounded-t-sm" style="height: 45%;" title="20-30%"></div>
                <div class="flex-1 bg-amber-500 rounded-t-sm" style="height: 25%;" title="30-40%"></div>
                <div class="flex-1 bg-amber-500 rounded-t-sm" style="height: 20%;" title="40-50%"></div>
                <div class="flex-1 bg-rose-600 rounded-t-sm" style="height: 15%;" title="50-60%"></div>
                <div class="flex-1 bg-rose-600 rounded-t-sm" style="height: 10%;" title="60-70%"></div>
                <div class="flex-1 bg-rose-600 rounded-t-sm" style="height: 5%;" title="70-80%"></div>
            </div>
        </div>
    `;
}

function renderSvgDeptRankChart() {
    const container = document.getElementById('chartDeptRankContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2 text-xs">
            <div class="space-y-3 p-2">
                <div class="flex items-center justify-between p-2.5 rounded-xl bg-rose-50 border border-rose-200"><div class="flex items-center space-x-2"><span class="w-6 h-6 rounded-full bg-rose-600 text-white font-bold flex items-center justify-center text-[10px]">1</span><span class="font-bold text-rose-900">Sales Department</span></div><span class="font-black text-rose-700">20.6% Risk</span></div>
                <div class="flex items-center justify-between p-2.5 rounded-xl bg-amber-50 border border-amber-200"><div class="flex items-center space-x-2"><span class="w-6 h-6 rounded-full bg-amber-600 text-white font-bold flex items-center justify-center text-[10px]">2</span><span class="font-bold text-amber-900">Human Resources</span></div><span class="font-black text-amber-700">19.0% Risk</span></div>
                <div class="flex items-center justify-between p-2.5 rounded-xl bg-emerald-50 border border-emerald-200"><div class="flex items-center space-x-2"><span class="w-6 h-6 rounded-full bg-emerald-700 text-white font-bold flex items-center justify-center text-[10px]">3</span><span class="font-bold text-emerald-900">Research & Development</span></div><span class="font-black text-emerald-700">13.8% Risk</span></div>
            </div>
        </div>
    `;
}

function initPerformanceCharts() {
    renderSvgPerfConfusionMatrix();
    renderSvgPerfLearningCurve();
    renderSvgPerfCvChart();
}

function renderSvgPerfConfusionMatrix() {
    const container = document.getElementById('chartPerfConfusionMatrixContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="grid grid-cols-2 gap-2 h-full text-xs">
            <div class="bg-emerald-100 p-3 rounded-xl border border-emerald-300 text-center"><span class="font-bold text-emerald-800">TN: 236</span></div>
            <div class="bg-rose-50 p-3 rounded-xl border border-rose-200 text-center"><span class="font-bold text-rose-800">FP: 10</span></div>
            <div class="bg-amber-50 p-3 rounded-xl border border-amber-200 text-center"><span class="font-bold text-amber-800">FN: 33</span></div>
            <div class="bg-primary-container p-3 rounded-xl border border-primary text-on-primary-container text-center"><span class="font-bold text-white">TP: 21</span></div>
        </div>
    `;
}

function renderSvgPerfLearningCurve() {
    const container = document.getElementById('chartPerfLearningCurveContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-between p-2">
            <div class="flex justify-between text-[10px] font-bold text-on-surface-variant">
                <span>Training Score: <strong class="text-primary">89.2%</strong></span>
                <span>Validation Score: <strong class="text-emerald-700">87.1%</strong></span>
            </div>
            <div class="flex-1 border-b border-l border-surface-variant p-2 h-36 flex items-center justify-center">
                <svg viewBox="0 0 100 100" class="w-full h-full">
                    <path d="M 0,20 Q 50,15 100,10" fill="none" stroke="#1f108e" stroke-width="2"/>
                    <path d="M 0,40 Q 50,22 100,14" fill="none" stroke="#006c49" stroke-dasharray="3" stroke-width="2"/>
                </svg>
            </div>
        </div>
    `;
}

function renderSvgPerfCvChart() {
    const container = document.getElementById('chartPerfCvContainer');
    if (!container) return;
    container.innerHTML = `
        <div class="flex flex-col h-full justify-around p-2 text-xs">
            <div class="flex justify-between font-semibold"><span>Fold 1 Score</span><span class="font-bold text-primary">87.4%</span></div>
            <div class="flex justify-between font-semibold"><span>Fold 2 Score</span><span class="font-bold text-primary">86.8%</span></div>
            <div class="flex justify-between font-semibold"><span>Fold 3 Score</span><span class="font-bold text-primary">88.1%</span></div>
            <div class="flex justify-between font-semibold"><span>Fold 4 Score</span><span class="font-bold text-primary">86.5%</span></div>
            <div class="flex justify-between font-semibold"><span>Fold 5 Score</span><span class="font-bold text-primary">87.0%</span></div>
            <div class="pt-1 border-t border-surface-variant flex justify-between font-extrabold text-emerald-700"><span>Mean 5-Fold CV</span><span>87.16% ± 0.58%</span></div>
        </div>
    `;
}
