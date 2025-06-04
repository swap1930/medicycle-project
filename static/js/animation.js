// Animations script file for MediCycle

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initAnimations();
});

// Initialize animations
function initAnimations() {
    // Shine effect on cards
    initShineEffect();
    
    // Floating animation for elements
    initFloatingAnimation();
    
    // Scale effect on hover
    initScaleEffect();
    
    // Pulse animation for icons
    initPulseAnimation();
}

// Shine effect on cards
function initShineEffect() {
    const shineElements = document.querySelectorAll('.shine-effect');
    
    shineElements.forEach(element => {
        element.addEventListener('mousemove', function(e) {
            const { left, top, width, height } = this.getBoundingClientRect();
            const x = e.clientX - left;
            const y = e.clientY - top;
            
            const xPercent = Math.floor((x / width) * 100);
            const yPercent = Math.floor((y / height) * 100);
            
            this.style.background = `radial-gradient(circle at ${xPercent}% ${yPercent}%, rgba(255,255,255,0.2) 0%, transparent 50%)`;
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.background = '';
        });
    });
}

// Floating animation for elements
function initFloatingAnimation() {
    const floatingElements = document.querySelectorAll('.floating');
    
    // Create Intersection Observer to trigger animation when element is visible
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'float 3s ease-in-out infinite';
                // Unobserve after animation starts
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });
    
    floatingElements.forEach(element => {
        observer.observe(element);
    });
}

// Scale effect on hover
function initScaleEffect() {
    const scaleElements = document.querySelectorAll('.scale-effect');
    
    scaleElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// Pulse animation for icons
function initPulseAnimation() {
    const pulseElements = document.querySelectorAll('.pulse-animation');
    
    // Create Intersection Observer to trigger animation when element is visible
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'pulse 2s ease-in-out infinite';
                // Unobserve after animation starts
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });
    
    pulseElements.forEach(element => {
        observer.observe(element);
    });
}

// Glow effect on hover
document.addEventListener('DOMContentLoaded', function() {
    const glowElements = document.querySelectorAll('.glow-effect');
    
    glowElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 0 15px rgba(24, 119, 242, 0.7)';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.boxShadow = '';
        });
    });
}); 