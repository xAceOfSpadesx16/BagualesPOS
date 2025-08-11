import { Modal } from '/static/js/modal.js';
import { ClientCCFetcher } from '/static/js/requests/fetchers/clients_cc_fetchers.js';

document.addEventListener('DOMContentLoaded', () => {
    const newBtn = document.getElementById('new-cc-movement-btn');
    if (newBtn) {
        newBtn.addEventListener('click', openNewMovementModal);
    }

    // Agregar event listeners para botones de eliminar
    document.addEventListener('click', handleDeleteClick);
});

function handleDeleteClick(e) {
    if (e.target.closest('.delete-btn')) {
        e.preventDefault();
        const button = e.target.closest('.delete-btn');
        const movementId = button.dataset.movementId;

        if (confirm('¿Estás seguro de que quieres eliminar este movimiento?')) {
            deleteMovement(movementId, button);
        }
    }
}

async function deleteMovement(movementId, button) {
    try {
        const result = await ClientCCFetcher.deleteMovement(movementId);

        if (result.success) {
            // Eliminar la fila del DOM
            const row = button.closest('tr');
            row.remove();

            // Verificar si la tabla quedó vacía
            checkAndShowEmptyMessage();
        } else {
            alert('Error: ' + (result.error || 'No se pudo eliminar el movimiento.'));
        }

    } catch (error) {
        console.error('Error al eliminar el movimiento:', error);
        alert('Error al eliminar el movimiento');
    }
}

function checkAndShowEmptyMessage() {
    const tbody = document.querySelector('.table-container tbody');
    const dataRows = tbody.querySelectorAll('tr[data-movement-id]');
    const noMovementsRow = document.getElementById('no-movements');

    if (dataRows.length === 0) {
        // Si no hay filas de datos, mostrar mensaje de vacío
        if (!noMovementsRow) {
            const tr = document.createElement('tr');
            tr.id = 'no-movements';
            tr.innerHTML = '<td colspan="6">No hay movimientos registrados.</td>';
            tbody.appendChild(tr);
        }
    } else {
        // Si hay filas de datos, remover mensaje de vacío si existe
        if (noMovementsRow) {
            noMovementsRow.remove();
        }
    }
}

function openNewMovementModal() {
    const clientId = window.location.pathname.split('/')[2];
    const modal = new Modal({
        title: 'Nuevo movimiento de cuenta corriente',
        content: `
            <form id="cc-movement-form">
                <label>Monto:<br><input type="number" name="amount" required step="0.01"></label><br>
                <label>Tipo:<br>
                    <select name="movement_type" required>
                        <option value="CREDIT">Crédito</option>
                        <option value="DEBIT">Débito</option>
                        <option value="ADJUSTMENT">Ajuste</option>
                        <option value="REFUND">Reintegro</option>
                        <option value="REVERSAL">Reverso</option>
                    </select>
                </label><br>
                <label>Notas:<br><input type="text" name="notes"></label><br>
                <label>Referencia:<br><input type="text" name="reference"></label><br>
            </form>
        `,
        onSubmit: async () => {
            const form = document.getElementById('cc-movement-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            data.client_id = clientId;
            const result = await ClientCCFetcher.createMovement(data);
            if (result.success) {
                // Remover mensaje de vacío si existe
                const noMovementsRow = document.getElementById('no-movements');
                if (noMovementsRow) noMovementsRow.remove();
                window.location.reload();
            } else {
                alert('Error: ' + (result.error || 'No se pudo crear el movimiento.'));
            }
            return result.success;
        }
    });
    modal.openModal();
} 