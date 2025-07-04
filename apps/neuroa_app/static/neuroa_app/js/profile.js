function init(exp_type_inf) {
    const experienceModal = document.getElementById('experienceModal');
    const attributeModal = document.getElementById('attributeModal');
    const cancelExperience = document.getElementById('cancelExperience');
    const cancelAttribute = document.getElementById('cancelAttribute');
    const experienceForm = document.getElementById('experienceForm');
    const attributeForm = document.getElementById('attributeForm');
    const experienceType = document.getElementById('id_experience_type');
    const uploadPhotoBtn = document.getElementById('uploadPhotoBtn');
    const photoUpload = document.getElementById('id_photo');
    const basicInfoModal = document.getElementById('basicInfoModal');
    const candidateInfoModal = document.getElementById('candidateInfoModal');
    const cancelBasicInfo = document.getElementById('cancelBasicInfo');
    const cancelCandidateInfo = document.getElementById('cancelCandidateInfo');
    const basicInfoForm = document.getElementById('basicInfoForm');
    const candidateInfoForm = document.getElementById('candidateInfoForm');
    const experienceContractTypeField = document.getElementById('id_experience_contract_type').closest('p');
    const experienceWorkTime = document.getElementById('id_experience_work_time').closest('p');
    const startMonth = document.getElementById('id_start_month');
    const startYear = document.getElementById('id_start_year');
    const endMonth = document.getElementById('id_end_month');
    const endYear = document.getElementById('id_end_year');
    const isCurrentPosition = document.getElementById('id_is_current_position');
    const requiredLabels = document.querySelectorAll('.required-field');
    const closeBasicInfoModal = document.getElementById('closeBasicInfoModal');
    const closeCandidateInfoModal = document.getElementById('closeCandidateInfoModal');
    const closeExperienceModal = document.getElementById('closeExperienceModal');
    const closeAttributeModal = document.getElementById('closeAttributeModal');

    $('#id_mobilities').select2({
        width: '100%',
    });

    requiredLabels.forEach(label => {
        const asterisk = document.createElement('span');
        asterisk.textContent = ' *';
        asterisk.style.color = 'red';
        label.appendChild(asterisk);
    });

    // Gestion de l'upload de photo
    uploadPhotoBtn.addEventListener('click', () => photoUpload.click());
    photoUpload.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('photo', file);
            formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

            fetch('/upload-photo/', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const profilePhoto = document.getElementById('profilePhoto');
                    if (profilePhoto.tagName.toLowerCase() === 'i') {
                        // Remplacer l'icône par une image
                        const img = document.createElement('img');
                        img.id = 'profilePhoto';
                        img.src = data.photo_url;
                        img.alt = 'Photo de profil';
                        img.className = 'w-32 h-32 rounded-full object-cover mr-4';
                        profilePhoto.parentNode.replaceChild(img, profilePhoto);
                    } else {
                        profilePhoto.src = data.photo_url;
                    }
                }
            });
        }
    });

    // Ouverture de la modale d'infos de base
    document.querySelectorAll('.editBasicInfoBtn').forEach(button => {
        button.addEventListener('click', () => {
            basicInfoModal.classList.remove('hidden');
            basicInfoModal.classList.add('flex');
        });
    });

    // Ouverture de la modale d'infos du candidat
    document.querySelectorAll('.editCandidateInfoBtn').forEach(button => {
        button.addEventListener('click', () => {
            candidateInfoModal.classList.remove('hidden');
            candidateInfoModal.classList.add('flex');

            const mobility_textarea = document.querySelector('[aria-describedby="select2-id_mobilities-container"]');

            if (mobility_textarea) {
              mobility_textarea.setAttribute('placeholder', 'Sélectionnez');
            }

            const mobilitiesSelectedItems = document.querySelector('.selection');
            const classes = ['w-[280px]', 'h-10', 'pl-3', 'text-sm', 'font-roboto', 'border-[var(--border_color_primary)]', 'rounded', 'md:w-[590px]'];
            classes.forEach(className => {
                mobilitiesSelectedItems.classList.add(className);
            });
        });
    });

    function setupModalListeners(buttons, modal) {
        buttons.forEach(e => {
            e.addEventListener('click', () => {
                modal.classList.add('hidden');
                modal.classList.remove('flex');
            });
        });
    }

    setupModalListeners([cancelBasicInfo, closeBasicInfoModal], basicInfoModal);

    setupModalListeners([cancelCandidateInfo, closeCandidateInfoModal], candidateInfoModal);

    basicInfoForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(basicInfoForm);
        formData.append('action', 'update_basic_info');

        // Réinitialiser les messages
        document.querySelector('#basicInfoModal #errorMessages').textContent = '';
        document.querySelector('#basicInfoModal #successMessages').textContent = '';

        fetch('/update-profile/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.querySelector('#basicInfoModal #successMessages').textContent = data.message || 'Opération réussie!';
                setTimeout(() => {
                    basicInfoModal.classList.add('hidden');
                    basicInfoModal.classList.remove('flex');
                    location.reload();
                }, 1500);
            } else {
                document.querySelector('#basicInfoModal #errorMessages').textContent = data.message || 'Erreur inconnue';
            }
        }).catch(error => {
            document.querySelector('#basicInfoModal #errorMessages').textContent = 'Erreur réseau';
            console.error("Erreur lors de la mise à jour des informations de base", data.errors);
        });
    });

    candidateInfoForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(candidateInfoForm);
        formData.append('action', 'update_candidate_info');

        // Réinitialiser les messages
        document.querySelector('#basicInfoModal #errorMessages').textContent = '';
        document.querySelector('#basicInfoModal #successMessages').textContent = '';

        fetch('/update-profile/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.querySelector('#candidateInfoModal #successMessages').textContent = data.message || 'Opération réussie!';
                setTimeout(() => {
                    basicInfoModal.classList.add('hidden');
                    basicInfoModal.classList.remove('flex');
                    location.reload();
                }, 1500);
            } else {
                document.querySelector('#candidateInfoModal #errorMessages').textContent = data.message || 'Erreur inconnue';
            }
        }).catch(error => {
            document.querySelector('#candidateInfoModal #errorMessages').textContent = 'Erreur réseau';
            console.error("Erreur lors de la mise à jour des informations de base", data.errors);
        });
    });

    // Gestion de l'ajout et de la modification d'expérience
    document.querySelectorAll('.addExperienceBtn').forEach(button => {
        button.addEventListener('click', () => {
            const experienceType = button.getAttribute('data-type');
            openExperienceModal('add', experienceType);
        });
    });

    document.querySelectorAll('.editExperienceBtn').forEach(button => {
        button.addEventListener('click', function() {
            const experienceId = this.getAttribute('data-id');
            const experienceType = button.getAttribute('data-type');
            openExperienceModal('edit', experienceType, experienceId);
        });
    });

    function updateExperienceLabels(type) {
        const infos = exp_type_inf[type] || exp_type_inf['personal'];
        document.getElementById('nameLabel').textContent = infos.name_label;
        document.getElementById('organisationLabel').textContent = infos.organization_label;
        document.getElementById('currentLabel').textContent = infos.is_current_label;
    }

    function getExperienceTypeLabel(type) {
        // Pour le titre du modal
        return (exp_type_inf[type] && exp_type_inf[type].type_label) || type;
    }

    function openExperienceModal(mode, type, id = null) {
        const modal = document.getElementById('experienceModal');
        const form = document.getElementById('experienceForm');
        const title = document.getElementById('experienceModalTitle');
        const submitBtn = document.getElementById('submitExperience');
        const typeField = document.getElementById('experienceType');
        const idField = document.getElementById('experienceId');

        // Réinitialiser les messages
        document.querySelector('#experienceModal #errorMessages').textContent = '';
        document.querySelector('#experienceModal #successMessages').textContent = '';

        // MAJ des labels dynamiquement
        updateExperienceLabels(type);
        const label = getExperienceTypeLabel(type).toLowerCase();

        if (mode === 'add') {
            title.textContent = "Ajouter une " + label;
            submitBtn.textContent = 'Ajouter';
            form.reset();
            typeField.value = type;
            idField.value = '';
            toggleExpFields();
        } else {
            title.textContent = "Modifier " + getArticle(label) + label;
            submitBtn.textContent = 'Modifier';
            loadExperienceData(id);
        }

        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }

    function getArticle(word) {
      // Liste des voyelles (minuscule et majuscule)
      const voyelles = ['a', 'e', 'i', 'o', 'u', 'y', 'h', 'â', 'é', 'è', 'ê', 'ë', 'î', 'ï', 'ô', 'û', 'ü', 'ù', 'œ'];
      if (!word || word.length === 0) return "la "; // Par défaut

      // On prend la première lettre (en minuscule)
      const firstLetter = word[0].toLowerCase();
      // Si c'est une voyelle ou un h muet, on met l'
      if (voyelles.includes(firstLetter)) {
        return "l'";
      }
      // Sinon, on met la
      return "la ";
    }

    cancelExperience.addEventListener('click', () => {
        experienceModal.classList.add('hidden');
        experienceModal.classList.remove('flex');
    });

    closeExperienceModal.addEventListener('click', function() {
        experienceModal.classList.add('hidden');
        experienceModal.classList.remove('flex');
    });

    experienceForm.addEventListener('submit', (e) => {
        e.preventDefault();
        if (!checkDate()) return;
        const formData = new FormData(experienceForm);
        formData.append('action', 'add_experience');
        formData.set('experience_type', document.getElementById('experienceType').value);

        // Réinitialiser les messages
        document.querySelector('#experienceModal #errorMessages').textContent = '';
        document.querySelector('#experienceModal #successMessages').textContent = '';

        fetch(formData.get('experience_id') ? '/update-experience/' : '/update-profile/', {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': window.csrf_token }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.querySelector('#experienceModal #successMessages').textContent = data.message || 'Opération réussie!';
                setTimeout(() => {
                    experienceModal.classList.add('hidden');
                    location.reload();
                }, 1500);
            } else {
                // Afficher les erreurs de validation
                if (data.errors) {
                    const errorMessages = Object.values(data.errors).join('<br>');
                    document.querySelector('#experienceModal #errorMessages').innerHTML = errorMessages;
                } else {
                    document.querySelector('#experienceModal #errorMessages').textContent = data.message || 'Erreur inconnue';
                }
            }
        })
        .catch(error => {
            document.querySelector('#experienceModal #errorMessages').textContent = 'Erreur réseau';
            console.error('Error:', error);
        });
    });

    // Gestion de l'ajout et de la modification d'attribut
    document.querySelectorAll('.addAttributeBtn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const attributeType = button.getAttribute('data-type');
            const name = document.querySelector('textarea[name="name"]');
            if (name) {
                name.placeholder = "Ex: " + {
                    skill: "Python, Management, Langues ...",
                    hobby: "Randonnée, Jeux vidéo, Cuisine ...",
                    cause: "Écologie, Droits humains, Éducation ..."
                }[button.dataset.type] || "Saisissez des éléments";
            }
            openAttributeModal('add', attributeType);
        });
    });

    function openAttributeModal(mode, type, id = null) {
        const modal = document.getElementById('attributeModal');
        const form = document.getElementById('attributeForm');
        const title = document.getElementById('attributeModalTitle');
        const submitBtn = document.getElementById('submitAttribute');
        const typeField = document.getElementById('attributeType');
        const idField = document.getElementById('attributeId');

        // Réinitialiser les messages
        document.querySelector('#attributeModal #errorMessages').textContent = '';
        document.querySelector('#attributeModal #successMessages').textContent = '';

        if (mode === 'add') {
            const typeTexts = {
              skill: "une compétence",
              hobby: "un loisir ou une passion",
              cause: "une cause ou un engagement"
            };

            title.textContent = `Ajouter ${typeTexts[type] || "un élément"}`;
            typeField.value = type;
            submitBtn.textContent = 'Ajouter';
            form.reset();
            idField.value = '';
        } else {
            title.textContent = `Modifier ${type === 'skill' ? 'la compétence' : 'le centre d\'intérêt'}`;
            submitBtn.textContent = 'Modifier';
            loadAttributeData(id);
        }

        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }

    cancelAttribute.addEventListener('click', () => {
        attributeModal.classList.add('hidden');
        attributeModal.classList.remove('flex');
    });

     closeAttributeModal.addEventListener('click', function() {
        attributeModal.classList.add('hidden');
        attributeModal.classList.remove('flex');
    });

    attributeForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const textarea = document.querySelector('textarea[name="name"]');
        const entries = textarea.value.split(',');

        errorContainer = document.querySelector('#attributeModal #errorMessages')
        successContainer =document.querySelector('#attributeModal #successMessages')

        if (textarea.value.length > 300) {
            errorContainer.textContent = "Text trop long (300 caractères maximum)";
            return;
        }

        // Validation client avant envoi
        let hasErrors = false;
        entries.forEach(entry => {
            const trimmedEntry = entry.trim();
            if (trimmedEntry.length > 50) {
                alert(`❌ "${trimmedEntry}" dépasse 50 caractères`);
                hasErrors = true;
            }
        });

        // Blocage de la soumission si erreurs
        if (hasErrors) {
            return;
        }

        const formData = new FormData(attributeForm);
        formData.append('action', 'add_attribute');
        formData.set('attribute_type', document.getElementById('attributeType').value);

        // Réinitialiser les messages
        errorContainer.textContent = '';
        successContainer.textContent = '';

        fetch(formData.get('attribute_id') ? '/update-attribute/' : '/update-profile/', {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': window.csrf_token }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.querySelector('#attributeModal #successMessages').textContent = data.message || 'Opération réussie!';
                setTimeout(() => {
                    attributeModal.classList.add('hidden');
                    location.reload();
                }, 700);
            } else {
                document.querySelector('#attributeModal #errorMessages').textContent = data.message || 'Erreur inconnue';
            }
        })
        .catch(error => {
            document.querySelector('#attributeModal #errorMessages').textContent = 'Erreur réseau';
            console.error('Error:', error);
        });
    });

    function loadExperienceData(id) {
        fetch(`/get-experience-data/${id}/`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error("Erreur lors du chargement des données de l'expérience:", data.error);
                    return;
                }

                const form = document.getElementById('experienceForm');
                form.querySelector('#experienceId').value = data.id;
                form.querySelector('#experienceType').value = data.experience_type;

                form.querySelector('#id_organization').value = data.organization;
                form.querySelector('#id_name').value = data.name;
                form.querySelector('#id_city').value = data.city;
                form.querySelector('#id_country').value = data.country;
                form.querySelector('#id_experience_contract_type').value = data.experience_contract_type;
                form.querySelector('#id_experience_work_time').value = data.experience_work_time;
                form.querySelector('#id_start_month').value = data.start_month;
                form.querySelector('#id_start_year').value = data.start_year;
                form.querySelector('#id_end_month').value = data.end_month || '';
                form.querySelector('#id_end_year').value = data.end_year || '';
                form.querySelector('#id_is_current_position').value = data.is_current_position === true ? 'True' : (data.is_current_position === false ? 'False' : '');
                form.querySelector('#id_url').value = data.url || '';
                form.querySelector('#id_description').value = data.description;

                // Mettre à jour l'affichage des champs en fonction du type d'expérience
                toggleExpFields();
            })
            .catch(error => console.error("Erreur lors de la récupération des données de l'expérience:", error));
    }

    function loadAttributeData(id) {
        fetch(`/get-attribute-data/${id}/`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error("Erreur lors du chargement des données de l'attribut:", data.error);
                    return;
                }

                const form = document.getElementById('attributeForm');
                form.querySelector('#attributeId').value = data.id;
                form.querySelector('#attributeType').value = data.attribute_type;

                form.querySelector('#id_name').value = data.name;
            })
            .catch(error => console.error("Erreur lors de la récupération des données de l'attribut:", error));
    }

    // Suppression de la photo
    const deletePhotoBtn = document.getElementById('deletePhotoBtn');
    deletePhotoBtn.addEventListener('click', () => {
        if (confirm('Êtes-vous sûr de vouloir supprimer votre photo de profil ?')) {
            fetch('/delete-photo/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    photoUpload.value = null;
                    const profilePhoto = document.getElementById('profilePhoto');
                    profilePhoto.src = window.default_profile_url;
                }
            });
        }
    });

    // Suppression des expériences (version améliorée)
    document.querySelectorAll('.deleteExperienceBtn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault(); // Bloque l'action par défaut du bouton

            const experienceId = this.dataset.id;
            if (confirm('Êtes-vous sûr de vouloir supprimer cette expérience ?')) {
                const formData = new FormData();
                formData.append('experience_id', experienceId);

                fetch('/delete-experience/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest' // Header recommandé
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Suppression progressive avec animation
                        const element = this.closest('.exp-card');
                        element.style.transition = 'opacity 0.3s';
                        element.style.opacity = '0';

                        setTimeout(() => {
                            element.remove();
                        }, 300);
                    }
                })
                .catch(error => console.error('Erreur:', error));
            }
        });
    });

    // Suppression des attributs
    document.querySelectorAll('.deleteAttributeBtn').forEach(button => {
        button.addEventListener('click', function() {
            const attributeId = this.getAttribute('data-id');
            if (confirm('Êtes-vous sûr de vouloir supprimer cet attribut ?')) {
                const formData = new FormData();
                formData.append('attribute_id', attributeId);
                fetch('/delete-attribute/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        this.closest('.tag').remove();
                    }
                });
            }
        });
    });

    function toggleExpFields() {
        const experienceType = document.getElementById("experienceType").value;

        // Les champs
        const name = document.getElementById("wrapper_id_name");
        const organization = document.getElementById("wrapper_id_organization");
        const city = document.getElementById("wrapper_id_city");
        const country = document.getElementById("wrapper_id_country");
        const contract = document.getElementById("wrapper_id_experience_contract_type");
        const worktime = document.getElementById("wrapper_id_experience_work_time");
        const placer = document.getElementById("placer");
        const reverse = document.getElementById("reverse");

        // Les astérisques
        const contractAsterisk = document.getElementById("asterisk_id_experience_contract_type");
        const worktimeAsterisk = document.getElementById("asterisk_id_experience_work_time");

        normalClasses = ["flex-col", "md:flex-row"]
        normalDispositionClasses = ["md:col-span-2", "gap-x-11"]
        trainingReverseClasses = ["flex-col-reverse", "md:flex-row-reverse"]

        if (experienceType === "pro") {
            placer.style.display = "none";

            contract.required = true;
            worktime.required = true;

            organization.style.display = "inline";
            city.style.display = "inline";
            country.style.display = "inline";

            contract.style.display = "inline";
            worktime.style.display = "inline";

            contractAsterisk.style.display = "inline";
            worktimeAsterisk.style.display = "inline";

            let iteration = 0;
            normalClasses.forEach(nc => {
                reverse.classList.add(nc)
                reverse.classList.add(normalDispositionClasses[iteration])
                reverse.classList.remove(trainingReverseClasses[iteration])
                iteration ++;
            })

        } else {
            contract.required = false;
            worktime.required = false;

            city.style.display = "none";
            country.style.display = "none";

            contract.style.display = "none";
            worktime.style.display = "none";

            contractAsterisk.style.display = "none";
            worktimeAsterisk.style.display = "none";

            if (experienceType === "personal"){
                organization.style.display = "none";
                placer.style.display = "inline";

                let iteration = 0;
                normalClasses.forEach(nc => {
                    reverse.classList.add(nc)
                    reverse.classList.remove(normalDispositionClasses[iteration])
                    reverse.classList.remove(trainingReverseClasses[iteration])
                    iteration ++;
                })

            } else {
                organization.style.display = "inline";
                placer.style.display = "none";
                let iteration = 0;
                normalClasses.forEach(nc => {
                    reverse.classList.remove(nc)
                    reverse.classList.add(normalDispositionClasses[iteration])
                    reverse.classList.add(trainingReverseClasses[iteration])
                    iteration ++;
                })
            }
        }
    }

    endMonth.addEventListener('change', function() {
        const currentDate = new Date();
        const selectedDate = new Date(endYear.value, endMonth.value - 1);
        if (this.value === "" || selectedDate > currentDate) {
            isCurrentPosition.selectedIndex = 1;
        } else {
            isCurrentPosition.selectedIndex = 2;
        }
    });

    endYear.addEventListener('change', function() {
        const currentDate = new Date();
        const selectedDate = new Date(this.value, endMonth.value - 1);
        if (this.value === "" || selectedDate > currentDate) {
            isCurrentPosition.selectedIndex = 1;
        } else {
            isCurrentPosition.selectedIndex = 2;
        }
    });

    isCurrentPosition.addEventListener('change', function() {
        const currentDate = new Date();
        const selectedDate = new Date(endYear.value, endMonth.value - 1);
        if (this.value === 'True' && (selectedDate < currentDate || (endMonth.value === "" && endYear.value === ""))) {
            endMonth.disabled = true;
            endYear.disabled = true;
            endMonth.value = '';
            endYear.value = '';
        } else if (this.value === 'True' && selectedDate > currentDate) {
            endMonth.disabled = false;
            endYear.disabled = false;
        } else if (this.value === 'False' && selectedDate > currentDate){
            endMonth.value = '';
            endYear.value = '';
        } else {
            endMonth.disabled = false;
            endYear.disabled = false;
        }
    });

    function checkDate() {
        if (!startMonth.value || !startYear.value) {
            alert("Le mois et l'année de début sont obligatoires.");
            return false;
        }

        if (startMonth < 1 || startMonth > 12) {
            alert("Le mois de début doit être compris entre 1 et 12.");
            return false;
        }

        if (endMonth && (endMonth < 1 || endMonth > 12)) {
            alert("Le mois de fin doit être compris entre 1 et 12.");
            return false;
        }

        if (isCurrentPosition.value !== 'True' && (!endMonth.value || !endYear.value)) {
            alert("Le mois et l'année de fin sont obligatoires si ce n'est pas votre poste actuel.");
            return false;
        }

        if (endMonth.value && endYear.value) {
            const startValue = new Date(startYear.value, startMonth.value - 1);
            const endValue = new Date(endYear.value, endMonth.value - 1);

            if (endValue < startValue) {
                alert("La date de fin ne peut pas être antérieure à la date de début.");
                return false;
            }
        }
        return true
    };

    startMonth.addEventListener('change', function() {
        if (endMonth.value && endYear.value) {
            endMonth.min = startMonth.value;
            endYear.min = startYear.value;
        }
    });

    startYear.addEventListener('change', function() {
        if (endMonth.value && endYear.value) {
            endMonth.min = startMonth.value;
            endYear.min = startYear.value;
        }
    });

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
}

