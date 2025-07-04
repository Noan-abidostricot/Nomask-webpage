document.addEventListener('DOMContentLoaded', function() {
    const bookmarkButtons = document.querySelectorAll('.bookmark_btn');

    bookmarkButtons.forEach(button => {
        // Supprimer les anciens écouteurs pour éviter les doublons
        button.replaceWith(button.cloneNode(true));
    });

    // Réattacher les écouteurs sur les nouveaux clones
    document.querySelectorAll('.bookmark_btn').forEach(button => {
        updateButtonAppearance(button);
        button.addEventListener('click', function() {
            const offerId = this.getAttribute('data-offer-id');
            toggleFavorite(offerId, this);
        });
    });
});


function updateButtonAppearance(button) {
    const isFavorite = button.getAttribute('data-is-favorite').toLowerCase() === 'true';
    if (isFavorite) {
        button.innerHTML = '<i class="fa-solid fa-bookmark"></i>';
        button.title = "Retirer des favoris";
    } else {
        button.innerHTML = '<i class="fa-regular fa-bookmark"></i>';
        button.title = "Sauvegarder cette annonce";
    }
}

function toggleFavorite(offerId, button) {
    const isFavorite = button.getAttribute('data-is-favorite') === 'true';

    fetch(`/toggle-favorite/${offerId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({is_favorite: !isFavorite})
    })
    .then(response => response.json())
    .then(data => {
        button.setAttribute('data-is-favorite', data.is_favorite);
        updateButtonAppearance(button);

        if (data.is_favorite) {
            alert("Ajouté aux favoris")
        } else {
            alert("Retiré des favoris")
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


// Fonction pour obtenir le token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
