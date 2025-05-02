import { InventoryFetcher } from "./requests/fetchers/inventory_fetchers.js";
const QuantityDialog = (() => {
    let currentDialog = null;
    let currentOperation = null;

    const createDialog = (button, operation) => {
        const dialog = document.createElement('div');
        dialog.className = 'quantity-dialog';
        dialog.dataset.operation = operation;
        dialog.dataset.arrow = 'top';

        // Crear elementos
        const arrow = document.createElement('div');
        arrow.className = 'dialog-arrow';

        const input = document.createElement('input');
        input.type = 'number';
        input.min = '0';
        input.className = 'quantity-input';
        input.value = 0;
        input.placeholder = `Cantidad a ${operation === 'plus' ? 'sumar' : 'restar'}`;
        input.autofocus = true;

        const confirmBtn = document.createElement('button');
        confirmBtn.className = 'btn-confirm';

        // SVG Check
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('viewBox', '0 0 24 24');
        svg.setAttribute('width', '20');
        svg.setAttribute('height', '20');
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', 'M9 16.17 4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z');
        svg.appendChild(path);
        confirmBtn.appendChild(svg);

        // Ensamblar diálogo
        dialog.append(arrow, input, confirmBtn);
        document.body.appendChild(dialog);

        // Calcular posicionamiento
        const buttonRect = button.getBoundingClientRect();
        const dialogRect = dialog.getBoundingClientRect();
        const viewportPadding = 15;

        // Posición vertical
        let top = buttonRect.top - dialogRect.height - 10;
        let arrowDirection = 'top';

        if (top < viewportPadding) {
            top = buttonRect.bottom + 10;
            arrowDirection = 'bottom';
        }

        // Posición horizontal
        let left = buttonRect.left + (buttonRect.width / 2) - (dialogRect.width / 2);
        left = Math.max(viewportPadding, Math.min(left, window.innerWidth - dialogRect.width - viewportPadding));

        // Ajustar flecha
        const buttonCenterX = buttonRect.left + (buttonRect.width / 2);
        const dialogCenterX = left + (dialogRect.width / 2);
        const arrowOffset = buttonCenterX - dialogCenterX;

        arrow.style.left = `calc(50% + ${arrowOffset}px)`;
        dialog.dataset.arrow = arrowDirection;

        // Aplicar estilos
        dialog.style.position = 'fixed';
        dialog.style.top = `${top + window.scrollY}px`;
        dialog.style.left = `${left}px`;
        dialog.style.zIndex = '10000';
        dialog.style.opacity = '0';

        setTimeout(() => {
            dialog.style.opacity = '1';
            dialog.style.transition = 'opacity 0.2s';
        }, 10);

        return dialog;
    };

    const destroyDialog = () => {
        if (currentDialog) {
            currentDialog.remove();
            currentDialog = null;
            currentOperation = null;
        }
    };

    const handleClickOutside = (event) => {
        if (currentDialog && !currentDialog.contains(event.target)) {
            destroyDialog();
            document.removeEventListener('click', handleClickOutside);
        }
    };

    const init = (event) => {
        const btn = event.target.closest('.btn-quantity');
        if (!btn) return;

        event.stopPropagation();
        destroyDialog();

        currentOperation = btn.classList.contains('addition') ? 'addition' : 'subtraction';

        currentDialog = createDialog(btn, currentOperation);

        currentDialog.querySelector('.btn-confirm').addEventListener('click', () => {
            const delta = parseInt(currentDialog.querySelector('input').value) || 0;
            if (delta > 0) {
                InventoryFetcher.updateInventoryQuantity(btn.parentElement.getAttribute('data-inventory-id'), delta, currentOperation)
                    .then(() => {
                        window.location.reload();
                    });
            }
            destroyDialog();
        });

        document.addEventListener('click', handleClickOutside);
    };

    return { init };
})();

document.addEventListener('click', (e) => QuantityDialog.init(e));