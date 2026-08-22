// SkillSetu Frontend Interactive Logic & Dashboard Charts

document.addEventListener('DOMContentLoaded', () => {
    // 1. Registration Form Interactivity
    const registrationForm = document.getElementById('registrationForm');
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const successBox = document.getElementById('regSuccess');
            successBox.classList.remove('hidden');
            successBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            // --- BACKEND PLUG-IN NOTE ---
            // In production: POST request to FastAPI backend endpoint `/api/v1/trainees` 
            // storing encrypted PII in PostgreSQL with consent timestamp.
        });
    }

    // 2. AI Reasoning Simulation
    const runAiBtn = document.getElementById('runAiBtn');
    if (runAiBtn) {
        runAiBtn.addEventListener('click', function() {
            const loading = document.getElementById('aiLoading');
            const resultCard = document.getElementById('aiResultCard');
            
            loading.classList.remove('hidden');
            resultCard.classList.add('hidden');

            setTimeout(() => {
                loading.classList.add('hidden');
                resultCard.classList.remove('hidden');
                resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 1000);

            // --- BACKEND PLUG-IN NOTE ---
            // In production: POST request to FastAPI backend endpoint `/api/v1/ai/analyze`
            // passing trainee feedback string to Groq API client with system prompt for classification.
        });
    }

    // 3. Chart.js Initializations
    // Conversion Bar Chart
    const ctxBar = document.getElementById('conversionChart');
    let conversionChart;
    if (ctxBar) {
        conversionChart = new Chart(ctxBar.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Pune', 'Nagpur', 'Thane', 'Aurangabad', 'Nashik'],
                datasets: [{
                    label: 'Employment Conversion %',
                    data: [68, 74, 82, 61, 70],
                    backgroundColor: '#1e3a8a',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, max: 100 } }
            }
        });
    }

    // Outcome Donut Chart
    const ctxDonut = document.getElementById('outcomeDonut');
    if (ctxDonut) {
        new Chart(ctxDonut.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Employed (Salaried)', 'Self-Employed', 'Still Searching', 'Higher Studies'],
                datasets: [{
                    data: [62, 12, 18, 8],
                    backgroundColor: ['#1e3a8a', '#0f766e', '#f59e0b', '#64748b']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } } }
            }
        });
    }

    // Simple District Filter Interactivity for Dashboard
    const districtFilter = document.getElementById('districtFilter');
    if (districtFilter && conversionChart) {
        districtFilter.addEventListener('change', function(e) {
            const val = e.target.value;
            if(val === 'pune') {
                conversionChart.data.datasets[0].data = [58, 58, 58, 58, 58];
                document.getElementById('policyInsightText').innerHTML = '"Analysis of Pune district cohorts shows a <strong>38% skill-mismatch rate</strong> in industrial manufacturing courses. Immediate curriculum upgrade recommended."';
            } else if(val === 'nagpur') {
                conversionChart.data.datasets[0].data = [74, 74, 74, 74, 74];
                document.getElementById('policyInsightText').innerHTML = '"Nagpur district exhibits high tech adoption with a <strong>76% web developer placement rate</strong>. Recommend expanding IT incubation linkages."';
            } else {
                conversionChart.data.datasets[0].data = [68, 74, 82, 61, 70];
                document.getElementById('policyInsightText').innerHTML = '"Statewide aggregated analysis indicates a <strong>68.4% overall employment conversion</strong> at 90 days. Wage mismatch remains the primary barrier in tier-2 districts."';
            }
            conversionChart.update();
        });
    }
});