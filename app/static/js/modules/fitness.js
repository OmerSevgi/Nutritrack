
async function initFitnessTab() {
    // 1. Fetch and render routine builder
    const res = await secureFetch('/api/fitness/routines');
    if (res && res.ok) {
        const routines = await res.json();
        renderRoutineBuilder(routines);
    }
    
    // 2. Fetch today's routine for tracker
    const todayRes = await secureFetch('/api/fitness/today-routine');
    if (todayRes && todayRes.ok) {
        const routine = await todayRes.json();
        renderTodayTracker(routine);
    }
}

function renderRoutineBuilder(routines) {
    const container = document.getElementById('routineBuilder');
    const days = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'];
    container.innerHTML = '';
    
    days.forEach((day, index) => {
        const routine = routines.find(r => r.day_of_week === index);
        const col = document.createElement('div');
        col.className = 'glass p-4 rounded-xl border border-white/5';
        col.innerHTML = `
            <p class="text-[10px] font-black text-slate-500 uppercase mb-2">${day}</p>
            <div class="space-y-2 mb-4">
                ${routine ? routine.exercises.map(ex => `<p class="text-[10px] text-white font-bold">${ex.name}</p>`).join('') : '<p class="text-[9px] text-slate-600 italic">Boş</p>'}
            </div>
            <button onclick="editRoutine(${index})" class="text-[9px] bg-blue-500/10 text-blue-400 px-2 py-1 rounded">Düzenle</button>
        `;
        container.appendChild(col);
    });
}

function renderTodayTracker(routine) {
    document.getElementById('todayRoutineName').innerText = routine.name;
    const container = document.getElementById('todayExercises');
    container.innerHTML = '';
    
    routine.exercises.forEach(ex => {
        const div = document.createElement('div');
        div.className = 'glass p-5 rounded-2xl border border-white/5';
        div.dataset.name = ex.name;
        div.innerHTML = `
            <p class="text-sm font-black text-white mb-4">${ex.name}</p>
            <div class="space-y-2">
                ${Array.from({length: ex.sets}).map((_, i) => `
                    <div class="flex items-center gap-2 set-row">
                        <span class="text-[10px] text-slate-500 w-8">Set ${i+1}</span>
                        <input type="number" placeholder="kg" class="w-16 bg-slate-900 border border-slate-700 rounded p-1.5 text-center text-xs text-white weight-in">
                        <input type="number" placeholder="tekrar" class="w-16 bg-slate-900 border border-slate-700 rounded p-1.5 text-center text-xs text-white reps-in">
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(div);
    });
}

async function completeWorkout() {
    const exercises = [];
    document.querySelectorAll('#todayExercises > div').forEach(exDiv => {
        const sets = [];
        exDiv.querySelectorAll('.set-row').forEach(row => {
            sets.push({
                weight: row.querySelector('.weight-in').value || 0,
                reps: row.querySelector('.reps-in').value || 0
            });
        });
        exercises.push({ name: exDiv.dataset.name, sets });
    });
    
    const res = await secureFetch('/api/fitness/workout/complete', {
        method: 'POST',
        body: JSON.stringify({ routine_id: 1, exercises }) // Need to dynamic routine_id
    });
    
    if (res && res.ok) {
        const data = await res.json();
        alert('Antrenman tamamlandı! AI Yorumu: ' + data.feedback);
    }
}
