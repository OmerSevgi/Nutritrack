
async function initFitnessTab() {
    const res = await secureFetch('/api/fitness/routines');
    if (res && res.ok) {
        window.allRoutines = await res.json();
        renderRoutineBuilder(window.allRoutines);
    }
    const todayRes = await secureFetch('/api/fitness/today-routine');
    if (todayRes && todayRes.ok) {
        const routine = await todayRes.json();
        window.currentRoutineId = routine.id;
        renderTodayTracker(routine);
    } else {
        document.getElementById('todayRoutineName').innerText = "Bugün için program yok.";
    }
}

function renderRoutineBuilder(routines) {
    const container = document.getElementById('routineBuilder');
    const days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'];
    
    container.innerHTML = `
        <div class="space-y-6">
            <div class="flex items-center justify-between">
                <div class="grid grid-cols-4 md:grid-cols-7 gap-2 w-full">
                    ${days.map((day, i) => `
                        <button onclick="selectDay(${i})" id="dayBtn-${i}" class="px-2 py-4 rounded-xl bg-slate-900 border border-slate-800 text-[10px] font-black text-slate-400 hover:text-white hover:border-blue-500/50 transition-all">
                            ${day}
                        </button>
                    `).join('')}
                </div>
            </div>
            <div id="dayDetail" class="p-8 bg-slate-950/50 rounded-3xl border border-white/5 min-h-[200px]">
                <p class="text-slate-500 text-sm text-center pt-16 font-bold italic">Antrenmanını görüntülemek veya düzenlemek için bir gün seç.</p>
            </div>
        </div>
    `;
    // Select today by default
    selectDay(new Date().getDay() === 0 ? 6 : new Date().getDay() - 1);
}

function selectDay(dayIndex) {
    // UI Update
    document.querySelectorAll('[id^="dayBtn-"]').forEach(btn => btn.classList.remove('bg-blue-600', 'text-white'));
    document.getElementById(`dayBtn-${dayIndex}`).classList.add('bg-blue-600', 'text-white');
    
    const routine = window.allRoutines.find(r => r.day_of_week === dayIndex);
    const detail = document.getElementById('dayDetail');
    
    detail.innerHTML = `
        <div class="flex justify-between items-center mb-6">
            <h4 class="text-lg font-black text-white">${routine ? routine.name : 'Program Tanımlanmamış'}</h4>
            <button onclick="editRoutine(${dayIndex})" class="text-[10px] bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-bold uppercase transition">Düzenle</button>
        </div>
        <div class="space-y-2">
            ${routine ? routine.exercises.map(ex => `
                <div class="flex justify-between items-center bg-slate-900/50 p-3 rounded-xl border border-white/5">
                    <span class="text-xs font-bold text-white">${ex.name}</span>
                    <span class="text-[10px] text-slate-500 font-black uppercase">${ex.sets} SET X ${ex.reps} TEKRAR</span>
                </div>
            `).join('') : '<p class="text-slate-600 text-xs italic">Bu gün için herhangi bir antrenman eklenmemiş.</p>'}
        </div>
    `;
}


function editRoutine(dayIndex) {
    document.getElementById('modalDayIndex').value = dayIndex;
    const routine = window.allRoutines.find(r => r.day_of_week === dayIndex);
    document.getElementById('routineName').value = routine ? routine.name : '';
    document.getElementById('exerciseList').innerHTML = '';
    
    if (routine) {
        routine.exercises.forEach(ex => addExerciseRow(ex.name, ex.sets, ex.reps));
    } else {
        addExerciseRow();
    }
    document.getElementById('routineModal').classList.remove('hidden');
}

function closeModal() { document.getElementById('routineModal').classList.add('hidden'); }

function addExerciseRow(name = '', sets = 3, reps = 10) {
    const div = document.createElement('div');
    div.className = 'grid grid-cols-3 gap-2 items-center bg-slate-800 p-3 rounded-lg';
    div.innerHTML = `
        <input type="text" value="${name}" placeholder="Hareket" class="col-span-1 bg-transparent border-none text-xs text-white ex-name">
        <input type="number" value="${sets}" class="w-12 bg-slate-950 border border-slate-700 rounded p-1 text-xs text-white text-center ex-sets">
        <select class="w-20 bg-slate-950 border border-slate-700 rounded p-1 text-xs text-white ex-reps">
            <option value="Tükeniş" ${reps=='Tükeniş'?'selected':''}>Tükeniş</option>
            ${[5,8,10,12,15,20].map(r => `<option value="${r}" ${reps==r?'selected':''}>${r}</option>`).join('')}
        </select>
    `;
    document.getElementById('exerciseList').appendChild(div);
}

async function saveRoutine() {
    const day = parseInt(document.getElementById('modalDayIndex').value);
    const name = document.getElementById('routineName').value;
    const exercises = [];
    document.querySelectorAll('#exerciseList > div').forEach(row => {
        exercises.push({
            name: row.querySelector('.ex-name').value,
            sets: row.querySelector('.ex-sets').value,
            reps: row.querySelector('.ex-reps').value
        });
    });
    
    // Check if updating or creating (simplified for now: always delete and post)
    const existing = window.allRoutines.find(r => r.day_of_week === day);
    if (existing) {
        await secureFetch(`/api/fitness/routines/${existing.id}`, {
            method: 'PUT',
            body: JSON.stringify({ name, exercises })
        });
    } else {
        await secureFetch('/api/fitness/routines', {
            method: 'POST',
            body: JSON.stringify({ day_of_week: day, name, exercises })
        });
    }
    closeModal();
    initFitnessTab();
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
        body: JSON.stringify({ routine_id: window.currentRoutineId, exercises })
    });
    
    if (res && res.ok) {
        const data = await res.json();
        alert('Antrenman tamamlandı! AI Yorumu: ' + data.feedback);
    }
}
