// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize existing functions
    initFaqAccordion();
    initSearch();
    initLocationDropdown();
    initFooterToggle();
    initStickySearch();
    initServicesSlider();
    
    // Initialize mobile menu toggle
    initMobileMenu();
    
    // Profile Dropdown Functionality
    const profileContainer = document.querySelector('.profile-container');
    const profileDropdown = document.querySelector('.profile-dropdown');
    
    if (profileContainer && profileDropdown) {
        // User state (would come from your authentication system)
        let isLoggedIn = false;
        
     
        
        // Update dropdown content based on login state
        function updateDropdownContent() {
        }
        
        // Initialize dropdown content
        updateDropdownContent();
        
        // Toggle dropdown visibility when clicking on profile icon
        profileContainer.addEventListener('click', function(e) {
            e.stopPropagation();
            profileDropdown.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!profileContainer.contains(e.target)) {
                profileDropdown.classList.remove('active');
            }
        });
        
        // For demo: Add a way to toggle login status with button
        const testToggleBtn = document.getElementById('test-toggle-login');
        if (testToggleBtn) {
            testToggleBtn.addEventListener('click', function() {
                isLoggedIn = !isLoggedIn;
                updateDropdownContent();
                this.textContent = isLoggedIn ? 
                    'Toggle to Logged Out (Demo)' : 
                    'Toggle to Logged In (Demo)';
            });
        }
        
        // Also keep the keyboard shortcut
        document.addEventListener('keydown', function(e) {
            // Press 'L' key to toggle login status (for demo purposes)
            if (e.key === 'l' || e.key === 'L') {
                isLoggedIn = !isLoggedIn;
                updateDropdownContent();
                if (testToggleBtn) {
                    testToggleBtn.textContent = isLoggedIn ? 
                        'Toggle to Logged Out (Demo)' : 
                        'Toggle to Logged In (Demo)';
                }
                console.log('Login status toggled:', isLoggedIn ? 'Logged In' : 'Logged Out');
            }
        });
    }

    // Improved handling for service images
    const serviceImages = document.querySelectorAll('.service-image, .service-image img');
    serviceImages.forEach(image => {
        // Prevent default behavior without completely stopping events
        image.addEventListener('click', function(e) {
            // Only prevent default to avoid issues with animations
            e.preventDefault();
        });
        
        // Add touch feedback for mobile devices
        image.addEventListener('touchstart', function() {
            const parent = this.closest('.service-item');
            if (parent) {
                parent.classList.add('touched');
            }
        });
        
        image.addEventListener('touchend', function() {
            const parent = this.closest('.service-item');
            if (parent) {
                parent.classList.remove('touched');
            }
        });
    });
});

// Handle sticky search bar on scroll
function initStickySearch() {
    const header = document.getElementById('mainHeader');
    const heroSearch = document.getElementById('heroSearch');
    const heroSearchInput = document.getElementById('heroSearchInput');
    const headerSearchInput = document.getElementById('headerSearchInput');
    const headerSearchContainer = document.querySelector('.header-search-container');
    
    // If any required elements are missing, exit the function
    if (!header || !heroSearch || !heroSearchInput || !headerSearchInput || !headerSearchContainer) {
        return;
    }
    
    // Scroll threshold for showing the header search
    const scrollThreshold = 100;
    
    // Initially hide header search container
    headerSearchContainer.style.display = 'none';
    
    // Update search inputs to sync values
    function syncSearchInputs() {
        headerSearchInput.value = heroSearchInput.value;
    }
    
    heroSearchInput.addEventListener('input', syncSearchInputs);
    headerSearchInput.addEventListener('input', function() {
        heroSearchInput.value = headerSearchInput.value;
    });
    
    // Handle scroll event
    window.addEventListener('scroll', function() {
        if (window.scrollY > scrollThreshold) {
            // When scrolled down, show header search bar and hide hero search
            header.classList.add('scrolled');
            headerSearchContainer.style.display = 'flex';
            heroSearch.classList.add('hidden');
            syncSearchInputs();
        } else {
            // When scrolled to top, hide header search bar and show hero search
            header.classList.remove('scrolled');
            headerSearchContainer.style.display = 'none';
            heroSearch.classList.remove('hidden');
            // Make sure hero search input has the latest value
            heroSearchInput.value = headerSearchInput.value;
        }
    });
}

// Handle FAQ accordion functionality
document.addEventListener('DOMContentLoaded', function() {
    initFaqAccordion();
});

function initFaqAccordion() {
    console.log('FAQ accordion initialized');
    
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        
        // Set initial display state based on active class
        if (answer) {
            answer.style.display = item.classList.contains('active') ? 'block' : 'none';
        }
        
        question.addEventListener('click', () => {
            // Toggle active class on the clicked item
            const isActive = item.classList.contains('active');
            
            // First close all open items
            faqItems.forEach(otherItem => {
                if (otherItem !== item && otherItem.classList.contains('active')) {
                    otherItem.classList.remove('active');
                    const otherAnswer = otherItem.querySelector('.faq-answer');
                    if (otherAnswer) {
                        otherAnswer.style.display = 'none';
                    }
                }
            });
            
            // Then toggle the clicked item
            if (isActive) {
                item.classList.remove('active');
                if (answer) {
                    answer.style.display = 'none';
                }
            } else {
                item.classList.add('active');
                if (answer) {
                    answer.style.display = 'block';
                }
            }
            
            console.log('FAQ item clicked:', item.classList.contains('active'));
        });
    });
}
// Handle search functionality
function initSearch() {
    const searchBtns = document.querySelectorAll('.search-btn');
    
    searchBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const inputField = this.previousElementSibling;
            const searchTerm = inputField.value.trim();
            
            if (searchTerm !== '') {
                performSearch(searchTerm);
            } else {
                alert('Please enter a search term');
            }
        });
    });
    
    // Also trigger search on Enter key press
    const searchInputs = document.querySelectorAll('input[type="text"]');
    searchInputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const searchTerm = this.value.trim();
                if (searchTerm !== '') {
                    performSearch(searchTerm);
                } else {
                    alert('Please enter a search term');
                }
            }
        });
    });
}

// Simulate search functionality
function performSearch(term) {
    console.log(`Searching for: ${term}`);
    // In a real application, this would make an API call to search for the term
    alert(`Searching for: ${term}... \nThis would normally redirect to search results page.`);
}

// Handle location dropdown
function initLocationDropdown() {
    const locationBtns = document.querySelectorAll('.location-btn, .location-select');
    
    locationBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // This would normally open a location picker dropdown
            alert('Location picker would open here...');
        });
    });
}

// Handle footer toggle
function initFooterToggle() {
    const footerToggle = document.querySelector('.footer-toggle');
    const footerContent = document.querySelector('.footer-content');
    
    if (footerToggle && footerContent) {
        footerToggle.addEventListener('click', function() {
            footerContent.style.display = footerContent.style.display === 'none' ? 'grid' : 'none';
            
            // Toggle the icon
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-chevron-down');
                icon.classList.toggle('fa-chevron-up');
            }
        });
    }
}

// Counter animation for stats
document.addEventListener('DOMContentLoaded', function() {
    const counterElements = document.querySelectorAll('.counter-value');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const target = parseInt(element.getAttribute('data-target'));
                let count = 0;
                const duration = 2000; // 2 seconds
                const increment = Math.ceil(target / (duration / 30)); // Update every 30ms
                
                const timer = setInterval(() => {
                    count += increment;
                    if (count >= target) {
                        element.textContent = target;
                        clearInterval(timer);
                    } else {
                        element.textContent = count;
                    }
                }, 30);
                
                // Unobserve after animation starts
                observer.unobserve(element);
            }
        });
    }, { threshold: 0.5 });
    
    counterElements.forEach(counter => {
        observer.observe(counter);
    });
});

// Product related functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add to cart functionality
    const addButtons = document.querySelectorAll('.add-btn');
    
    addButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productCard = this.closest('.product-card');
            const productName = productCard.querySelector('h3').textContent;
            
            addToCart(productName);
        });
    });
});

// Simulate add to cart functionality
function addToCart(productName) {
    console.log(`Added to cart: ${productName}`);
    
    // Show a success message
    const message = document.createElement('div');
    message.className = 'cart-message';
    message.style.position = 'fixed';
    message.style.top = '20px';
    message.style.right = '20px';
    message.style.backgroundColor = 'var(--primary-green)';
    message.style.color = 'white';
    message.style.padding = '10px 20px';
    message.style.borderRadius = '4px';
    message.style.zIndex = '1000';
    message.textContent = `${productName} added to cart`;
    
    document.body.appendChild(message);
    
    // Remove the message after 3 seconds
    setTimeout(() => {
        message.style.opacity = '0';
        message.style.transition = 'opacity 0.5s';
        
        // Remove from DOM after fade out
        setTimeout(() => {
            document.body.removeChild(message);
        }, 500);
    }, 3000);
}

// Add smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
});

// Services slider functionality - removing this older implementation
function initServicesSlider() {
    // This implementation is being replaced with the newer carousel code below
    console.log("Using updated carousel implementation");
}

// This is our new horizontal carousel implementation
document.addEventListener('DOMContentLoaded', function() {
    // Initialize existing functions
    initFaqAccordion();
    initSearch();
    initLocationDropdown();
    initFooterToggle();
    initStickySearch();
    
    // Services carousel functionality - horizontal layout
    const carousel = document.querySelector('.carousel');
    const carouselInner = document.querySelector('.carousel-inner');
    const items = document.querySelectorAll('.service-item');
    const dots = document.querySelectorAll('.carousel-dot');
    const prevButton = document.querySelector('.prev-button');
    const nextButton = document.querySelector('.next-button');
    
    // If carousel elements don't exist, exit
    if (!carousel || !items.length) return;
    
    // Calculate item width including margins
    const getItemWidth = () => {
        const item = items[0];
        const style = window.getComputedStyle(item);
        const width = item.offsetWidth;
        const marginLeft = parseInt(style.marginLeft) || 0;
        const marginRight = parseInt(style.marginRight) || 0;
        return width + marginLeft + marginRight;
    };
    
    // Set the number of items visible based on screen width
    const getVisibleItems = () => {
        const viewportWidth = window.innerWidth;
        if (viewportWidth < 576) return 1;
        if (viewportWidth < 992) return 2;
        return 3;
    };
    
    let currentIndex = 0;
    const itemCount = items.length;
    
    // Update carousel position
    const updateCarousel = () => {
        const itemWidth = getItemWidth();
        const scrollPosition = currentIndex * itemWidth;
        
        // Use smooth scrolling
        carousel.scrollTo({
            left: scrollPosition,
            behavior: 'smooth'
        });
        
        // Update active dot
        dots.forEach((dot, index) => {
            if (index === currentIndex) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    };
    
    // Calculate max index based on visible items
    const getMaxIndex = () => {
        const visibleItems = getVisibleItems();
        return Math.max(0, items.length - visibleItems);
    };
    
    // Go to previous slide
    const goToPrev = () => {
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            // Loop to end
            currentIndex = getMaxIndex();
        }
        updateCarousel();
    };
    
    // Go to next slide
    const goToNext = () => {
        if (currentIndex < getMaxIndex()) {
            currentIndex++;
        } else {
            // Loop to beginning
            currentIndex = 0;
        }
        updateCarousel();
    };
    
    // Go to specific slide
    const goToSlide = (index) => {
        currentIndex = Math.min(Math.max(0, index), getMaxIndex());
        updateCarousel();
    };
    
    // Add event listeners
    if (prevButton) {
        prevButton.addEventListener('click', goToPrev);
    }
    
    if (nextButton) {
        nextButton.addEventListener('click', goToNext);
    }
    
    // Add click events to dots
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => goToSlide(index));
    });
    
    // Handle manual scroll on carousel
    let isScrolling;
    carousel.addEventListener('scroll', () => {
        window.clearTimeout(isScrolling);
        
        // Wait until scrolling stops before updating currentIndex
        isScrolling = setTimeout(() => {
            const itemWidth = getItemWidth();
            currentIndex = Math.round(carousel.scrollLeft / itemWidth);
            
            // Update dots after scrolling
            dots.forEach((dot, index) => {
                if (index === currentIndex) {
                    dot.classList.add('active');
                } else {
                    dot.classList.remove('active');
                }
            });
        }, 50);
    });
    
    // Auto slide functionality
    let autoSlideInterval;
    
    const startAutoSlide = () => {
        autoSlideInterval = setInterval(() => {
            goToNext();
        }, 5000);
    };
    
    const stopAutoSlide = () => {
        clearInterval(autoSlideInterval);
    };
    
    // Start auto slide
    startAutoSlide();
    
    // Pause on hover
    carousel.addEventListener('mouseenter', stopAutoSlide);
    carousel.addEventListener('mouseleave', startAutoSlide);
    
    // Handle window resize
    window.addEventListener('resize', () => {
        // Recalculate visible items and max index on resize
        const maxIndex = getMaxIndex();
        if (currentIndex > maxIndex) {
            currentIndex = maxIndex;
        }
        updateCarousel();
    });
    
    // Initialize carousel
    updateCarousel();
});

// Mobile menu toggle functionality
function initMobileMenu() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileNavOptions = document.querySelector('.mobile-nav-options');
    
    // The menu dropdown elements
    const menuContainer = document.getElementById('menuToggle');
    const menuDropdown = document.querySelector('.menu-dropdown');
    
    // Mobile bottom navigation
    const bottomNavItems = document.querySelectorAll('.bottom-nav-item');
    
    // Handle original mobile menu toggle
    if (mobileMenuToggle && mobileNavOptions) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileNavOptions.classList.toggle('active');
        });
        
        document.addEventListener('click', function(e) {
            if (!mobileMenuToggle.contains(e.target) && !mobileNavOptions.contains(e.target)) {
                mobileNavOptions.classList.remove('active');
            }
        });
    }
    
    // Handle menu dropdown
    if (menuContainer && menuDropdown) {
        // Toggle dropdown visibility when clicking on menu icon
        menuContainer.addEventListener('click', function(e) {
            e.stopPropagation();
            menuDropdown.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!menuContainer.contains(e.target)) {
                menuDropdown.classList.remove('active');
            }
        });
        
        // Add click handler for menu items
        const menuItems = menuDropdown.querySelectorAll('.menu-item');
        menuItems.forEach(item => {
            item.addEventListener('click', function() {
                menuDropdown.classList.remove('active');
                // Here you can add navigation logic based on which item was clicked
                console.log("Menu item clicked:", this.querySelector('span').textContent);
            });
        });
    }
    
    // Handle bottom navigation items
    if (bottomNavItems.length) {
        bottomNavItems.forEach(item => {
            item.addEventListener('click', function(e) {
                // Remove active class from all items
                bottomNavItems.forEach(navItem => navItem.classList.remove('active'));
                // Add active class to clicked item
                this.classList.add('active');
                
                // You can add navigation logic based on which item was clicked
                console.log("Bottom nav item clicked:", this.querySelector('span').textContent);
            });
        });
    }
}