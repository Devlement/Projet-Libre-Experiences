// Empêche toute interaction sur l'overlay
document.addEventListener('DOMContentLoaded', function() {
  const overlay = document.getElementById('loader-overlay');
  if (overlay) {
    ['click', 'mousedown', 'mouseup', 'mousemove', 'touchstart', 'touchmove', 'touchend', 'wheel', 'scroll'].forEach(function(eventName) {
      overlay.addEventListener(eventName, function(e) {
        e.preventDefault();
        e.stopPropagation();
        return false;
      }, { passive: false });
    });
  }
});
// Script JavaScript pour Expériences Satisfaisantes

// Gestion du loader
const loader = {
  show: function() {
    const loaderElement = document.getElementById('loader');
    if (loaderElement) {
      loaderElement.classList.add('active');
    }
  },
  hide: function() {
    const loaderElement = document.getElementById('loader');
    if (loaderElement) {
      loaderElement.classList.remove('active');
    }
  }
};

// Afficher le loader au chargement de la page
window.addEventListener('beforeunload', function() {
  loader.show();
});

// Masquer le loader quand la page est complètement chargée
document.addEventListener('DOMContentLoaded', function() {
  loader.hide();

  // Validation du formulaire de connexion
  const loginForm = document.querySelector('form[action="/login"]');
  if (loginForm) {
    loginForm.addEventListener('submit', function(event) {
      loader.show();
      const username = document.getElementById('username').value.trim();
      const password = document.getElementById('password').value.trim();

      if (username === '' || password === '') {
        alert('Veuillez remplir tous les champs.');
        loader.hide();
        event.preventDefault();
        return;
      }

      if (password.length < 6) {
        alert('Le mot de passe doit contenir au moins 6 caractères.');
        loader.hide();
        event.preventDefault();
        return;
      }
    });
  }

  // Validation du formulaire d'inscription
  const registerForm = document.querySelector('form[action="/register"]');
  if (registerForm) {
    registerForm.addEventListener('submit', function(event) {
      loader.show();
      const username = document.getElementById('username').value.trim();
      const password = document.getElementById('password').value.trim();
      const confirmPassword = document.getElementById('confirm_password').value.trim();

      if (username === '' || password === '' || confirmPassword === '') {
        alert('Veuillez remplir tous les champs.');
        loader.hide();
        event.preventDefault();
        return;
      }

      if (password.length < 6) {
        alert('Le mot de passe doit contenir au moins 6 caractères.');
        loader.hide();
        event.preventDefault();
        return;
      }

      if (password !== confirmPassword) {
        alert('Les mots de passe ne correspondent pas.');
        loader.hide();
        event.preventDefault();
        return;
      }
    });
  }

    // Animation pour les cartes d'expériences
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Confirmation pour les actions destructives
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
                event.preventDefault();
            }
        });
    });
});
