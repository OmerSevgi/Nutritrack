let currentDate = new Date().toISOString().split('T')[0];

function switchTab(tab) {
    const tabs = ['nutrition', 'fitness', 'progress'];
    tabs.forEach(t => {
        const btn = document.getElementById(t + 'TabBtn');
        const sec = document.getElementById(t + 'Section');
        if (t === tab) {
            if (btn) btn.className = 'px-8 py-3 rounded-xl bg-emerald-500 text-white text-sm font-black transition-all duration-500 shadow-xl shadow-emerald-500/20 flex items-center gap-2';
            if (sec) sec.classList.remove('hidden');
        } else {
            if (btn) btn.className = 'px-8 py-3 rounded-xl text-slate-400 text-sm font-black hover:text-white transition-all duration-500 flex items-center gap-2';
            if (sec) sec.classList.add('hidden');
        }
    });
    if (tab === 'fitness') { fetchWorkouts(); fetchWeeklyStats(); fetchWeeklyReport(); }
    if (tab === 'progress') { fetchWeightHistory(); }
}

// Form Handlers
document.addEventListener('DOMContentLoaded', () => {
    const manualForm = document.getElementById('manualLogForm');
    if (manualForm) {
        manualForm.onsubmit = async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button');
            const name = document.getElementById('foodName').value;
            const qty = document.getElementById('foodQty').value;
            const cal = document.getElementById('foodCal').value;
            const pro = document.getElementById('foodPro').value;
            
            setButtonLoading(btn, true);
            const res = await secureFetch('/api/nutrition/food', {
                method: 'POST',
                body: JSON.stringify({ 
                    name, calories: cal, protein: pro, 
                    carbs: document.getElementById('foodCarb').value, 
                    fats: document.getElementById('foodFat').value 
                })
            });
            
            if (res && res.ok) {
                const foodData = await res.json();
                await secureFetch('/api/nutrition/log', {
                    method: 'POST',
                    body: JSON.stringify({ food_item_id: foodData.id, quantity: qty, meal_type: 'manual' })
                });
                e.target.reset();
                fetchSummary();
                fetchWeeklyHistory();
            }
            setButtonLoading(btn, false);
        };
    }

    const aiLogForm = document.getElementById('aiLogForm');
    if (aiLogForm) {
        aiLogForm.onsubmit = async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button');
            const input = document.getElementById('aiInput');
            if (!input.value) return;
            
            setButtonLoading(btn, true);
            await secureFetch('/api/nutrition/log-ai', { method: 'POST', body: JSON.stringify({ text: input.value }) });
            setButtonLoading(btn, false);
            input.value = ''; fetchSummary(); fetchWeeklyHistory();
        };
    }

    const workoutForm = document.getElementById('workoutForm');
    if (workoutForm) {
        workoutForm.onsubmit = async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button');
            const input = document.getElementById('workoutInput');
            setButtonLoading(btn, true);
            await secureFetch('/api/fitness/workout', { method: 'POST', body: JSON.stringify({ text: input.value }) });
            setButtonLoading(btn, false);
            input.value = ''; fetchWorkouts();
        };
    }

    const weightForm = document.getElementById('weightForm');
    if (weightForm) {
        weightForm.onsubmit = async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button');
            const weight = document.getElementById('weightInput').value;
            setButtonLoading(btn, true);
            await secureFetch('/api/auth/weight', { method: 'POST', body: JSON.stringify({ weight }) });
            setButtonLoading(btn, false);
            fetchWeightHistory(); fetchSummary();
        };
    }

    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.onsubmit = async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button');
            const input = document.getElementById('chatInput');
            if (!input.value) return;
            
            const msgDiv = document.createElement('div');
            msgDiv.className = 'text-xs text-slate-300 bg-slate-800 p-3 rounded-xl';
            msgDiv.innerText = input.value;
            document.getElementById('chatMessages').appendChild(msgDiv);
            
            const text = input.value;
            input.value = '';
            setButtonLoading(btn, true);
            const res = await secureFetch('/api/ai/ask-coach', { method: 'POST', body: JSON.stringify({ query: text }) });
            setButtonLoading(btn, false);
            
            if (res && res.ok) {
                const data = await res.json();
                const replyDiv = document.createElement('div');
                replyDiv.className = 'text-xs text-emerald-300 bg-emerald-500/10 p-3 rounded-xl';
                replyDiv.innerText = data.response;
                document.getElementById('chatMessages').appendChild(replyDiv);
            }
        };
    }
});

window.onload = () => {
    fetchSummary();
    fetchWeeklyHistory();
    const dp = document.getElementById('datePicker');
    if (dp) dp.value = currentDate;
    
    // Fetch user profile for name and streak
    secureFetch('/api/auth/profile').then(res => res.json()).then(data => {
        if (data.username) document.getElementById('userNameDisplay').innerText = data.username;
        if (data.fitness_program) {
            const programInput = document.getElementById('fitnessProgramInput');
            if (programInput) programInput.value = data.fitness_program;
        }
    });
};

function toggleProgramEditor() {
    const editor = document.getElementById('programEditor');
    const chevron = document.getElementById('programChevron');
    if (editor) {
        editor.classList.toggle('hidden');
        if (chevron) {
            chevron.classList.toggle('fa-chevron-down');
            chevron.classList.toggle('fa-chevron-up');
        }
    }
}

async function saveFitnessProgram() {
    const btn = document.getElementById('saveProgramBtn');
    const program = document.getElementById('fitnessProgramInput').value;
    
    setButtonLoading(btn, true);
    const res = await secureFetch('/api/auth/profile', {
        method: 'PUT',
        body: JSON.stringify({ fitness_program: program })
    });
    setButtonLoading(btn, false);
    
    if (res && res.ok) {
        alert('Programınız başarıyla kaydedildi!');
        toggleProgramEditor();
    }
}
