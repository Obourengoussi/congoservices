// ============================================
// CongoServices - JavaScript Principal
// ============================================

document.addEventListener('DOMContentLoaded', () => {

    console.log('✅ CongoServices chargé');

    // ============================================
    // FORMATAGE NUMÉRO
    // ============================================

    window.formatPhone = function(phone) {

        if (!phone) return '';

        let cleaned = phone.replace(/\D/g, '');

        if (cleaned.startsWith('242')) {
            cleaned = '+' + cleaned;
        }

        else if (cleaned.startsWith('0')) {
            cleaned = '+242' + cleaned.substring(1);
        }

        return cleaned;
    };

    // ============================================
    // VIDEOS HOVER PLAY
    // ============================================

    const hoverVideos = document.querySelectorAll(
        'video[data-hover-play]'
    );

    hoverVideos.forEach(video => {

        video.addEventListener('mouseenter', () => {

            video.play().catch(() => {});

        });

        video.addEventListener('mouseleave', () => {

            video.pause();

            video.currentTime = 0;

        });

    });

    // ============================================
    // VALIDATION FORMULAIRES
    // ============================================

    const forms = document.querySelectorAll('.needs-validation');

    forms.forEach(form => {

        form.addEventListener('submit', event => {

            if (!form.checkValidity()) {

                event.preventDefault();

                event.stopPropagation();

            }

            form.classList.add('was-validated');

        });

    });

    // ============================================
    // TOAST NOTIFICATIONS
    // ============================================

    window.showToast = function(
        message,
        type = 'primary'
    ) {

        const toast = document.createElement('div');

        toast.className =
            `toast-notification alert alert-${type}
            shadow position-fixed`;

        toast.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="flex-grow-1">
                    ${message}
                </div>

                <button
                    type="button"
                    class="btn-close ms-3"
                    aria-label="Close"
                ></button>
            </div>
        `;

        toast.style.zIndex = '9999';

        toast.style.bottom = '20px';

        toast.style.right = '20px';

        toast.style.minWidth = '260px';

        document.body.appendChild(toast);

        // Fermer manuellement
        toast.querySelector('.btn-close')
            .addEventListener('click', () => {
                toast.remove();
            });

        // Auto remove
        setTimeout(() => {

            toast.classList.add('fade');

            setTimeout(() => {
                toast.remove();
            }, 300);

        }, 3000);

    };

    // ============================================
    // COPIER TEXTE
    // ============================================

    window.copyToClipboard = async function(text) {

        try {

            await navigator.clipboard.writeText(text);

            showToast(
                'Lien copié avec succès !',
                'success'
            );

        }

        catch (error) {

            const textarea =
                document.createElement('textarea');

            textarea.value = text;

            document.body.appendChild(textarea);

            textarea.select();

            document.execCommand('copy');

            document.body.removeChild(textarea);

            showToast(
                'Lien copié !',
                'success'
            );

        }

    };

    // ============================================
    // RECHERCHE LIVE
    // ============================================

    const searchInputs =
        document.querySelectorAll(
            'input[type="search"]'
        );

    searchInputs.forEach(input => {

        let timeout;

        input.addEventListener('input', () => {

            clearTimeout(timeout);

            timeout = setTimeout(() => {

                // Auto-search option
                // input.closest('form')?.submit();

            }, 500);

        });

    });

    // ============================================
    // ESCAPE MODAL
    // ============================================

    document.addEventListener('keydown', event => {

        if (event.key === 'Escape') {

            document
                .querySelectorAll('.modal.show')
                .forEach(modal => {

                    const instance =
                        bootstrap.Modal.getInstance(modal);

                    if (instance) {
                        instance.hide();
                    }

                });

        }

    });

    // ============================================
    // TRACKING WHATSAPP
    // ============================================

    document
        .querySelectorAll('a[href*="wa.me"]')
        .forEach(link => {

            link.addEventListener('click', () => {

                console.log(
                    '📱 WhatsApp cliqué'
                );

            });

        });

    // ============================================
    // LAZY LOAD IMAGES
    // ============================================

    if ('IntersectionObserver' in window) {

        const observer =
            new IntersectionObserver(
                entries => {

                    entries.forEach(entry => {

                        if (entry.isIntersecting) {

                            const img = entry.target;

                            if (img.dataset.src) {

                                img.src =
                                    img.dataset.src;

                                img.removeAttribute(
                                    'data-src'
                                );

                            }

                            observer.unobserve(img);

                        }

                    });

                }
            );

        document
            .querySelectorAll('img[data-src]')
            .forEach(img => {
                observer.observe(img);
            });

    }

});

// ============================================
// FONCTIONS GLOBALES
// ============================================

// Confirmation
function confirmAction(message = null) {

    return confirm(
        message ||
        'Êtes-vous sûr de vouloir continuer ?'
    );

}

// FORMAT DATE
function formatDate(dateString) {

    const date = new Date(dateString);

    return date.toLocaleDateString(
        'fr-FR',
        {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        }
    );

}

// NOMBRE ABRÉGÉ
function abbreviateNumber(number) {

    const num = Number(number);

    if (num >= 1000000) {

        return (
            (num / 1000000)
            .toFixed(1)
            .replace('.0', '') + 'M'
        );

    }

    if (num >= 1000) {

        return (
            (num / 1000)
            .toFixed(1)
            .replace('.0', '') + 'K'
        );

    }

    return num.toString();

}