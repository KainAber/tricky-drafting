function fetchCards() {
  const number = document.getElementById('numberDisplay').innerText;
  const setCode = document.getElementById('setInput').value.trim();

  // Build query string: e.g., "set:DFT t:instant mv<=3 c<=wu"
  let query = `set:${setCode} (t:instant or o:flash) mv<=${number} c<=`;

  if (document.getElementById('whiteToggle').checked) query += 'w';
  if (document.getElementById('blueToggle').checked)  query += 'u';
  if (document.getElementById('blackToggle').checked) query += 'b';
  if (document.getElementById('redToggle').checked)   query += 'r';
  if (document.getElementById('greenToggle').checked) query += 'g';

  console.log("Fetching with query:", query);

  fetch(`/fetch_cards?q=${encodeURIComponent(query)}&order=cmc&dir=asc`)
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById('cardContainer');
      container.innerHTML = ''; // Clear previous results

      if (data.error) {
        container.innerText = data.error;
        return;
      }
      if (data.message) {
        container.innerText = data.message;
      }
      data.cards.forEach(url => {
        const img = document.createElement('img');
        img.src = url;
        container.appendChild(img);
      });
    })
    .catch(error => console.error('Error fetching cards:', error));
}

// Attach event listeners for checkboxes and set code input.
document.querySelectorAll("input[type='checkbox']").forEach(el => {
  el.addEventListener('change', fetchCards);
});
document.getElementById('setInput').addEventListener('input', fetchCards);

// Number adjustment functionality.
let currentNumber = 1;
const numberDisplay = document.getElementById('numberDisplay');
document.getElementById('plusButton').addEventListener('click', () => {
  currentNumber++;
  numberDisplay.innerText = currentNumber;
  fetchCards();
});
document.getElementById('minusButton').addEventListener('click', () => {
  if (currentNumber > 0) currentNumber--;
  numberDisplay.innerText = currentNumber;
  fetchCards();
});

// Reset functionality.
document.getElementById('resetButton').addEventListener('click', () => {
  currentNumber = 1;
  numberDisplay.innerText = currentNumber;
  ['whiteToggle', 'blueToggle', 'blackToggle', 'redToggle', 'greenToggle']
    .forEach(id => document.getElementById(id).checked = false);
  fetchCards();
});

// Hotkey support.
document.addEventListener('keydown', (e) => {
  // Only trigger hotkeys when not typing in an input.
  if (document.activeElement.tagName === 'INPUT') return;

  const key = e.key;

  // Color toggle hotkeys: Use either WUBRG or ASDFG.
  switch(key.toUpperCase()) {
    case 'W': case 'A':
      document.getElementById('whiteToggle').click();
      return;
    case 'U': case 'S':
      document.getElementById('blueToggle').click();
      return;
    case 'B': case 'D':
      document.getElementById('blackToggle').click();
      return;
    case 'R': case 'F':
      document.getElementById('redToggle').click();
      return;
    case 'G':
      document.getElementById('greenToggle').click();
      return;
  }

  // Arrow keys for mana adjustment:
  // Left/Down arrow: decrease; Right/Up arrow: increase.
  if (key === 'ArrowRight' || key === 'ArrowUp') {
    currentNumber++;
    numberDisplay.innerText = currentNumber;
    fetchCards();
    return;
  }
  if (key === 'ArrowLeft' || key === 'ArrowDown') {
    if (currentNumber > 0) currentNumber--;
    numberDisplay.innerText = currentNumber;
    fetchCards();
    return;
  }

  // Numeric keys 1-9: directly set mana value.
  if (key >= '1' && key <= '9') {
    currentNumber = parseInt(key, 10);
    numberDisplay.innerText = currentNumber;
    fetchCards();
    return;
  }

  // Reset hotkey: Backspace.
  if (key === 'Backspace') {
    e.preventDefault();
    document.getElementById('resetButton').click();
    return;
  }
});

// Initial fetch when page loads.
fetchCards();
