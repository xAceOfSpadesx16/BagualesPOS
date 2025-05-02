class BaseButton extends HTMLButtonElement {
    constructor(idName, onClick, textContent, innerHTML, classList, newAttributes) {
        super();
        this.id = idName;
        this.onClick = onClick;
        this.classList.add(...classList);
        if (innerHTML && innerHTML.trim() !== '') {
            this.innerHTML = innerHTML;
        } else {
            this.textContent = textContent || '';
        }
        if (newAttributes) {
            Object.entries(newAttributes).forEach(([key, value]) => {
                this.setAttribute(key, value);
            });
        }
    }
    connectedCallback() {
        this.addEventListener('click', this.onClick);
    }
    disconnectedCallback() {
        this.removeEventListener('click', this.onClick);
    }
}

class XIconButton extends BaseButton {
    constructor(idName, onClick) {
        const svgCode = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path fill="none" d="M0 0h24v24H0z" />
            <path fill="currentColor" d="M12 10.586l4.95-4.95 1.414 1.414-4.95 4.95 4.95 4.95-1.414 1.414-4.95-4.95-4.95 4.95-1.414-1.414 4.95-4.95-4.95-4.95L7.05 5.636z" />
        </svg>
        `;
        let classList = ['icon-button'];
        super(idName, onClick, '', svgCode, classList);
    }
}


customElements.define('base-button', BaseButton, { extends: 'button' });
customElements.define('close-button', XIconButton, { extends: 'button' });

class Modal extends HTMLElement {
    static isOpen = false;
    static instance = null;

    /**
     * @param {string} [title=''] - Título del modal.
     * @param {string} [content=''] - Contenido del modal en formato HTML.
     * @param {Function} [onSubmit=() => {}] - Callback al confirmar el modal.
     * @param {Function} [onClose=() => {}] - Callback al cerrar el modal.
     * @param {string} [modalIdSelector='modal'] - Selector del modal en el DOM.
     * @param {Array} [titleClassSelector='modal-container-title'] - Selector del título del modal.
     * @param {Array} [contentclassSelector='modal-container-body'] - Selector del contenido del modal.
     * @param {string} [submitIdSelector='confirm_modal'] - Selector del botón de confirmación.
     * @param {string} [closeIdSelector='close_modal'] - Selector del botón de cierre.
     * @param {string} [modalXCloseIdSelector='modal_x_close'] - Selector del botón "X" para cerrar.
     */

    constructor({
        title = '',
        content = '',
        onSubmit = () => { },
        onClose = () => { },
        modalIdSelector = 'modal',

        titleClassSelector = ['modal-container-title'],
        contentclassSelector = ['modal-container-body', 'rtf'],

        submitIdSelector = 'confirm_modal',
        closeIdSelector = 'close_modal',
        modalXCloseIdSelector = 'modal_x_close',

        requireCloseConfirmation = false,

        confirmButtonDataAttr = {},

    } = {}) {
        super();
        this.onSubmit = onSubmit;
        this.onClose = onClose;

        this.id = modalIdSelector;
        this._title = title;
        this.content = content;

        this.titleSelector = titleClassSelector;
        this.contentSelector = contentclassSelector;

        this.submitSelector = submitIdSelector;
        this.closeSelector = closeIdSelector;
        this.modalXCloseSelector = modalXCloseIdSelector;

        this.requireCloseConfirmation = requireCloseConfirmation;

        this.confirmButtonDataAttr = confirmButtonDataAttr;

        this.#setUpModalContent();
    }

    #setUpModalContent() {
        const article = document.createElement('article');
        article.classList.add('modal-container');

        const header = document.createElement('header');
        header.classList.add('modal-container-header');

        const titleElem = document.createElement('h1');
        titleElem.classList.add(...this.titleSelector);
        titleElem.textContent = this._title;

        const closeBtn = new XIconButton(this.modalXCloseSelector, this.#closeModal.bind(this));

        header.appendChild(titleElem);
        header.appendChild(closeBtn);

        const section = document.createElement('section');
        section.classList.add(...this.contentSelector);
        section.innerHTML = this.content;

        const footer = document.createElement('footer');
        footer.classList.add('modal-container-footer');

        const cancelBtn = new BaseButton(this.closeSelector, this.#closeModal.bind(this), 'Cancelar', '', ['button', 'is-ghost']);
        const confirmBtn = new BaseButton(this.submitSelector, this.confirmAction.bind(this), 'Confirmar', '', ['button', 'is-primary'], this.confirmButtonDataAttr);

        footer.appendChild(cancelBtn);
        footer.appendChild(confirmBtn);

        article.appendChild(header);
        article.appendChild(section);
        article.appendChild(footer);

        this.appendChild(article);
    }

    openModal() {
        if (Modal.isOpen) return;
        Modal.instance = this;
        Modal.isOpen = true;
        document.querySelector('.page-wrapper').appendChild(this);
        setTimeout(() => this.classList.add('show'), 10);
    }


    #closeModal() {
        if (!Modal.isOpen) return;

        this.classList.remove('show');
        this.addEventListener('transitionend', () => {
            this.remove();
            Modal.isOpen = false;
            Modal.instance = null;
        }, { once: true });

    }

    async confirmAction(e) {
        const result = await this.onSubmit(e);
        if (this.requireCloseConfirmation && !result) return;
        this.#closeModal(result);
    }

    backdropListener(event) {
        if (event.target === this) {
            this.#closeModal(true);
        }
    }

    connectedCallback() {
        this.boundBackdropListener = this.backdropListener.bind(this);
        this.addEventListener('click', this.boundBackdropListener);
    }

    disconnectedCallback() {
        this.removeEventListener('click', this.boundBackdropListener);
    }

    #updateContent(newContent) {
        this.content = newContent;
        const contentContainer = this.querySelector(this.contentSelector.map(cls => `.${cls}`).join(", "))
        contentContainer.innerHTML = newContent;
    }
    static updateContent(newContent) {
        Modal.instance.#updateContent(newContent);
    }

}

customElements.define('custom-modal', Modal);

export { Modal };