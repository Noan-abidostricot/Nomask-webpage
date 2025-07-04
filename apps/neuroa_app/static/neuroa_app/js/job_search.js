function clear_filters() {
    let filter_fields = document.getElementsByClassName('input-lg');
    Array.from(filter_fields).forEach(function(fld) {
        fld.value = '';
    });
    document.getElementById('favorites-filter').setAttribute('data-active', 'false');
    document.getElementById('favorites-filter').classList.remove('active');
}

function init() {
    // Gestion des champs de formulaire
    document.querySelectorAll('select.input-lg').forEach(select => {
        // Mise à jour visuelle des selects
        select.classList.toggle('text-neutral-400', !select.value);
        select.addEventListener('change', () => {
            select.classList.toggle('text-neutral-400', !select.value);
        });
    });

    // Gestion du filtre des favoris
    const favoritesFilter = document.getElementById('favorites-filter');

    favoritesFilter?.addEventListener('click', (e) => {
        e.preventDefault();

        const filterButton = e.currentTarget;
        // Bascule l'état du dataset
        const newState = filterButton.dataset.active !== "true";
        filterButton.dataset.active = newState.toString();

        // Mise à jour visuelle
        filterButton.classList.toggle('active', newState);
        const icon = filterButton.querySelector('i');
        icon.classList.toggle('fa-regular', !newState);
        icon.classList.toggle('fa-solid', newState);

        // Crée un champ caché temporaire pour la soumission
        const tempInput = document.createElement('input');
        tempInput.type = 'hidden';
        tempInput.name = 'favorites_only';
        tempInput.value = newState;
        e.target.closest('form').appendChild(tempInput);

        // Soumission du formulaire
        e.target.closest('form').submit();
    });
}

