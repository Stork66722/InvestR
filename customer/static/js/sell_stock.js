// Sell Stock Page 
console.log('sell_stock.js loaded!');

const select = document.getElementById('stock');
const shares = document.getElementById('shares');
const holdingEl = document.getElementById('holding');
const proceedsEl = document.getElementById('proceeds');
const priceDisplayEl = document.getElementById('priceDisplaySell');
const cashAvailEl = document.getElementById('cashAvail');
const reviewSellBtn = document.getElementById('reviewSellBtn');
const warnShares = document.getElementById('warnShares');
const statusMessage = document.getElementById('statusMessage');
const tradeForm = document.getElementById('tradeForm');
const tradeTickerInput = document.getElementById('tradeTickerSell');
const tradeQuantityInput = document.getElementById('tradeQuantitySell');

// Modal elements
const modal = document.getElementById('sellConfirmModal');
const confirmBtn = document.getElementById('confirmSellBtn');
const cancelBtn = document.getElementById('cancelSellBtn');
const overlay = document.getElementById('sellModalOverlay');
const summary = document.getElementById('sellOrderSummary');

const initialCashString = cashAvailEl.textContent.replace('$', '').replace(/,/g, '');
let currentCash = parseFloat(initialCashString) || 0;

const fmt = n => '$' + (Number(n).toFixed(2)).replace(/\B(?=(\d{3})+(?!\d))/g, ",");

function getSelectedData() {
    const selectedOption = select.options[select.selectedIndex];
    return {
        price: parseFloat(selectedOption.value || 0),
        ticker: selectedOption.dataset?.ticker || null,
        name: selectedOption.dataset?.name || selectedOption.text || '',
        held: parseInt(selectedOption.dataset?.held || 0, 10),
        qty: parseInt(shares.value || 0, 10)
    };
}

function updateCalculations() {
    const { price, held, qty } = getSelectedData();
    const total = price * qty;

    holdingEl.textContent = held;
    priceDisplayEl.textContent = fmt(price);
    proceedsEl.textContent = fmt(total);
    cashAvailEl.textContent = fmt(currentCash);

    const validSelection = price > 0;
    const validQuantity = qty > 0;
    const valid = validSelection && validQuantity;
    const enoughShares = qty <= held;

    warnShares.style.display = valid && !enoughShares ? 'block' : 'none';
    reviewSellBtn.disabled = !(valid && enoughShares);

    shares.setAttribute('max', held);
}

select.addEventListener('change', () => {
    shares.value = ''; 
    updateCalculations();
});
shares.addEventListener('input', updateCalculations);

// ===========================================
// ORDER CONFIRMATION MODAL
// ===========================================

// Show confirmation modal when review button clicked
if (reviewSellBtn) {
    reviewSellBtn.addEventListener('click', (e) => {
        e.preventDefault();
        console.log('Review sell button clicked');
        
        const { price, held, qty, ticker, name } = getSelectedData();
        const total = price * qty;

        // Validate
        if (qty > held || !ticker || qty <= 0) {
            console.log('Validation failed');
            return;
        }

        // Build order summary
        summary.innerHTML = `
            <p><strong>Stock:</strong> <span>${ticker}</span></p>
            <p><strong>Company:</strong> <span>${name}</span></p>
            <p><strong>Quantity:</strong> <span>${qty} shares</span></p>
            <p><strong>Price per Share:</strong> <span>${fmt(price)}</span></p>
            <p class="order-total"><strong>Total Proceeds:</strong> <span>${fmt(total)}</span></p>
        `;

        // Show modal
        modal.style.display = 'block';
    });
}

// Confirm button - execute the sale
if (confirmBtn) {
    confirmBtn.addEventListener('click', function() {
        const { price, held, qty, ticker } = getSelectedData();
        const total = price * qty;

        // Hide modal
        modal.style.display = 'none';

        // Validate
        if (qty > held || !ticker || qty <= 0) {
            return;
        }

        // Set form values
        tradeTickerInput.value = ticker;
        tradeQuantityInput.value = qty;
        
        // Disable buttons and show processing
        confirmBtn.disabled = true;
        reviewSellBtn.disabled = true;
        reviewSellBtn.textContent = 'Processing...';
        statusMessage.textContent = 'Executing order...';
        statusMessage.style.display = 'block';

        // Submit trade
        fetch(tradeForm.action, {
            method: 'POST',
            body: new FormData(tradeForm),
        })
        .then(response => response.json().then(data => ({ status: response.status, body: data })))
        .then(({ status, body }) => {
            if (status === 200) {
                currentCash = parseFloat(body.new_cash);
                statusMessage.className = 'warn';
                statusMessage.style.color = 'darkgreen';
                statusMessage.style.background = '#dcfce7';
                statusMessage.style.borderColor = '#bbf7d0';
                statusMessage.textContent = body.message + `. New Cash: ${fmt(currentCash)}`;
            } else {
                statusMessage.className = 'warn';
                statusMessage.style.color = '#b91c1c';
                statusMessage.style.background = '#fee2e2';
                statusMessage.style.borderColor = '#fecaca';
                statusMessage.textContent = body.error || `Trade failed with status ${status}.`;
            }
        })
        .catch(error => {
            statusMessage.className = 'warn';
            statusMessage.style.color = '#b91c1c';
            statusMessage.style.background = '#fee2e2';
            statusMessage.style.borderColor = '#fecaca';
            statusMessage.textContent = 'A network error occurred. Please try again.';
            console.error('Error:', error);
        })
        .finally(() => {
            confirmBtn.disabled = false;
            reviewSellBtn.disabled = false;
            reviewSellBtn.textContent = 'Review Order';
            shares.value = '';
            updateCalculations();
        });
    });
}

// Cancel button
if (cancelBtn) {
    cancelBtn.addEventListener('click', function() {
        modal.style.display = 'none';
        statusMessage.className = 'warn';
        statusMessage.style.color = '#0369a1';
        statusMessage.style.background = '#e0f2fe';
        statusMessage.style.borderColor = '#bae6fd';
        statusMessage.textContent = 'Order cancelled';
        statusMessage.style.display = 'block';
        
        setTimeout(function() {
            statusMessage.style.display = 'none';
        }, 3000);
    });
}

// Click outside modal to close
if (overlay) {
    overlay.addEventListener('click', function() {
        modal.style.display = 'none';
    });
}

// Initial calculation
updateCalculations();