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

      var params = new URLSearchParams(window.location.search);
      if (params.get('thanks') === '1') {
        var contactForm = document.getElementById('contactForm');
        if (contactForm) {
          contactForm.innerHTML = '<p style="font-size:18px;color:var(--heading-dark);text-align:center;padding:40px 0;">Thank you! Your message has been sent. We\'ll be in touch soon.</p>';
        }
      }
    })();
