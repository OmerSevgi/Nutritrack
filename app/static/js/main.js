// NutriTrack AI Main JavaScript
console.log('NutriTrack AI initialized');

// Global Auth Check
function getAuthToken() {
    return localStorage.getItem('token');
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/auth';
}
