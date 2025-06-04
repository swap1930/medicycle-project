// Preloading Script for MediCycle Website
// This script helps with performance optimization by preloading key resources

// Execute when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add preload class to body to prevent transitions during page load
    if (document.body) {
        document.body.classList.add('preload');
    }
    
    // Preload images to avoid flickering during animations
    preloadImages();
    
    // Add page transition effects
    setupPageTransitions();
    
    // Initialize lazy loading for non-critical resources
    initLazyLoading();
    
    // Add smooth scrolling behavior for the whole page
    enableSmoothScrolling();
});

// Preload important images to avoid flickering during animations
function preloadImages() {
    // Array of critical images to preload (add your important images here)
    const imagesToPreload = [
        // Add local images here if needed
    ];
    
    imagesToPreload.forEach(src => {
        const img = new Image();
        img.src = src;
    });
}

// Setup page transition effects
function setupPageTransitions() {
    // Add transition class to body
    if (document.body) {
        document.body.classList.add('page-transition');
    }
    
    // Handle links for page transitions
    document.querySelectorAll('a[href^="http"], a[href^="/"]').forEach(link => {
        link.addEventListener('click', function(e) {
            // Don't apply transition to links that open in new tab
            if (this.target === '_blank' || e.ctrlKey || e.metaKey) return;
            
            const href = this.getAttribute('href');
            
            // Skip if it's a page anchor
            if (href.startsWith('#')) return;
            
            e.preventDefault();
            
            // Add exit animation
            if (document.body) {
                document.body.classList.add('page-exit');
            }
            
            // Navigate after animation completes
            setTimeout(() => {
                window.location.href = href;
            }, 300);
        });
    });
    
    // Add entry animation for page load
    window.addEventListener('load', () => {
        if (document.body) {
            document.body.classList.add('page-enter');
        }
    });
}

// Initialize lazy loading for non-critical resources
function initLazyLoading() {
    // Check if IntersectionObserver is supported
    if ('IntersectionObserver' in window) {
        const lazyElements = document.querySelectorAll('.lazy-load');
        
        const lazyObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    
                    // Handle different element types
                    if (element.tagName === 'IMG') {
                        // For images, replace the src
                        element.src = element.dataset.src;
                    } else if (element.tagName === 'DIV' || element.tagName === 'SECTION') {
                        // For background images in divs or sections
                        if (element.dataset.background) {
                            element.style.backgroundImage = `url(${element.dataset.background})`;
                        }
                    }
                    
                    // Remove lazy loading class
                    element.classList.remove('lazy-load');
                    
                    // Stop observing the element
                    lazyObserver.unobserve(element);
                }
            });
        }, {
            rootMargin: '100px' // Load when within 100px of viewport
        });
        
        // Observe all lazy elements
        lazyElements.forEach(element => {
            lazyObserver.observe(element);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        const lazyLoad = function() {
            const lazyElements = document.querySelectorAll('.lazy-load');
            
            lazyElements.forEach(element => {
                if (element.getBoundingClientRect().top <= window.innerHeight && 
                    element.getBoundingClientRect().bottom >= 0) {
                    
                    if (element.tagName === 'IMG') {
                        element.src = element.dataset.src;
                    } else if (element.dataset.background) {
                        element.style.backgroundImage = `url(${element.dataset.background})`;
                    }
                    
                    element.classList.remove('lazy-load');
                }
            });
        };
        
        // Initial load
        lazyLoad();
        
        // Add scroll event
        let lazyLoadThrottleTimeout;
        window.addEventListener('scroll', function() {
            if (lazyLoadThrottleTimeout) {
                clearTimeout(lazyLoadThrottleTimeout);
            }
            
            lazyLoadThrottleTimeout = setTimeout(lazyLoad, 250);
        });
    }
}

// Enable smooth scrolling for the whole page
function enableSmoothScrolling() {
    // Add smooth scrolling to all internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return; // Skip empty links
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const offsetTop = targetElement.getBoundingClientRect().top + window.pageYOffset;
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Make scroll-to-top button visible when scrolled down
    const scrollButton = document.querySelector('.scroll-to-top');
    if (scrollButton) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                scrollButton.classList.add('visible');
            } else {
                scrollButton.classList.remove('visible');
            }
        });
        
        // Scroll to top when clicked
        scrollButton.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

// Add resize handler for performance optimization
window.addEventListener('resize', debounce(function() {
    // Handle any resize-specific adjustments here
    adjustResponsiveElements();
}, 250));

// Debounce function to limit frequent calls
function debounce(func, delay) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), delay);
    };
}

// Adjust elements based on screen size
function adjustResponsiveElements() {
    const width = window.innerWidth;
    
    // Example: Adjust feature card layout for better responsiveness
    if (width < 768) {
        document.querySelectorAll('.feature-card').forEach(card => {
            card.classList.add('stacked');
        });
    } else {
        document.querySelectorAll('.feature-card').forEach(card => {
            card.classList.remove('stacked');
        });
    }
}

// Add a scroll-to-top button dynamically
function addScrollToTopButton() {
    const button = document.createElement('button');
    button.classList.add('scroll-to-top');
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.style.position = 'fixed';
    button.style.bottom = '20px';
    button.style.right = '20px';
    button.style.zIndex = '99';
    button.style.opacity = '0';
    button.style.visibility = 'hidden';
    button.style.transition = 'all 0.3s ease';
    button.style.width = '40px';
    button.style.height = '40px';
    button.style.borderRadius = '50%';
    button.style.backgroundColor = 'var(--primary-blue)';
    button.style.color = 'white';
    button.style.border = 'none';
    button.style.boxShadow = 'var(--shadow-md)';
    button.style.cursor = 'pointer';
    
    document.body.appendChild(button);
}

// Execute after window loads completely
window.addEventListener('load', function() {
    // Add scroll to top button
    addScrollToTopButton();
    
    // Remove the preload class from body to enable transitions
    if (document.body) {
        document.body.classList.remove('preload');
    }
});

// Add loader animation for page transitions
function showLoader() {
    const loader = document.querySelector('.page-loader');
    if (loader) {
        loader.style.display = 'flex';
        
        setTimeout(function() {
            loader.style.opacity = '1';
        }, 10);
    }
}

function hideLoader() {
    const loader = document.querySelector('.page-loader');
    if (loader) {
        loader.style.opacity = '0';
        
        setTimeout(function() {
            loader.style.display = 'none';
        }, 300);
    }
}

// This can be called before navigating to a new page
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a.page-transition').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            showLoader();
            setTimeout(function() {
                window.location.href = href;
            }, 500);
        });
    });
}); 