async function claim(site) {
  const input = document.getElementById("bonusCode");
  const tooltip = document.getElementById("clipboardMsg");
  let code = input.value.trim();

  // Fallback to clipboard if input is empty
  if (!code) {
    try {
      code = await navigator.clipboard.readText();
      input.value = code; // Fill input for visibility
      localStorage.setItem('lastCode', code);
    } catch (err) {
      tooltip.textContent = "❗ Please allow clipboard access or paste your code manually.";
      tooltip.style.display = "block";
      return;
    }
  }

  // If no code is provided (from input or clipboard), show alert
  if (!code) {
    alert('Please enter a bonus code');
    return;
  }

  // Construct URL and open in new tab
  let url = '';
  if (site === 'chanced') {
    url = `https://www.chanced.com/?rbc=${encodeURIComponent(code)}`;
  } else if (site === 'punt') {
    url = `https://www.punt.com/?rbc=${encodeURIComponent(code)}`;
  }
  window.open(url, '_blank');
}

// Auto-fill from localStorage
window.addEventListener("DOMContentLoaded", () => {
  const saved = localStorage.getItem("lastCode");
  if (saved && !document.getElementById("bonusCode").value) {
    document.getElementById("bonusCode").value = saved;
  }
});
