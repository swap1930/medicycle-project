// Scroll Animation System using Intersection Observer API
document.addEventListener('DOMContentLoaded', function() {
    // Show page loader initially
    showPageLoader();
    
    // Initialize animations after page load
    setTimeout(() => {
        hidePageLoader();
        initScrollAnimations();
        initNumberCounters();
        initHoverAnimations();
        createParticles();
    }, 1000);
});

// Show page loader animation
function showPageLoader() {
    const loader = document.querySelector('.page-loader');
    if (loader) {
        loader.style.display = 'flex';
    }
}

// Hide page loader animation
function hidePageLoader() {
    const loader = document.querySelector('.page-loader');
    if (loader) {
        loader.style.opacity = '0';
        loader.style.transition = 'opacity 0.5s ease';
        
        setTimeout(() => {
            loader.style.display = 'none';
        }, 500);
    }
}

// Set up scroll animations for elements
function initScrollAnimations() {
    // Elements that will animate when they come into view
    const animatedElements = document.querySelectorAll('.feature-card, .faq-item, .footer-column, .hero-content, .stat-item');
    
    // Create an Intersection Observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Add animation classes when the element is visible
                entry.target.classList.add('animate');
                
                // Optionally stop observing after animation is triggered
                observer.unobserve(entry.target);
            }
        });
    }, {
        // Options
        root: null, // Use viewport as root
        threshold: 0.1, // Trigger when 10% of the element is visible
        rootMargin: '0px' // No margin
    });
    
    // Observe all elements
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

// Animated number counters
function initNumberCounters() {
    // Example: You can add number counters to display stats
    const counters = document.querySelectorAll('.counter-value');
    
    // Create an observer for counters
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-target'));
                const duration = 2000; // 2 seconds
                const step = Math.ceil(target / (duration / 30)); // Update every 30ms
                
                let current = 0;
                const timer = setInterval(() => {
                    current += step;
                    counter.textContent = current;
                    
                    if (current >= target) {
                        counter.textContent = target; // Ensure exact final value
                        clearInterval(timer);
                    }
                }, 30);
                
                observer.unobserve(counter);
            }
        });
    }, {
        threshold: 0.5
    });
    
    // Observe all counters
    counters.forEach(counter => {
        observer.observe(counter);
    });
}

// Enhanced hover effects
function initHoverAnimations() {
    // Feature cards hover effect with 3D tilt
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        card.addEventListener('mousemove', function(e) {
            // Get mouse position relative to the card
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Calculate rotation based on mouse position
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            // Reduce the tilt effect (divide by higher number for less tilt)
            const tiltX = (y - centerY) / 20;
            const tiltY = (centerX - x) / 20;
            
            // Apply transformation
            card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale3d(1.02, 1.02, 1.02)`;
        });
        
        // Reset on mouse leave
        card.addEventListener('mouseleave', function() {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
            card.style.transition = 'transform 0.5s ease';
        });
    });
    
    // Smooth animation for navigation links
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transition = 'transform 0.3s ease';
            this.style.transform = 'translateY(-3px)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Add shine effect to buttons on hover
    document.querySelectorAll('.btn-hover-effect').forEach(button => {
        button.addEventListener('mouseenter', addShineEffect);
    });
    
    // Add ripple effect to buttons on click
    document.querySelectorAll('.search-btn, .subscribe-btn, .view-more-btn').forEach(button => {
        button.addEventListener('click', createRippleEffect);
    });
}

// Create shine effect on buttons
function addShineEffect(e) {
    const button = e.currentTarget;
    
    // Remove any existing shine elements
    const existingShine = button.querySelector('.shine');
    if (existingShine) {
        existingShine.remove();
    }
    
    // Create shine element
    const shine = document.createElement('span');
    shine.classList.add('shine');
    shine.style.position = 'absolute';
    shine.style.top = '0';
    shine.style.left = '-100%';
    shine.style.width = '100%';
    shine.style.height = '100%';
    shine.style.background = 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)';
    shine.style.transition = 'left 0.5s ease';
    
    // Ensure the button has position relative
    if (getComputedStyle(button).position !== 'relative') {
        button.style.position = 'relative';
    }
    button.style.overflow = 'hidden';
    
    // Add shine to button
    button.appendChild(shine);
    
    // Trigger animation
    setTimeout(() => {
        shine.style.left = '100%';
    }, 10);
    
    // Remove shine after animation
    setTimeout(() => {
        if (shine.parentNode === button) {
            button.removeChild(shine);
        }
    }, 700);
}

// Create ripple effect on button click
function createRippleEffect(e) {
    const button = e.currentTarget;
    
    // Create ripple element
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');
    
    // Get button dimensions
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    
    // Set ripple size and position
    ripple.style.width = ripple.style.height = `${diameter}px`;
    ripple.style.left = `${e.clientX - button.getBoundingClientRect().left - radius}px`;
    ripple.style.top = `${e.clientY - button.getBoundingClientRect().top - radius}px`;
    
    // Add ripple styles
    ripple.style.position = 'absolute';
    ripple.style.borderRadius = '50%';
    ripple.style.transform = 'scale(0)';
    ripple.style.backgroundColor = 'rgba(255, 255, 255, 0.7)';
    ripple.style.animation = 'ripple 0.6s linear';
    
    // Ensure button has position relative
    if (getComputedStyle(button).position !== 'relative') {
        button.style.position = 'relative';
    }
    button.style.overflow = 'hidden';
    
    // Add ripple to button
    button.appendChild(ripple);
    
    // Define ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Remove ripple after animation
    setTimeout(() => {
        ripple.remove();
        style.remove();
    }, 600);
}

// Add particle animation in hero section
function createParticles() {
    const hero = document.querySelector('.hero');
    if (!hero) return;
    
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random position, size and animation delay
        const size = Math.random() * 10 + 5;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 5}s`;
        
        hero.appendChild(particle);
    }
}

// Add to scrolling reveal system
window.addEventListener('load', function() {
    // Start animations after page load
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) {
        setTimeout(() => {
            heroContent.classList.add('animate');
        }, 300);
    }
    
    // Add typewriter effect to logo text if needed
    animateLogoText();
});

// Animate logo text
function animateLogoText() {
    const logoText = document.querySelector('.logo-text');
    if (logoText) {
        logoText.classList.add('animate');
    }
} 