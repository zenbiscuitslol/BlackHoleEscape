"use strict";

// Global state
let currentUser = null;
let userData = null;
let currentWeekOffset = 0;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    checkForCachedUser();
});

// Setup event listeners
function setupEventListeners() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    loginForm.addEventListener('submit', handleLogin);

    // Clear error when typing in input
    const intraLoginInput = document.getElementById('intraLogin');
    intraLoginInput.addEventListener('input', () => {
        if (intraLoginInput.classList.contains('error')) {
            hideLoginError();
        }
    });

    // Tab navigation
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', switchTab);
    });

    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    logoutBtn.addEventListener('click', logout);

    // Week navigation
    document.getElementById('prevWeek').addEventListener('click', () => {
        currentWeekOffset--;
        updateWeekDisplay();
    });

    document.getElementById('nextWeek').addEventListener('click', () => {
        currentWeekOffset++;
        updateWeekDisplay();
    });
}

// Check for cached user session
function checkForCachedUser() {
    const cached = sessionStorage.getItem('currentUser');
    if (cached) {
        currentUser = JSON.parse(cached);
        const cachedData = sessionStorage.getItem('userData');
        if (cachedData) {
            userData = JSON.parse(cachedData);
            showMainContent();
            populateUI();
        }
    }
}

// Handle login
async function handleLogin(e) {
    e.preventDefault();
    const intraLogin = document.getElementById('intraLogin').value.trim();
    
    if (!intraLogin) {
        showLoginError('Please enter your 42 intra login');
        return;
    }

    showLoadingSpinner(true);
    hideLoginError();

    try {
        const response = await fetch(`/api/escape/${encodeURIComponent(intraLogin)}`);
        
        // Handle HTTP errors from backend
        if (!response.ok) {
            showLoadingSpinner(false);
            
            if (response.status === 404) {
                showLoginError('❌ Invalid login. This user does not exist in the 42 database. Please try again.');
            } else if (response.status === 500) {
                showLoginError('❌ Server error. Please try again later.');
            } else {
                showLoginError('❌ Error fetching data. Please check your login and try again.');
            }
            return;
        }

        const apiResponse = await response.json();
        
        // Check if response contains an error field (shouldn't happen with 200 status, but just in case)
        if (apiResponse.error) {
            showLoadingSpinner(false);
            showLoginError(`❌ Invalid login: ${apiResponse.error}`);
            return;
        }

        // Validate that we have the expected data structure
        if (!apiResponse.status) {
            showLoadingSpinner(false);
            showLoginError('❌ Invalid response from server. Please try again.');
            return;
        }

        // Check if user is blackholed (warning but still allow access)
        if (apiResponse.status.is_blackholed) {
            showLoginError('⚠️ Warning: You are currently in the Black Hole. Please contact administration.');
        }

        userData = apiResponse;
        currentUser = intraLogin;

        // Cache in session storage
        sessionStorage.setItem('currentUser', JSON.stringify(currentUser));
        sessionStorage.setItem('userData', JSON.stringify(userData));

        // Clear any error messages
        hideLoginError();

        // Show main content with animation
        showMainContent();
        populateUI();
    } catch (error) {
        console.error('Login error:', error);
        showLoadingSpinner(false);
        showLoginError('❌ Network error. Please check your connection and try again.');
    }
}

// Show main content with smooth transition
function showMainContent() {
    const loginModal = document.getElementById('loginModal');
    const mainContainer = document.getElementById('mainContainer');

    loginModal.classList.remove('active');
    setTimeout(() => {
        loginModal.style.display = 'none';
        mainContainer.classList.remove('hidden');
    }, 300);
}

// Populate UI with user data
function populateUI() {
    if (!userData) return;

    // Extract status and escape plan from the nested structure
    const status = userData.status || {};
    const escapePlan = userData.escape_plan || {};

    // Update greeting
    const greeting = document.getElementById('userGreeting');
    const username = status.user_name || status.user_login || 'User';
    greeting.textContent = `Welcome, ${username}`;

    // Update status
    const statusEl = document.getElementById('userStatus');
    const daysLeft = status.days_until_blackhole || 0;
    if (daysLeft > 0) {
        statusEl.textContent = `You have ${daysLeft} days to escape the Black Hole`;
    } else if (status.is_blackholed) {
        statusEl.textContent = '⚠️ You are currently in the Black Hole';
    } else {
        statusEl.textContent = 'No Black Hole deadline - You are safe!';
    }

    // Update stats
    updateStats();
    updateRiskAnalysis();
    updateRecommendations();
    populateSchedule();
    populateProjects();

    showLoadingSpinner(false);
}

// Update statistics cards
function updateStats() {
    const status = userData.status || {};
    const escapePlan = userData.escape_plan || {};
    
    const level = status.level || status.user_level || 0;
    const daysRemaining = status.days_until_blackhole || 0;
    const circleInfo = status.circle_info?.circle_name || 'Unknown';
    const projectsRemaining = escapePlan.projects_remaining_current || 0;
    
    document.getElementById('userLevel').textContent = level.toFixed(1);
    document.getElementById('daysRemaining').textContent = Math.max(0, daysRemaining);
    document.getElementById('circleInfo').textContent = circleInfo;

    // Determine escape status based on actual data
    let status_text = 'At Risk';
    if (status.is_blackholed) {
        status_text = '🔴 In Black Hole';
    } else if (daysRemaining > 60) {
        status_text = '🟢 Safe';
    } else if (daysRemaining > 30) {
        status_text = '🟡 Caution';
    }
    
    const statusEl = document.getElementById('escapeStatus');
    statusEl.textContent = status_text;
}

// Update risk analysis
function updateRiskAnalysis() {
    const status = userData.status || {};
    const escapePlan = userData.escape_plan || {};
    
    // Ensure risk_level is a valid number between 0 and 1
    let riskLevel = parseFloat(status.risk_level);
    if (isNaN(riskLevel) || riskLevel === null || riskLevel === undefined) {
        riskLevel = 0.5; // Default to medium risk if invalid
    }
    riskLevel = Math.min(1, Math.max(0, riskLevel)); // Clamp to 0-1 range
    
    const daysLeft = status.days_until_blackhole || 0;
    const timelineFeasible = escapePlan.timeline_feasible || false;
    
    const riskFill = document.getElementById('riskFill');
    const riskLevelText = document.getElementById('riskLevel');
    const riskDescription = document.getElementById('riskDescription');

    // Set risk bar fill percentage (0-100)
    const riskPercentage = Math.min(100, Math.max(0, riskLevel * 100));
    riskFill.style.width = riskPercentage + '%';
    
    // Set risk bar color based on level
    if (riskPercentage > 70) {
        riskFill.style.background = 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)';
    } else if (riskPercentage > 40) {
        riskFill.style.background = 'linear-gradient(90deg, #facc15 0%, #eab308 100%)';
    } else {
        riskFill.style.background = 'linear-gradient(90deg, #4ade80 0%, #22c55e 100%)';
    }

    // Format risk level text
    let riskText = 'Low Risk';
    if (riskLevel > 0.7) riskText = 'High Risk';
    else if (riskLevel > 0.4) riskText = 'Medium Risk';
    riskLevelText.textContent = riskText + ` (${(riskLevel * 100).toFixed(0)}%)`;

    // Generate risk description based on actual data
    let description = '';
    
    if (status.is_blackholed) {
        description = '🔴 You are currently in the Black Hole. Contact administration immediately.';
    } else if (riskLevel > 0.8) {
        description = '⚠️ CRITICAL: Immediate action required. Focus urgently on completing projects.';
    } else if (riskLevel > 0.6) {
        description = '⚠️ HIGH RISK: Increase project work significantly. Consider adjusting your schedule.';
    } else if (riskLevel > 0.4) {
        description = '⏱️ MODERATE RISK: Maintain consistent work. Balance activities carefully.';
    } else {
        description = '✓ LOW RISK: On track. Continue at current pace while maintaining balance.';
    }
    
    if (!timelineFeasible && daysLeft > 0 && daysLeft < 30) {
        description += ' ⚡ Note: Current timeline may be tight.';
    }

    riskDescription.textContent = description;
}

// Update recommendations
function updateRecommendations() {
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';

    const recommendations = generateRecommendations();
    
    if (recommendations.length === 0) {
        recommendationsList.innerHTML = '<p class="loading-text">No recommendations at this time.</p>';
        return;
    }

    recommendations.forEach(rec => {
        const item = document.createElement('div');
        item.className = `recommendation-item ${rec.level}`;
        item.innerHTML = `<div class="recommendation-text">${rec.text}</div>`;
        recommendationsList.appendChild(item);
    });
}

// Generate recommendations based on user data
function generateRecommendations() {
    const status = userData.status || {};
    const escapePlan = userData.escape_plan || {};
    
    const recommendations = escapePlan.recommendations || [];
    const riskLevel = status.risk_level || 0;
    const daysLeft = status.days_until_blackhole || 0;
    const level = status.level || 0;

    // Use backend recommendations if available
    if (recommendations.length > 0) {
        return recommendations.map(rec => ({
            level: riskLevel > 0.6 ? 'danger' : (riskLevel > 0.3 ? 'warning' : 'info'),
            text: rec
        }));
    }

    // Fallback to generated recommendations
    const fallbackRecs = [];
    
    // Risk-based recommendations
    if (riskLevel > 0.8) {
        fallbackRecs.push({
            level: 'danger',
            text: '🚨 URGENT: Your risk level is critical. Prioritize project completion over all other activities.'
        });
        fallbackRecs.push({
            level: 'danger',
            text: '⏰ You have less than ' + daysLeft + ' days. Create a strict daily schedule focused on projects.'
        });
    } else if (riskLevel > 0.6) {
        fallbackRecs.push({
            level: 'warning',
            text: '🎯 Increase project work time by 20-30% this week to reduce risk.'
        });
        fallbackRecs.push({
            level: 'warning',
            text: '📋 Identify your top priority project and allocate dedicated focus time daily.'
        });
    }

    // Level-based recommendations
    if (level < 2) {
        fallbackRecs.push({
            level: 'info',
            text: '📚 Focus on fundamental projects. Build a strong foundation before moving to advanced work.'
        });
    } else if (level > 5) {
        fallbackRecs.push({
            level: 'info',
            text: '🏆 You\'re progressing well! Consider challenging projects to accelerate your growth.'
        });
    }

    // General wellness recommendations
    if (riskLevel < 0.5) {
        fallbackRecs.push({
            level: 'info',
            text: '✨ Maintain your current pace. Remember to take regular breaks for optimal productivity.'
        });
        fallbackRecs.push({
            level: 'info',
            text: '🤝 Connect with peers. Collaboration can enhance learning and provide support.'
        });
    }

    return fallbackRecs.slice(0, 5);
}

// Populate schedule table
function populateSchedule() {
    // Generate time slots (hourly from 00:00 to 24:00)
    const timeSlotContainer = document.getElementById('timeSlots');
    timeSlotContainer.innerHTML = '';
    
    for (let hour = 0; hour < 24; hour++) {
        const timeSlot = document.createElement('div');
        timeSlot.className = 'time-slot';
        const displayHour = hour.toString().padStart(2, '0');
        timeSlot.textContent = `${displayHour}:00`;
        timeSlotContainer.appendChild(timeSlot);
    }

    // Generate calendar view
    const daysContainer = document.getElementById('daysContainer');
    daysContainer.innerHTML = '';

    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    
    // Sample schedule data - 2-hour blocks per day
    const scheduleData = {
        0: [  // Monday
            { name: 'Study & Preparation', startHour: 6, endHour: 8, category: 'learning' },
            { name: 'Coding Session', startHour: 8, endHour: 10, category: 'coding' },
            { name: 'Coding Session', startHour: 10, endHour: 12, category: 'coding' },
            { name: 'Lunch Break', startHour: 12, endHour: 14, category: 'break' },
            { name: 'Project Work', startHour: 14, endHour: 16, category: 'coding' },
            { name: 'Exercise & Wellness', startHour: 16, endHour: 18, category: 'wellness' },
            { name: 'Evening Study', startHour: 18, endHour: 20, category: 'learning' },
            { name: 'Rest & Wind Down', startHour: 20, endHour: 22, category: 'wellness' }
        ],
        1: [  // Tuesday
            { name: 'Morning Coding', startHour: 6, endHour: 8, category: 'coding' },
            { name: 'Code Review', startHour: 8, endHour: 10, category: 'social' },
            { name: 'Pair Programming', startHour: 10, endHour: 12, category: 'coding' },
            { name: 'Lunch Break', startHour: 12, endHour: 14, category: 'break' },
            { name: 'Project Development', startHour: 14, endHour: 16, category: 'coding' },
            { name: 'Learning & Research', startHour: 16, endHour: 18, category: 'learning' },
            { name: 'Social Activities', startHour: 18, endHour: 20, category: 'social' },
            { name: 'Rest & Recovery', startHour: 20, endHour: 22, category: 'wellness' }
        ],
        2: [  // Wednesday
            { name: 'Coding Session', startHour: 6, endHour: 8, category: 'coding' },
            { name: 'Algorithm Study', startHour: 8, endHour: 10, category: 'learning' },
            { name: 'Project Work', startHour: 10, endHour: 12, category: 'coding' },
            { name: 'Lunch Break', startHour: 12, endHour: 14, category: 'break' },
            { name: 'Workshop & Training', startHour: 14, endHour: 16, category: 'learning' },
            { name: 'Development', startHour: 16, endHour: 18, category: 'coding' },
            { name: 'Community Events', startHour: 18, endHour: 20, category: 'social' },
            { name: 'Evening Relaxation', startHour: 20, endHour: 22, category: 'wellness' }
        ],
        3: [  // Thursday
            { name: 'Data Structures', startHour: 6, endHour: 8, category: 'learning' },
            { name: 'Coding Practice', startHour: 8, endHour: 10, category: 'coding' },
            { name: 'Problem Solving', startHour: 10, endHour: 12, category: 'coding' },
            { name: 'Lunch Break', startHour: 12, endHour: 14, category: 'break' },
            { name: 'Project Development', startHour: 14, endHour: 16, category: 'coding' },
            { name: 'Algorithm Optimization', startHour: 16, endHour: 18, category: 'learning' },
            { name: 'Social Time', startHour: 18, endHour: 20, category: 'social' },
            { name: 'Sleep Preparation', startHour: 20, endHour: 22, category: 'wellness' }
        ],
        4: [  // Friday
            { name: 'Final Push Coding', startHour: 6, endHour: 8, category: 'coding' },
            { name: 'Code Optimization', startHour: 8, endHour: 10, category: 'coding' },
            { name: 'Testing & Debug', startHour: 10, endHour: 12, category: 'coding' },
            { name: 'Lunch Break', startHour: 12, endHour: 14, category: 'break' },
            { name: 'Project Completion', startHour: 14, endHour: 16, category: 'coding' },
            { name: 'Team Collaboration', startHour: 16, endHour: 18, category: 'social' },
            { name: 'Weekend Prep', startHour: 18, endHour: 20, category: 'break' },
            { name: 'Social Celebration', startHour: 20, endHour: 22, category: 'social' }
        ],
        5: [  // Saturday
            { name: 'Morning Wellness', startHour: 8, endHour: 10, category: 'wellness' },
            { name: 'Physical Exercise', startHour: 10, endHour: 12, category: 'wellness' },
            { name: 'Social Brunch', startHour: 12, endHour: 14, category: 'social' },
            { name: 'Recreation Time', startHour: 14, endHour: 16, category: 'wellness' },
            { name: 'Learning & Hobby', startHour: 16, endHour: 18, category: 'learning' },
            { name: 'Entertainment', startHour: 18, endHour: 20, category: 'social' },
            { name: 'Relaxation', startHour: 20, endHour: 22, category: 'wellness' }
        ],
        6: [  // Sunday
            { name: 'Peaceful Morning', startHour: 8, endHour: 10, category: 'wellness' },
            { name: 'Meal Preparation', startHour: 10, endHour: 12, category: 'break' },
            { name: 'Personal Time', startHour: 12, endHour: 14, category: 'wellness' },
            { name: 'Week Planning', startHour: 14, endHour: 16, category: 'learning' },
            { name: 'Reflection Study', startHour: 16, endHour: 18, category: 'learning' },
            { name: 'Social Connection', startHour: 18, endHour: 20, category: 'social' },
            { name: 'Sleep Preparation', startHour: 20, endHour: 22, category: 'wellness' }
        ]
    };

    days.forEach((dayShort, dayIndex) => {
        const dayColumn = document.createElement('div');
        dayColumn.className = 'day-column';

        // Day header
        const dayHeader = document.createElement('div');
        dayHeader.className = 'day-header';
        dayHeader.innerHTML = `<div class="day-label">${dayShort}</div>`;
        dayColumn.appendChild(dayHeader);

        // Day timeline container
        const timeline = document.createElement('div');
        timeline.className = 'day-timeline';

        // Add 24 hour slots
        for (let hour = 0; hour < 24; hour++) {
            const hourBlock = document.createElement('div');
            hourBlock.className = 'hour-block';
            timeline.appendChild(hourBlock);
        }

        // Add events to the timeline
        const events = scheduleData[dayIndex] || [];
        events.forEach(event => {
            const eventEl = document.createElement('div');
            eventEl.className = `calendar-event ${event.category}`;
            
            // Calculate position and height
            const startPercent = (event.startHour / 24) * 100;
            const durationHours = event.endHour - event.startHour;
            const heightPercent = (durationHours / 24) * 100;
            
            eventEl.style.top = startPercent + '%';
            eventEl.style.height = heightPercent + '%';
            
            eventEl.innerHTML = `
                <div class="event-content">
                    <div class="event-time">${event.startHour.toString().padStart(2, '0')}:00 - ${event.endHour.toString().padStart(2, '0')}:00</div>
                    <div class="event-title">${event.name}</div>
                </div>
            `;
            
            timeline.appendChild(eventEl);
        });

        dayColumn.appendChild(timeline);
        daysContainer.appendChild(dayColumn);
    });

    updateWeekDisplay();
}

// Update week display
function updateWeekDisplay() {
    const today = new Date();
    const weekDate = new Date(today);
    weekDate.setDate(today.getDate() + currentWeekOffset * 7);
    
    const weekStart = new Date(weekDate);
    const day = weekStart.getDay();
    const diff = weekStart.getDate() - day + (day === 0 ? -6 : 1);
    weekStart.setDate(diff);

    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6);

    const options = { month: 'short', day: 'numeric' };
    const startStr = weekStart.toLocaleDateString('en-US', options);
    const endStr = weekEnd.toLocaleDateString('en-US', options);

    document.getElementById('weekDisplay').textContent = `${startStr} - ${endStr}`;
}

// Populate projects list
function populateProjects() {
    const projectsGrid = document.getElementById('projectsGrid');
    projectsGrid.innerHTML = '';

    // Get projects from backend escape plan or create default list
    const escapePlan = userData.escape_plan || {};
    const priorityProjects = escapePlan.priority_projects || [];
    const remainingProjects = escapePlan.projects_remaining_current || 0;
    
    let projects = [];
    
    // Try to get projects from backend first
    if (priorityProjects.length > 0) {
        projects = priorityProjects.map((name, idx) => ({
            name: name,
            description: `Priority project ${idx + 1} - Focus on completing this`,
            status: idx < remainingProjects ? 'pending' : 'completed',
            level: 'Beginner',
            duration: '2-3 weeks'
        }));
    }
    
    // Fallback to default list if no backend projects
    if (projects.length === 0) {
        projects = [
            {
                name: 'Libft',
                description: 'Your first C library - foundation of everything',
                status: 'completed'
            },
            {
                name: 'Get Next Line',
                description: 'Read file line by line - core utility skill',
                status: 'completed'
            },
            {
                name: 'Printf',
                description: 'Recreate printf function - string and formatting mastery',
                status: 'in-progress'
            },
            {
                name: 'Born2Beroot',
                description: 'Virtual machine and system administration basics',
                status: 'pending'
            },
            {
                name: 'Minishell',
                description: 'Build a shell - understand process and system calls',
                status: 'pending'
            },
            {
                name: 'Philosophers',
                description: 'Threading and synchronization - advanced concepts',
                status: 'pending'
            }
        ];
    }

    projects.forEach((project, index) => {
        const card = document.createElement('div');
        card.className = 'project-card';
        
        let statusClass = 'pending';
        let statusText = 'Pending';
        if (project.status === 'completed') {
            statusClass = 'completed';
            statusText = 'Completed ✓';
        } else if (project.status === 'in-progress') {
            statusClass = 'in-progress';
            statusText = 'In Progress';
        }

        card.innerHTML = `
            <div class="project-status ${statusClass}">${statusText}</div>
            <h3>${project.name || 'Project ' + (index + 1)}</h3>
            <p class="project-description">${project.description || 'Important project to master'}</p>
            <div class="project-meta">
                <span>📚 Level: ${project.level || 'Beginner'}</span>
                <span>⏱️ Duration: ${project.duration || '2-3 weeks'}</span>
            </div>
        `;

        projectsGrid.appendChild(card);
    });
}

// Switch between tabs
function switchTab(e) {
    const tabBtn = e.target.closest('.tab-btn');
    if (!tabBtn) return;

    // Remove active class from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    // Add active class to clicked tab
    tabBtn.classList.add('active');
    const tabName = tabBtn.dataset.tab;
    const tabContent = document.getElementById(tabName);
    if (tabContent) {
        tabContent.classList.add('active');
    }
}

// Show/hide loading spinner
function showLoadingSpinner(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (show) {
        spinner.style.display = 'flex';
    } else {
        spinner.style.display = 'none';
    }
}

// Interactive background animation with mouse tracking
let mouseX = window.innerWidth / 2;
let mouseY = window.innerHeight / 2;
let targetX = mouseX;
let targetY = mouseY;

document.addEventListener('mousemove', (e) => {
    targetX = e.clientX;
    targetY = e.clientY;
});

function animateBackgroundGradient() {
    // Smooth interpolation for smoother animation
    mouseX += (targetX - mouseX) * 0.05;
    mouseY += (targetY - mouseY) * 0.05;

    const bg = document.querySelector('.background-animation');
    if (bg) {
        const xPercent = (mouseX / window.innerWidth) * 100;
        const yPercent = (mouseY / window.innerHeight) * 100;

        // Create interactive gradient that follows cursor - increased by 150%
        const gradient = `
            radial-gradient(circle at ${xPercent}% ${yPercent}%, rgba(255, 255, 255, 0.2) 0%, transparent 25%),
            radial-gradient(circle at ${100 - xPercent}% ${100 - yPercent}%, rgba(255, 255, 255, 0.125) 0%, transparent 25%),
            radial-gradient(circle at ${xPercent}% ${100 - yPercent}%, rgba(255, 255, 255, 0.1) 0%, transparent 30%),
            linear-gradient(180deg, #000000 0%, #0a0a0a 50%, #000000 100%)
        `;
        bg.style.background = gradient;
    }

    requestAnimationFrame(animateBackgroundGradient);
}

// Start the background animation
animateBackgroundGradient();

// Show login error
function showLoginError(message) {
    const errorEl = document.getElementById('loginError');
    const inputEl = document.getElementById('intraLogin');
    
    errorEl.textContent = message;
    errorEl.classList.add('show');
    inputEl.classList.add('error');
}

// Hide login error
function hideLoginError() {
    const errorEl = document.getElementById('loginError');
    const inputEl = document.getElementById('intraLogin');
    
    errorEl.textContent = '';
    errorEl.classList.remove('show');
    inputEl.classList.remove('error');
}

// Logout function
function logout() {
    currentUser = null;
    userData = null;
    currentWeekOffset = 0;

    // Clear session storage
    sessionStorage.removeItem('currentUser');
    sessionStorage.removeItem('userData');

    // Reset form
    document.getElementById('intraLogin').value = '';
    hideLoginError();

    // Smooth transition to login modal
    const loginModal = document.getElementById('loginModal');
    const mainContainer = document.getElementById('mainContainer');

    // Fade out main container
    mainContainer.style.opacity = '0';
    mainContainer.style.transition = 'opacity 0.5s ease-out';
    
    // After fade out, hide and show login
    setTimeout(() => {
        mainContainer.classList.add('hidden');
        mainContainer.style.opacity = '1';
        mainContainer.style.transition = '';
        
        loginModal.style.display = 'flex';
        loginModal.classList.add('active');
    }, 500);
}
