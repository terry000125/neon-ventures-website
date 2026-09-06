    (function() {
      var navbar = document.getElementById('navbar');
      var navLinks = document.getElementById('navLinks');
      var navToggle = document.getElementById('navToggle');
      function onScroll() {
        navbar.classList.toggle('scrolled', window.scrollY > 20);
      }
      window.addEventListener('scroll', onScroll);
      onScroll();

      navToggle.addEventListener('click', function() {
        navLinks.classList.toggle('open');
      });

      document.querySelectorAll('.nav-links a').forEach(function(a) {
        a.addEventListener('click', function() {
          if (window.innerWidth <= 768) navLinks.classList.remove('open');
        });
      });

      document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
          var href = this.getAttribute('href');
          if (href === '#') return;
          e.preventDefault();
          var target = document.querySelector(href);
          if (target) {
            var top = target.getBoundingClientRect().top + window.pageYOffset - navbar.offsetHeight;
            window.scrollTo({ top: top, behavior: 'smooth' });
          }
        });
      });

      var contactForm = document.getElementById('contactForm');
      if (contactForm) contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        var name = document.getElementById('name').value;
        var email = document.getElementById('email').value;
        var subject = document.getElementById('subject').value || 'Website Inquiry';
        var message = document.getElementById('message').value;
        var body = 'Name: ' + name + '\nEmail: ' + email + '\n\n' + message;
        window.location.href = 'mailto:admin@neonventures.biz?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      });
    })();
