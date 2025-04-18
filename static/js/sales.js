import { setInputQuantity } from "./sale_quant.js";
import { SalesFetcher } from "./requests/fetchers.js";
import { Modal } from "./modal.js";


const trashIconSVG = `
    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
        <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
    </svg>
`;

const buildRow = (row, data) => {
    const cellsConfig = [
        {
            value: data.quantity,
            class: 'editable-cell quantity-cell',
            attributes: {
                'data-saledetail-id': data.id,
                'ondblclick': 'setInputQuantity(this)'
            }
        },
        {
            value: data.product.name
        },
        {
            value: `$${data.sale_price}`
        },
        {
            value: `$${data.total_price}`
        },
        {
            class: 'action-cell',
            actions: [
                {
                    class: 'delete-btn icon-btn',
                    attributes: {
                        'data-sale-detail-id': data.id,
                        'title': 'Eliminar',
                    },
                    content: trashIconSVG
                }
            ]
        }
    ];

    cellsConfig.forEach(config => {
        const cell = document.createElement('td');

        if (config.class) cell.classList.add(...config.class.split(' '));
        if (config.attributes) setAttributes(cell, config.attributes);

        if (config.actions) {
            config.actions.forEach(action => createActionButton(cell, action));
        } else {
            cell.textContent = config.value || '';
        }

        row.appendChild(cell);
    });
};

function createActionButton(cell, { class: btnClass, attributes, content }) {
    const button = document.createElement('button');

    if (btnClass) button.classList.add(...btnClass.split(' '));

    if (attributes) setAttributes(button, attributes);

    button.innerHTML = content || '';

    cell.appendChild(button);
}

function setAttributes(element, attributes) {
    Object.entries(attributes).forEach(([key, value]) => {
        element.setAttribute(key, value);
    });
}

async function closeSale(e) {
    e.preventDefault();
    const form = e.target.closest('.modal-container').querySelector('form');
    if (!form) {
        console.error("No se encontró el formulario.");
        return Promise.resolve(false);
    }

    const saleId = form.getAttribute('data-sale-id');
    const clientData = form.querySelector('select[name="pay_method"]').value;

    return SalesFetcher.closeSale(saleId, clientData)
        .then(response => {
            if (response.ok) {
                const contentType = response.headers.get('Content-Type');
                if (contentType.toLowerCase().includes("application/json")) {
                    response.json().then(data => {
                        window.location.href = data.redirect_url;
                    })
                }
                if (contentType.toLowerCase().includes("text/html")) {
                    response.text().then(html => {
                        Modal.updateContent(html);
                        return false;
                    })
                }

            }
        })
        .catch(error => {
            console.error("Error en fetch:", error);
            return false;
        });
}

document.addEventListener('submit', function (event) {

    if (event.target.id === 'product-form') {
        event.preventDefault();
        const formularioVenta = event.target;
        const totalElement = document.getElementById('total-value');
        const listaCarrito = document.getElementById('sale-table');
        const bodyCarrito = listaCarrito.querySelector('tbody');
        const dalInput = formularioVenta.querySelector('select[name="product"]');
        const quantityInput = formularioVenta.querySelector('input[name="quantity"]');
        const noProducts = document.getElementById('no-products');

        SalesFetcher.createSaleDetail(dalInput.value, quantityInput.value).then(
            response => response.json()
        ).then(
            data => {

                if (noProducts && data.product.name.length > 0) {
                    bodyCarrito.removeChild(noProducts);
                };

                let newRow = bodyCarrito.insertRow(-1);
                buildRow(newRow, data);

                totalElement.textContent = `$${data.total_sale_amount}`;
            }).catch(error => {
                alert(error.message);
            });

        formularioVenta.reset();
        if (dalInput) {
            dalInput.value = null;
            dalInput.dispatchEvent(new Event('change'));
        }
    }
});

document.addEventListener('click', function (event) {

    if (event.target.closest('.delete-btn')) {
        const totalElement = document.getElementById('total-value')
        const button = event.target.closest('.delete-btn');
        const saleDetailId = button.getAttribute('data-sale-detail-id');
        const bodyCarrito = button.closest('tbody');
        SalesFetcher.deleteSaleDetail(saleDetailId).then(response => response.json()).then(data => {
            const row = button.closest('tr');
            row.remove();
            totalElement.textContent = `$${data.total_sale_amount}`;
            if (bodyCarrito.childElementCount === 0) {
                let noProducts = document.createElement('tr');
                noProducts.id = 'no-products';
                noProducts.innerHTML = `<td colspan="5">No hay productos en el carrito</td>`;
                bodyCarrito.appendChild(noProducts);
            }
            // agregar dialogo de exito
        }).catch(error => {
            console.error(error);
        });
    }

    if (event.target.closest('#close-sale-button')) {
        const button = event.target.closest('#close-sale-button');
        const saleId = button.getAttribute('data-sale-id');
        SalesFetcher.closeSaleDetails(saleId).then(response => response.text()).then(data => {
            const modal = new Modal({ title: 'Resumen de venta', content: data, onSubmit: closeSale, requireCloseConfirmation: true });
            modal.openModal();
        }).catch(error => {
            console.error(error);
        });
    }
});


document.getElementById('sale-table').querySelector('tbody').addEventListener('dblclick', function (event) {
    const target = event.target;
    if (target.classList.contains('quantity-cell')) {
        setInputQuantity(target);
    }
});


window.addEventListener('load', (event) => {
    const clientSelect = document.getElementById('client-autocomplete');

    if (clientSelect) {

        function ClientChange(event) {
            const selectedValue = this.value;
            const previousValue = this.dataset.previousValue;
            const saleId = this.getAttribute('data-sale-id');
            SalesFetcher.updateClient(saleId, selectedValue).then(
                () => { this.dataset.previousValue = selectedValue }
            ).catch(error => {
                console.error(error);
                this.value = previousValue;
                const changeEvent = new Event('change');
                this.dispatchEvent(changeEvent);
            });
        }
        clientSelect.dataset.previousValue = clientSelect.value;
        clientSelect.onchange = ClientChange;
    }
});


