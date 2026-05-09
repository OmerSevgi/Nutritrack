    // Token yönetimi
    const getToken = () => localStorage.getItem('token');
    
    // Merkezi fetch fonksiyonu
    async function secureFetch(url, options = {}) {
        let token = getToken();
        if (!token) { window.location.href = '/auth'; return null; }
        
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        let res = await fetch(url, options);
        
        // Token süresi dolmuş veya geçersizse yenilemeyi dene
        if (res.status === 401) {
            const refreshRes = await fetch('/api/auth/refresh', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
            });
            
            if (refreshRes.ok) {
                const data = await refreshRes.json();
                localStorage.setItem('token', data.auth_token);
                token = data.auth_token;
                
                // İsteği yeni token ile tekrarla
                options.headers['Authorization'] = `Bearer ${token}`;
                res = await fetch(url, options);
            } else {
                console.error("Oturum süresi doldu, giriş sayfasına yönlendiriliyor.");
                localStorage.removeItem('token');
                window.location.href = '/auth';
                return null;
            }
        }
        return res;
    }

    let currentDate = new Date().toISOString().split('T')[0];

    // TAB SYSTEM
    function switchTab(tab) {
        const tabs = ['nutrition', 'fitness', 'progress'];
        const btns = {
            nutrition: document.getElementById('nutritionTabBtn'),
            fitness: document.getElementById('fitnessTabBtn'),
            progress: document.getElementById('progressTabBtn')
        };
        const sections = {
            nutrition: document.getElementById('nutritionSection'),
            fitness: document.getElementById('fitnessSection'),
            progress: document.getElementById('progressSection')
        };

        tabs.forEach(t => {
            if (t === tab) {
                btns[t].className = 'px-8 py-3 rounded-xl bg-emerald-500 text-white text-sm font-black transition-all duration-500 shadow-xl shadow-emerald-500/20 flex items-center gap-2';
                sections[t].classList.remove('hidden');
            } else {
                btns[t].className = 'px-8 py-3 rounded-xl text-slate-400 text-sm font-black hover:text-white transition-all duration-500 flex items-center gap-2';
                sections[t].classList.add('hidden');
            }
        });

        if (tab === 'fitness') { fetchWorkouts(); fetchWeeklyStats(); fetchWeeklyReport(); }
        if (tab === 'progress') { fetchWeightHistory(); }
    }

    // AI Request Loading Helper
    function setButtonLoading(btn, isLoading) {
        if (isLoading) {
            btn.dataset.originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin mr-2"></i> İşleniyor...';
            btn.disabled = true;
            btn.classList.add('opacity-50', 'cursor-not-allowed');
        } else {
            btn.innerHTML = btn.dataset.originalText;
            btn.disabled = false;
            btn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }

    // NUTRITION LOGIC
    async function fetchSummary(date = currentDate) {
        currentDate = date;
        document.getElementById('selectedDateDisplay').innerText = date === new Date().toISOString().split('T')[0] ? 'BUGÜN' : date;
        
        const res = await secureFetch(`/api/nutrition/summary?date=${date}`);
        if (!res) return;
        const data = await res.json();
        if (res.ok) updateUI(data);
    }

    function updateUI(data) {
        console.log("DEBUG: Updating UI with data:", data);
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
                        div.className = 'glass rounded-3xl overflow-hidden border-white/5';
                        div.innerHTML = `
                            <div class="p-6 cursor-pointer hover:bg-white/5 transition flex items-center justify-between" onclick="toggleMealDetails(${idx})">
                                <div class="flex items-center gap-4">
                                    <div class="h-10 w-10 bg-emerald-500/10 rounded-xl flex items-center justify-center text-emerald-400">
                                        <i class="fa-solid ${meal.is_ai ? 'fa-wand-magic-sparkles' : 'fa-utensils'} text-xs"></i>
                                    </div>
                                    <p class="font-bold text-sm text-white">${meal.title}</p>
                                </div>
                                <div class="flex items-center gap-6">
                                    <div class="text-right">
                                        <p class="font-black text-emerald-400">${meal.total_calories} <span class="text-[8px] text-slate-500 uppercase">kcal</span></p>
                                    </div>
                                    <button onclick="event.stopPropagation(); deleteMealGroup('${meal.title.replace(/'/g, "\\'")}')" class="text-slate-600 hover:text-red-400"><i class="fa-solid fa-trash-can text-xs"></i></button>
                                </div>
                            </div>
                            <div id="meal-details-${idx}" class="hidden p-6 bg-slate-950/20 border-t border-white/5 space-y-3">
                                ${meal.items.map(it => `<div class="flex justify-between text-xs text-slate-400"><span>${it.name} (${it.quantity})</span><span>${it.total_calories} kcal</span></div>`).join('')}
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
        document.getElementById(`meal-details-${idx}`).classList.toggle('hidden');
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

    // FITNESS LOGIC
    async function fetchWorkouts() {
        const res = await secureFetch('/api/fitness/workouts');
        if (!res) return;
        const data = await res.json();
        const list = document.getElementById('workoutList');
        list.innerHTML = '';
        if (Array.isArray(data)) {
            data.forEach(w => {
                const div = document.createElement('div');
                div.className = 'glass p-6 rounded-[2rem] space-y-4';
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

    async function fetchWeeklyReport() {
        const res = await secureFetch('/api/fitness/stats/report');
        if (!res) return;
        const data = await res.json();
        const el = document.getElementById('weeklyAIReport');
        if (res.ok) { el.innerText = data.report; el.classList.remove('hidden'); }
    }

    async function fetchWeeklyStats() {
        const res = await secureFetch('/api/fitness/stats/weekly');
        if (!res) return;
        const data = await res.json();
        const grid = document.getElementById('exerciseStatsGrid');
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

    // PROGRESS LOGIC
    async function fetchWeightHistory() {
        const res = await secureFetch('/api/auth/weight-history');
        if (!res) return;
        const data = await res.json();
        if (Array.isArray(data)) initWeightChart(data);
    }

    let weightChart;
    function initWeightChart(data) {
        const ctx = document.getElementById('weightChart').getContext('2d');
        if (weightChart) weightChart.destroy();
        weightChart = new Chart(ctx, {
            type: 'line',
            data: { labels: data.map(d => d.date), datasets: [{ data: data.map(d => d.weight), borderColor: '#6366f1', tension: 0.4, fill: true, backgroundColor: 'rgba(99, 102, 241, 0.1)' }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });
    }

    // FRIDGE
    async function askFridge() {
        const btn = document.getElementById('fridgeBtn');
        const resEl = document.getElementById('fridgeResult');
        setButtonLoading(btn, true);
        resEl.classList.remove('hidden'); resEl.innerText = 'Şef hazırlanıyor...';
        const res = await secureFetch('/api/ai/fridge-assistant', { method: 'POST', body: JSON.stringify({ ingredients: document.getElementById('fridgeInput').value }) });
        setButtonLoading(btn, false);
        if (!res) return;
        const data = await res.json();
        resEl.innerHTML = data.recipe.replace(/\n/g, '<br>');
    }

    // FORMS
    document.getElementById('manualLogForm').onsubmit = async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        const name = document.getElementById('foodName').value;
        const qty = document.getElementById('foodQty').value;
        const cal = document.getElementById('foodCal').value;
        const pro = document.getElementById('foodPro').value;
        const carb = document.getElementById('foodCarb').value;
        const fat = document.getElementById('foodFat').value;
        
        setButtonLoading(btn, true);
        const res = await secureFetch('/api/nutrition/food', {
            method: 'POST',
            body: JSON.stringify({ name: name, calories: cal, protein: pro, carbs: carb, fats: fat })
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

    document.getElementById('aiLogForm').onsubmit = async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        const input = document.getElementById('aiInput');
        const text = input.value;
        
        setButtonLoading(btn, true);
        await secureFetch('/api/nutrition/log-ai', { method: 'POST', body: JSON.stringify({ text }) });
        
        setButtonLoading(btn, false);
        input.value = ''; fetchSummary(); fetchWeeklyHistory();
    };

    document.getElementById('workoutForm').onsubmit = async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        const text = document.getElementById('workoutInput').value;
        
        setButtonLoading(btn, true);
        await secureFetch('/api/fitness/workout', { method: 'POST', body: JSON.stringify({ text }) });
        setButtonLoading(btn, false);
        
        document.getElementById('workoutInput').value = ''; fetchWorkouts();
    };

    document.getElementById('weightForm').onsubmit = async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        const weight = document.getElementById('weightInput').value;
        
        setButtonLoading(btn, true);
        await secureFetch('/api/auth/weight', { method: 'POST', body: JSON.stringify({ weight }) });
        setButtonLoading(btn, false);
        
        fetchWeightHistory(); fetchSummary();
    };

    document.getElementById('chatForm').onsubmit = async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        const input = document.getElementById('chatInput');
        const text = input.value;
        if (!text) return;
        
        const msgDiv = document.createElement('div');
        msgDiv.className = 'text-xs text-slate-300 bg-slate-800 p-3 rounded-xl';
        msgDiv.innerText = text;
        document.getElementById('chatMessages').appendChild(msgDiv);
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

    function toggleChat() { document.getElementById('aiChatWindow').classList.toggle('hidden'); }
    
    async function fetchWeeklyHistory() {
        const res = await secureFetch('/api/nutrition/weekly-history');
        if (!res) return;
        const data = await res.json();
        if (Array.isArray(data)) initHistoryChart(data);
    }

    let historyChart;
    function initHistoryChart(data) {
        const ctx = document.getElementById('historyChart').getContext('2d');
        if (historyChart) historyChart.destroy();
        historyChart = new Chart(ctx, {
            type: 'bar',
            data: { labels: data.map(d => d.date), datasets: [{ data: data.map(d => d.calories), backgroundColor: '#10b981', borderRadius: 5 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });
    }

    async function deleteMealGroup(promptText) {
        if (confirm('Silinsin mi?')) {
            await secureFetch('/api/nutrition/log/group', { method: 'DELETE', body: JSON.stringify({ prompt_text: promptText, date: currentDate }) });
            fetchSummary();
        }
    }

    async function deleteWorkout(id) {
        if (confirm('Silinsin mi?')) {
            await secureFetch(`/api/fitness/workout/${id}`, { method: 'DELETE' });
            fetchWorkouts();
        }
    }

    function changeDate(days) {
        const d = new Date(currentDate);
        d.setDate(d.getDate() + days);
        const newDate = d.toISOString().split('T')[0];
        document.getElementById('datePicker').value = newDate;
        fetchSummary(newDate);
    }

    window.onload = () => {
        fetchSummary();
        fetchWeeklyHistory();
        document.getElementById('datePicker').value = currentDate;
    };
