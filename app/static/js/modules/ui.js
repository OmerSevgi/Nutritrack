async function fetchWeightHistory() {
    const res = await secureFetch('/api/auth/weight-history');
    if (!res) return;
    const data = await res.json();
    if (Array.isArray(data)) initWeightChart(data);
}

let weightChart;
function initWeightChart(data) {
    const ctx = document.getElementById('weightChart');
    if (!ctx) return;
    if (weightChart) weightChart.destroy();
    weightChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: { 
            labels: data.map(d => d.date), 
            datasets: [{ 
                data: data.map(d => d.weight), 
                borderColor: '#6366f1', 
                tension: 0.4, 
                fill: true, 
                backgroundColor: 'rgba(99, 102, 241, 0.1)' 
            }] 
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });
}

async function askFridge() {
    const btn = document.getElementById('fridgeBtn');
    const resEl = document.getElementById('fridgeResult');
    if (!btn || !resEl) return;

    setButtonLoading(btn, true);
    resEl.classList.remove('hidden'); 
    resEl.innerText = 'Şef hazırlanıyor...';
    
    const res = await secureFetch('/api/ai/fridge-assistant', { 
        method: 'POST', 
        body: JSON.stringify({ ingredients: document.getElementById('fridgeInput').value }) 
    });
    
    setButtonLoading(btn, false);
    if (!res) return;
    const data = await res.json();
    resEl.innerHTML = data.recipe.replace(/\n/g, '<br>');
}

async function fetchWeeklyHistory() {
    const res = await secureFetch('/api/nutrition/weekly-history');
    if (!res) return;
    const data = await res.json();
    if (Array.isArray(data)) initHistoryChart(data);
}

let historyChart;
function initHistoryChart(data) {
    const ctx = document.getElementById('historyChart');
    if (!ctx) return;
    if (historyChart) historyChart.destroy();
    historyChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: { 
            labels: data.map(d => d.date), 
            datasets: [{ 
                data: data.map(d => d.calories), 
                backgroundColor: '#10b981', 
                borderRadius: 5 
            }] 
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });
}

function toggleChat() { 
    const chat = document.getElementById('aiChatWindow');
    if (chat) chat.classList.toggle('hidden'); 
}

function changeDate(days) {
    const d = new Date(currentDate);
    d.setDate(d.getDate() + days);
    const newDate = d.toISOString().split('T')[0];
    const dp = document.getElementById('datePicker');
    if (dp) dp.value = newDate;
    fetchSummary(newDate);
}
