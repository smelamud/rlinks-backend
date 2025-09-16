document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('bookmark-form');
  const input = document.getElementById('url-input');
  const result = document.getElementById('result');

  if (!form || !input || !result) {
    return;
  }

  async function onSubmit(e) {
    e.preventDefault();
    const url = input.value.trim();
    if (!url) return;

    result.textContent = 'Submitting...';
    try {
      const resp = await fetch('/api/bookmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });

      if (!resp.ok) {
        throw new Error(`Request failed: ${resp.status}`);
      }

      const data = await resp.json();
      result.innerHTML = '';
      const a = document.createElement('a');
      a.href = data.url;
      a.textContent = data.url;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      result.appendChild(a);

      input.value = '';
      input.focus();
    } catch (err) {
      result.textContent = `Error: ${err && err.message ? err.message : 'Unknown error'}`;
    }
  }

  form.addEventListener('submit', onSubmit);
});
