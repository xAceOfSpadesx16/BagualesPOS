import { setInputQuantity } from "./sale_quant.js";
import { SalesFetcher } from "./requests/fetchers.js";


const trashIconSVG = `
    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
        <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
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
            value: trashIconSVG,
            class: 'eliminar-sale-detail',
            attributes: {
                'data-sale-detail-id': data.id,
                'type': 'button'
            },
            isHTML: true
        }
    ];

    cellsConfig.forEach(config => {
        const cell = document.createElement('td');

        // Establecer contenido
        if (config.isHTML) {
            cell.innerHTML = config.value;
        } else {
            cell.textContent = config.value;
        }

        // Añadir clases
        if (config.class) {
            cell.classList.add(...config.class.split(' '));
        }

        // Añadir atributos
        if (config.attributes) {
            Object.entries(config.attributes).forEach(([key, value]) => {
                cell.setAttribute(key, value);
            });
        }

        row.appendChild(cell);
    });
};

document.addEventListener('submit', function (event) {

    if (event.target.id === 'product-form') {
        event.preventDefault();
        const formularioVenta = event.target;
        const totalElement = document.getElementById('total-value');
        const listaCarrito = document.getElementById('sale-table');
        const bodyCarrito = listaCarrito.querySelector('tbody');
        const dalInput = formularioVenta.querySelector('select[name="product"]');
        const quantityInput = formularioVenta.querySelector('input[name="quantity"]');

        SalesFetcher.createSaleDetail(dalInput.value, quantityInput.value).then(data => {

            if (document.getElementById('no-products') && data.product.name.length > 0) {
                bodyCarrito.removeChild(no_products);
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

    if (event.target.closest('.eliminar-sale-detail')) {
        const totalElement = document.getElementById('total-value')
        const button = event.target.closest('.eliminar-sale-detail');
        const saleDetailId = button.getAttribute('data-sale-detail-id');
        SalesFetcher.deleteSaleDetail(saleDetailId).then(data => {
            const row = button.closest('tr');
            row.remove();
            totalElement.textContent = `$${data.total_sale_amount}`;
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