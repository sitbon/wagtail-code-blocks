const HIGHLIGHT_CLASS = document.currentScript.getAttribute('highlight-class');
const CSS_STATIC_BASE = document.currentScript.getAttribute('css-static-base');
const DYNAMIC_CSS = Boolean(document.currentScript.getAttribute('dynamic-css'));

function linkPygmentsStyleCSS(style) {
    const css_id = `pygments-style-${style}`;

    if (!document.getElementById(css_id)) {
        const head  = document.getElementsByTagName('head')[0];
        const link  = document.createElement('link');

        link.id   = css_id;
        link.rel  = 'stylesheet';
        link.type = 'text/css';
        link.href = `${CSS_STATIC_BASE}pygments/${style}.css`;
        link.media = 'all';

        head.appendChild(link);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const fit_blocks = document.querySelectorAll(`.${HIGHLIGHT_CLASS}.fit-content-width`);

    for (let block of fit_blocks) {
        block.parentElement.classList.add('fit-content-width');
    }

    const block_class_blocks = document.querySelectorAll(`.${HIGHLIGHT_CLASS}[data-block-class]`);

    for (let block of block_class_blocks) {
        block.parentElement.classList.add(block.dataset.blockClass);
    }

    if (DYNAMIC_CSS) {
        let pygments_styles = []

        const style_data_elements = document.querySelectorAll(
            `.${HIGHLIGHT_CLASS}[data-class-light],.${HIGHLIGHT_CLASS}[data-class-dark]`
        );

        for (let element of style_data_elements) {
            const style_light = element.dataset.classLight?.replace(
                `${HIGHLIGHT_CLASS}-`, ''
            );

            const style_dark = element.dataset.classDark?.replace(
                `${HIGHLIGHT_CLASS}-`, ''
            );

            if (style_light && !pygments_styles.includes(style_light)) {
                pygments_styles.push(style_light);
            }

            if (style_dark && !pygments_styles.includes(style_dark)) {
                pygments_styles.push(style_dark);
            }
        }

        for (let style of pygments_styles) {
            linkPygmentsStyleCSS(style);
        }
    }
});
