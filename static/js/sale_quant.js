class QuantityInput extends HTMLInputElement {
    constructor(initialValue, saledetailId) {
        super();
        this.type = 'number';
        this.originalValue = initialValue;
        this.value = initialValue;
        this.saledetailId = saledetailId;
        this.escapePressed = false;
    }

    connectedCallback() {
        this.addEventListener('blur', this.handleBlur);
        this.addEventListener('keydown', this.handleKeyDown);
    }

    disconnectedCallback() {
        this.removeEventListener('blur', this.handleBlur);
        this.removeEventListener('keydown', this.handleKeyDown);
    }

    handleBlur = () => {
        if (this.escapePressed) {
            this.escapePressed = false;
            return;
        }
        else {
            simularEnvioBackend(this.saledetailId, this.value)
                .then(respuestaBackend => {
                    console.log("Respuesta del backend:", respuestaBackend);
                    // cambiar precios acorde a respuesta de Backend
                })
                .catch(error => {
                    console.error("Error al actualizar la cantidad:", error);
                    this.parentElement.textContent = this.originalValue;
                    alert("Error al actualizar la cantidad del producto.");
                })
        }
    }

    handleKeyDown = (event) => {
        switch (event.key) {
            case 'Enter':
                this.onEnterPress();
                break;
            case 'Escape':
                this.onEscapePress();
                break;
        }
    }

    onEnterPress = () => {
        this.parentElement.textContent = this.value;
        this.blur();
    }

    onEscapePress = () => {
        this.parentElement.textContent = this.originalValue;
        this.blur();
    }

}

customElements.define('quantity-input', QuantityInput, { extends: 'input' });




function simularEnvioBackend(saledetailId, nuevaCantidad) {
    return new Promise((resolve, reject) => {
        // Aquí iría tu llamada real al backend (fetch, axios, etc.)
        // Simulación de respuesta exitosa después de 1 segundo
        setTimeout(() => {
            const exito = true; // Simula éxito o fallo del backend
            if (exito) {
                resolve({ saledetailId: saledetailId, nuevaCantidad: nuevaCantidad });
            } else {
                reject("Error en el backend");
            }
        }, 1000); // Simula un segundo de espera para la respuesta del backend
    });
}
