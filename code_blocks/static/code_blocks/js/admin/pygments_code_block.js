class PygmentsCodeBlockDefinition extends window.wagtailStreamField.blocks
    .StructBlockDefinition {
    render(placeholder, prefix, initialState, initialError) {
        const block = super.render(
            placeholder,
            prefix,
            initialState,
            initialError,
        );

        const showCornerTextField = document.getElementById(prefix + '-show_corner_text');
        const cornerTextField = document.getElementById(prefix + '-corner_text');

        const updateStateInput = () => {

            if (showCornerTextField.checked === true) {

                //cornerTextField.removeAttribute('disabled');
                const saved_value = cornerTextField.getAttribute('data-saved-value');

                if (saved_value) {
                    cornerTextField.value = saved_value;
                    cornerTextField.removeAttribute('data-saved-value');
                }

                cornerTextField.closest('div[data-contentpath="corner_text"]').style.display = null;
            } else {

                //cornerTextField.setAttribute('disabled', 'true');
                cornerTextField.closest('div[data-contentpath="corner_text"]').style.display = 'none';

                if (cornerTextField.value) {
                    cornerTextField.setAttribute('data-saved-value', cornerTextField.value);
                    cornerTextField.value = '';
                }
            }
        };

        if (showCornerTextField && cornerTextField) {
            updateStateInput();

            showCornerTextField.addEventListener(
                'change',
                updateStateInput,
                {passive: true},
            );
        }

        return block;
    }
}

window.telepath.register('code_blocks.blocks.pygments.PygmentsCodeBlock', PygmentsCodeBlockDefinition);
