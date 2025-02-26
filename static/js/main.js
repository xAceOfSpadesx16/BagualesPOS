const formularioVenta = document.getElementById('formulario-venta');
const listaCarrito = document.getElementById('lista-carrito');
const totalElement = document.getElementById('total');
let total = 0;

formularioVenta.addEventListener('submit', function(event) {
    event.preventDefault();
    const producto = document.getElementById('producto').value;
    const cantidad = parseInt(document.getElementById('cantidad').value);
    const precio = 10;
    const subtotal = precio * cantidad;

    const nuevoItem = document.createElement('li');
    nuevoItem.textContent = `${producto} x ${cantidad} - $${subtotal.toFixed(2)}`;
    listaCarrito.appendChild(nuevoItem);

    total += subtotal;
    totalElement.textContent = total.toFixed(2);

    formularioVenta.reset();
});

document.getElementById('finalizar-compra').addEventListener('click', function() {
    alert(`Compra finalizada. Total: $${total.toFixed(2)}`);
    listaCarrito.innerHTML = '';
    total = 0;
    totalElement.textContent = '0.00';
});
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');

tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const tabId = button.dataset.tab;

        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));

        button.classList.add('active');
        document.getElementById(tabId).classList.add('active');
    });
});