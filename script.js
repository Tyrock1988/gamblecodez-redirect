
function claim(site) {
    const code = document.getElementById('bonusCode').value.trim();
    if (!code) {
        alert('Please enter a bonus code');
        return;
    }
    let url = '';
    if (site === 'chanced') {
        url = `https://www.chanced.com/?rbc=${code}`;
    } else if (site === 'punt') {
        url = `https://www.punt.com/?rbc=${code}`;
    }
    window.open(url, '_blank');
}
