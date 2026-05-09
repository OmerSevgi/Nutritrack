async function fetchSummary(date = currentDate) {
    currentDate = date;
    const dateDisplay = document.getElementById('selectedDateDisplay');
    if (dateDisplay) {
        dateDisplay.innerText = date === new Date().toISOString().split('T')[0] ? 'BUGÜN' : date;
    }
    
    const res = await secureFetch(`/api/nutrition/summary?date=${date}`);
    if (!res) return;
    const data = await res.json();
    if (res.ok) updateNutritionUI(data);
}

function updateNutritionUI(data) {
    try {
        const setVal = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.innerText = Math.round(val || 0);
        };
        const setBar = (id, cur, target) => {
            const el = document.getElementById(id);
            if (el) el.style.width = (target && target > 0) ? `${Math.min((cur / target) * 100, 100)}%` : '0%';
        };

        setVal('calDisplay', data.calories);
        setVal('proDisplay', data.protein);
        setVal('carbDisplay', data.carbs);
        setVal('fatDisplay', data.fats);
        setVal('nutriScoreDisplay', data.nutri_score || 0);

        if (data.targets) {
            setBar('calBar', data.calories, data.targets.calories);
            setBar('proBar', data.protein, data.targets.protein);
            setBar('carbBar', data.carbs, data.targets.carbs);
            setBar('fatBar', data.fats, data.targets.fats);
        }

        const waterEl = document.getElementById('waterDisplay');
        if (waterEl) waterEl.innerText = Math.round(data.water || 0);
        
        const list = document.getElementById('foodEntriesList');
        if (list) {
            list.innerHTML = '';
            if (!data.meals || data.meals.length === 0) {
                list.innerHTML = '<p class="text-slate-600 text-center py-10 font-bold italic uppercase tracking-tighter">Henüz bir kayıt yok</p>';
            } else {
                data.meals.forEach((meal, idx) => {
                    const div = document.createElement('div');
                    div.className = 'glass rounded-3xl overflow-hidden border-white/5 mb-4';
                    div.innerHTML = `
                        <div class="p-6 cursor-pointer hover:bg-white/5 transition flex items-center justify-between" onclick="toggleMealDetails(${idx})">
                            <div class="flex items-center gap-4">
                                <div class="h-10 w-10 bg-emerald-500/10 rounded-xl flex items-center justify-center text-emerald-400">
                                    <i class="fa-solid ${meal.is_ai ? 'fa-wand-magic-sparkles' : 'fa-utensils'} text-xs"></i>
                                </div>
                                <div>
                                    <p class="font-bold text-sm text-white">${meal.title}</p>
                                    <p class="text-[9px] text-slate-500 font-bold uppercase tracking-widest mt-1">
                                        P: ${meal.total_protein}g | K: ${meal.total_carbs}g | Y: ${meal.total_fats}g
                                    </p>
                                </div>
                            </div>
                            <div class="flex items-center gap-6">
                                <div class="text-right">
                                    <p class="font-black text-emerald-400">${meal.total_calories} <span class="text-[8px] text-slate-500 uppercase">kcal</span></p>
                                </div>
                                <button onclick="event.stopPropagation(); deleteMealGroup('${meal.title.replace(/'/g, "\\'")}')" class="text-slate-600 hover:text-red-400"><i class="fa-solid fa-trash-can text-xs"></i></button>
                            </div>
                        </div>
                        <div id="meal-details-${idx}" class="hidden p-6 bg-slate-950/20 border-t border-white/5 space-y-3">
                            ${meal.items.map(it => `
                                <div class="flex justify-between items-center text-[11px]">
                                    <span class="text-slate-300 font-medium">${it.name} (${it.quantity}${it.unit})</span>
                                    <div class="flex gap-4 text-slate-500 font-bold">

                                        <span>${it.calories} kcal</span>
                                        <span class="text-blue-400/80">P: ${it.protein}</span>
                                        <span class="text-amber-400/80">K: ${it.carbs}</span>
                                        <span class="text-rose-400/80">Y: ${it.fats}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    `;
                    list.appendChild(div);
                });

            }
        }
    } catch (err) {
        console.error("UI güncelleme hatası:", err);
    }
}

function toggleMealDetails(idx) {
    const el = document.getElementById(`meal-details-${idx}`);
    if (el) el.classList.toggle('hidden');
}

async function addWater(amount) {
    await secureFetch('/api/nutrition/water', { method: 'POST', body: JSON.stringify({ amount }) });
    fetchSummary();
}

async function resetWater() {
    if (confirm('Sıfırlansın mı?')) {
        await secureFetch('/api/nutrition/water', { method: 'DELETE' });
        fetchSummary();
    }
}

async function deleteMealGroup(promptText) {
    if (confirm('Silinsin mi?')) {
        await secureFetch('/api/nutrition/log/group', { method: 'DELETE', body: JSON.stringify({ prompt_text: promptText, date: currentDate }) });
        fetchSummary();
    }
}
