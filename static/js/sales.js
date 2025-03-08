const formularioVenta = document.getElementById('product-form');
const listaCarrito = document.getElementById('sale-table');
const bodyCarrito = listaCarrito.querySelector('tbody');
const totalElement = document.getElementById('total');
const dalInput = formularioVenta.querySelector('select[name="product"]');


const trashIconSVG = `
    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
        <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
    </svg>
`;

let total = 0; //sacar y debe venir del back

formularioVenta.addEventListener('submit', function(event) {
    event.preventDefault();
    let csrfToken = getCookie('csrftoken');

    let formData = new FormData(formularioVenta);
    formData.append('csrfmiddlewaretoken', csrfToken);

    fetch(formularioVenta.action, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Error en la solicitud');
        }
    })
    .then(data => {
        no_products = document.getElementById('no-products');
        if (no_products && data.product.name.length > 0) {
            bodyCarrito.removeChild(no_products);
        };

        let newRow = bodyCarrito.insertRow(-1);
        newRow.innerHTML = `
            <td>${data.quantity}</td>
            <td>${data.product.name}</td>
            <td>${data.sale_price}</td>
            <td>${data.total_price}</td>
            <td><button class="eliminar-sale-detail" data-sale-detail-id="${data.id}" type="button" onclick="deleteSaleDetail.call(this)">${trashIconSVG}</button></td>
        `;
    })
    .catch(error => {
        console.error(error);
    });
    formularioVenta.reset();
    if (dalInput) {
        $(dalInput).val(null).trigger('change');
    }
});

//data-sale-detail-id
function deleteSaleDetail() {
    let saleDetailId = this.getAttribute('data-sale-detail-id');
    let csrfToken = getCookie('csrftoken');
    fetch(`/ventas/delete-detail/${saleDetailId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrfToken,
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Error en la solicitud');
        }
    })
    .then(data => {
        let row = this.parentNode.parentNode;
        bodyCarrito.removeChild(row);
    })
    .catch(error => {
        console.error(error);
    });
}