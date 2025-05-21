// Armazena a posição anterior do scroll
let lastScrollTop = 0;

function handleScroll() {
    const header = document.querySelector('header');
    const navbar = document.querySelector('.navbar');
    const aboutUsSection = document.querySelector('.section-content'); // Supondo que seja a seção "Sobre Nós"
    const areasDeAtuacaoSection = document.querySelector('#areas-de-atuacao');
    const scrollTop = window.scrollY;

    // Scroll Down / Up Handling
    if (scrollTop > lastScrollTop) {
        // Scrolling down
        header.classList.add('header-navbar-scrolled');
        navbar.classList.add('header-navbar-scrolled');
    } else {
        // Scrolling up
        header.classList.remove('header-navbar-scrolled');
        navbar.classList.remove('header-navbar-scrolled');
    }
    lastScrollTop = scrollTop;

    // Show "About Us" section on scroll down
    if (scrollTop > window.innerHeight / 2) {
        aboutUsSection.style.opacity = '1';
        aboutUsSection.style.transform = 'translateY(0)';
    } else {
        aboutUsSection.style.opacity = '0';
        aboutUsSection.style.transform = 'translateY(50px)';
    }

    // Show "Áreas de Atuação" section on scroll down
    if (scrollTop > window.innerHeight) {
        areasDeAtuacaoSection.style.opacity = '1';
        areasDeAtuacaoSection.style.transform = 'translateY(0)';
    } else {
        areasDeAtuacaoSection.style.opacity = '0';
        areasDeAtuacaoSection.style.transform = 'translateY(50px)';
    }
}

// Adiciona o listener de evento de scroll
window.addEventListener('scroll', handleScroll);

document.addEventListener('DOMContentLoaded', function () {
    const aboutUsSection = document.querySelector('.section-content');
    const areasDeAtuacaoSection = document.querySelector('#areas-de-atuacao');

    aboutUsSection.style.transition = 'opacity var(--transition-ease), transform var(--transition-ease)';
    aboutUsSection.style.opacity = '0';
    aboutUsSection.style.transform = 'translateY(50px)';

    areasDeAtuacaoSection.style.transition = 'opacity var(--transition-ease), transform var(--transition-ease)';
    areasDeAtuacaoSection.style.opacity = '0';
    areasDeAtuacaoSection.style.transform = 'translateY(50px)';
});

