function init() {
    const bookmarkBtn = document.getElementById('bookmark_btn');
    const modal = document.getElementById('application_modal');
    const btn = document.getElementById('application_btn');
    const form = document.getElementById('application_form');
    const cancelBtn = document.getElementById('cancelApplication');
    const closeApplicationModal = document.getElementById('closeApplicationModal');
    const resume = document.getElementById('resume');
    const removeResume = document.getElementById('remove-file');

    [cancelBtn, closeApplicationModal].forEach((e) => {
        e.onclick = () => {
            modal.style.display = 'none';
        }
    })

    if (bookmarkBtn) {
        bookmarkBtn.addEventListener('click', function() {
            const offerId = this.getAttribute('data-offer-id');
            const isFavorite = this.getAttribute('data-is-favorite') === 'true';
            toggleFavorite(offerId, this);
        });
    }

    // Gestion du modal de candidature (si le bouton existe)
    if (btn && btn.tagName.toLowerCase() === 'button') {
        btn.addEventListener('click', function() {
            modal.style.display = 'flex';
        })

        window.addEventListener('click', function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        })

        resume.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const fileName = file?.name || 'Aucun fichier sélectionné';
            const fileType = file?.type;

            // Vérification du type de fichier
            if (fileType !== 'application/pdf') {
                alert('Veuillez sélectionner un fichier au format PDF uniquement.');
                e.target.value = ''; // Réinitialise l'input
                document.getElementById('file-display').classList.add('hidden');
                return;
            }

            // Affichage du nom du fichier si valide
            document.getElementById('file-name').textContent = fileName;
            document.getElementById('file-display').classList.remove('hidden');
        });

        removeResume.addEventListener('click', function() {
            const fileInput = document.getElementById('resume');
            fileInput.value = ''; // Réinitialise l'input
            document.getElementById('file-display').classList.add('hidden');
        });

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitApplication(form);
        })
    }
}

function toggleFavorite(offerId, button) {
    fetch(`/toggle-favorite/${offerId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': window.csrf_token,
            'Content-Type': 'application/json',
        },
    }).then(response => response.json()).then(data => {
        if (data.is_favorite) {
            button.innerHTML = 'Retirer <i class="fas fa-bookmark"></i>';
            button.setAttribute('data-is-favorite', 'true');
        } else {
            button.innerHTML = 'Sauvegarder <i class="far fa-bookmark"></i>';
            button.setAttribute('data-is-favorite', 'false');
        }
    }).catch(error => console.error('Error:', error));
}

function submitApplication(form) {
    const formData = new FormData(form);
    const offerId = document.getElementById('application_btn').getAttribute('data-offer-id');

    fetch(`/submit-application/${offerId}/`, {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRFToken': window.csrf_token }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Succès
            const confirmationModal = document.getElementById('confirmation_modal');
            document.getElementById('successMessages').textContent = data.message;
            document.getElementById('successMessages').classList.remove('hidden');

            // Fermer la modale après délai
            setTimeout(() => {
                document.getElementById('application_btn').style.display = 'none';
                document.getElementById('bookmark_btn').style.display = 'none';
                document.getElementById('application_modal').style.display = 'none';

                // Afficher la modale de confirmation
                confirmationModal.style.display = 'flex';

            }, 1500); // 1.5s avant fermeture

            // Gestion des fermetures
            document.getElementById('closeConfirmation').onclick = () => {
                confirmationModal.style.display = 'none';
            };
            document.getElementById('closeConfirmationBtn').onclick = () => {
                confirmationModal.style.display = 'none';
            };
            window.addEventListener('click', (event) => {
                if (event.target === confirmationModal) {
                    confirmationModal.style.display = 'none';
                }
            });
        } else {
            document.getElementById('errorMessages').textContent = data.message;
            document.getElementById('errorMessages').classList.remove('hidden');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('errorMessages').textContent = 'Erreur réseau ou serveur';
        document.getElementById('errorMessages').classList.remove('hidden');
    });
}

