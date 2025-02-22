document.addEventListener('DOMContentLoaded', function() {
    // Scroll animations for feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
        card.style.opacity = 0;
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = 1;
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Hero section button hover effect
    const heroButton = document.querySelector('.hero-section .btn');
    if (heroButton) {
        heroButton.addEventListener('mouseenter', () => {
            heroButton.style.transform = 'scale(1.05)';
        });
        heroButton.addEventListener('mouseleave', () => {
            heroButton.style.transform = 'scale(1)';
        });
    }

    // Additional interactive features can be added here
});
