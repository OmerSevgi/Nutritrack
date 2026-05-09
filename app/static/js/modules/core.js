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
    if (isLoading) {
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin mr-2"></i>';
        btn.disabled = true;
    } else {
        btn.innerHTML = btn.dataset.originalText;
        btn.disabled = false;
    }
}
