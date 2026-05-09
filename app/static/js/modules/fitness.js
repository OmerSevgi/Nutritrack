async function fetchWorkouts() {
    const res = await secureFetch('/api/fitness/workouts');
    if (!res) return;
    const data = await res.json();
    const list = document.getElementById('workoutList');
    if (list) {
        list.innerHTML = '';
        if (Array.isArray(data)) {
            data.forEach(w => {
                const div = document.createElement('div');
                div.className = 'glass p-6 rounded-[2rem] space-y-4 mb-4';
                div.innerHTML = `
                    <div class="flex justify-between items-start">
                        <p class="text-xs font-bold text-slate-500 uppercase">${w.date}</p>
                        <button onclick="deleteWorkout(${w.id})" class="text-slate-600 hover:text-red-400"><i class="fa-solid fa-trash-can text-xs"></i></button>
                    </div>
                    <p class="text-sm font-bold text-white">${w.description}</p>
                    <div class="bg-blue-500/5 p-4 rounded-2xl text-xs text-slate-300 italic border border-blue-500/10">"${w.feedback}"</div>
                `;
                list.appendChild(div);
            });
        }
    }
}

async function fetchWeeklyReport() {
    const res = await secureFetch('/api/fitness/stats/report');
    if (!res) return;
    const data = await res.json();
    const el = document.getElementById('weeklyAIReport');
    if (el && res.ok) { 
        el.innerText = data.report; 
        el.classList.remove('hidden'); 
    }
}

async function fetchWeeklyStats() {
    const res = await secureFetch('/api/fitness/stats/weekly');
    if (!res) return;
    const data = await res.json();
    const grid = document.getElementById('exerciseStatsGrid');
    if (grid) {
        grid.innerHTML = '';
        if (data && typeof data === 'object') {
            Object.entries(data).forEach(([name, s]) => {
                const div = document.createElement('div');
                div.className = 'glass p-4 rounded-2xl text-center';
                div.innerHTML = `<p class="text-[8px] text-slate-500 uppercase font-black mb-1">${name}</p><p class="text-sm font-black text-white">${s.max_weight}kg</p>`;
                grid.appendChild(div);
            });
        }
    }
}

async function deleteWorkout(id) {
    if (confirm('Silinsin mi?')) {
        await secureFetch(`/api/fitness/workout/${id}`, { method: 'DELETE' });
        fetchWorkouts();
    }
}
