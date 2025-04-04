import { SalesFetcher } from "./requests/fetchers.js";

class QuantityInput extends HTMLInputElement {
    constructor(initialValue, saledetailId) {
        super();
        this.type = 'number';
        this.originalValue = initialValue;
        this.value = initialValue;
        this.saledetailId = saledetailId;
        this.escapePressed = false;

    };

    connectedCallback() {
        this.addEventListener('blur', this.handleBlur);
        this.addEventListener('keydown', this.handleKeyDown);
    };

    disconnectedCallback() {
        this.removeEventListener('blur', this.handleBlur);
        this.removeEventListener('keydown', this.handleKeyDown);
    };

    handleBlur = () => {
        const Cell = this.parentElement;
        const Row = Cell.parentElement;
        if (this.escapePressed) {
            Cell.textContent = this.originalValue;
            this.escapePressed = false;
        }
        else {
            Cell.textContent = this.value;
            this.UpdateQuantityFetch(this.saledetailId, this.value, Cell, Row);
        };
        this.remove();
    };

    handleKeyDown = (event) => {
        switch (event.key) {
            case 'Enter':
                this.onEnterPress();
                break;
            case 'Escape':
                this.onEscapePress();
                break;
        };
    };

    onEnterPress = () => {
        this.blur();
    };

    onEscapePress = () => {
        this.escapePressed = true;
        this.blur();
    };


    UpdateQuantityFetch = (saledetailId, newQuantity, Cell, Row) => {
        SalesFetcher.updateSaleDetailQuantity(saledetailId, newQuantity).then(data => {

            Cell.textContent = data.quantity;
            Row.querySelector('.price-cell').textContent = `$${data.sale_price}`;
            Row.querySelector('.subtotal-cell').textContent = `$${data.total_price}`;
            const totalSalePrice = document.getElementById('total-value');
            totalSalePrice.textContent = `$${data.total_sale_amount}`;

        }).catch(error => {
            Cell.textContent = this.originalValue;
        });
    };

};

customElements.define('quantity-input', QuantityInput, { extends: 'input' });

function setInputQuantity(cellElement) {
    if (!cellElement.querySelector('input')) {
        const originalValue = cellElement.textContent;
        cellElement.textContent = '';
        const saledetailId = cellElement.getAttribute('data-sale-detail-id');
        const inputElement = new QuantityInput(originalValue, saledetailId);
        cellElement.appendChild(inputElement);
        inputElement.focus();
    }
}

export { setInputQuantity };