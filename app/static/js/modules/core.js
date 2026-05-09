const getToken = () => localStorage.getItem('token');

async function secureFetch(url, options = {}) {
    let token = getToken();
    if (!token) { window.location.href = '/auth'; return null; }
    options.headers = { ...options.headers, 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
    let res = await fetch(url, options);
    if (res.status === 401) {
        const refreshRes = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        });
        if (refreshRes.ok) {
            const data = await refreshRes.json();
            localStorage.setItem('token', data.auth_token);
            options.headers['Authorization'] = `Bearer ${data.auth_token}`;
            res = await fetch(url, options);
        } else {
            localStorage.removeItem('token');
            window.location.href = '/auth';
            return null;
        }
    }
    return res;
}

function setButtonLoading(btn, isLoading) {
    if (!btn) return;
    if (isLoading) {
        btn.dataset.originalContent = btn.innerHTML;
        btn.disabled = true;
        btn.classList.add('opacity-70', 'cursor-not-allowed');
        btn.innerHTML = `
            <div class="flex items-center justify-center gap-2">
                <i class="fa-solid fa-circle-notch animate-spin"></i>
                <span class="text-[10px] font-black uppercase tracking-widest">İşleniyor...</span>
            </div>
        `;
    } else {
        if (btn.dataset.originalContent) {
            btn.innerHTML = btn.dataset.originalContent;
        }
        btn.disabled = false;
        btn.classList.remove('opacity-70', 'cursor-not-allowed');
    }
}
