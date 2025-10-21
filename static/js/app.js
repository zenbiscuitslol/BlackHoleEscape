"use strict";

document.getElementById("loginGo").addEventListener("click", async () => {
  const login = document.getElementById("loginInputMain").value.trim();
  if (!login) {
    alert("Please enter your intra name!");
    return;
  }

  const res = await fetch(`/api/escape/${encodeURIComponent(login)}`);
  if (!res.ok) {
    document.getElementById("apiOut").textContent = "Error fetching data!";
    return;
  }
  const json = await res.json();
  document.getElementById("apiOut").textContent = JSON.stringify(json, null, 2);
});

// (Optional) allow Enter key to submit
document.getElementById("loginInputMain").addEventListener("keydown", (e) => {
  if (e.key === "Enter") document.getElementById("loginGo").click();
});

document.addEventListener("DOMContentLoaded", function() {
  // Week navigation
  const weekDisplay = document.getElementById("current-week");
  const prevWeekBtn = document.getElementById("prev-week");
  const nextWeekBtn = document.getElementById("next-week");

  let currentWeek = 0;

  function updateWeekDisplay() {
    const baseDate = new Date();
    baseDate.setDate(baseDate.getDate() + currentWeek * 7);

    const startOfWeek = new Date(baseDate);
    startOfWeek.setDate(baseDate.getDate() - baseDate.getDay() + 1);

    const options = { month: "long", day: "numeric", year: "numeric" };
    weekDisplay.textContent = `Week of ${startOfWeek.toLocaleDateString("en-US", options)}`;
  }

  prevWeekBtn.addEventListener("click", function() {
    currentWeek--;
    updateWeekDisplay();
  });

  nextWeekBtn.addEventListener("click", function() {
    currentWeek++;
    updateWeekDisplay();
  });

  // Initialize week display
  updateWeekDisplay();

  // Default schedule data
  const defaultSchedule = {
    studentName: "",
    focusArea: "coding",
    currentProject: "",
    sleepPattern: "balanced",
    socialPreference: "medium",
    exerciseFrequency: "3-4-times",
    breakStyle: "pomodoro",
    studyEnvironment: "campus",
    suggestionsPreference: "moderate",
    timeSlots: [
      {
        time: "7:00 - 8:00",
        days: [
          { type: "wellness", text: "Morning Exercise & Breakfast", suggested: false },
          { type: "wellness", text: "Morning Exercise & Breakfast", suggested: false },
          { type: "wellness", text: "Morning Exercise & Breakfast", suggested: false },
          { type: "wellness", text: "Morning Exercise & Breakfast", suggested: false },
          { type: "wellness", text: "Morning Exercise & Breakfast", suggested: false },
          { type: "wellness", text: "Sleep In & Light Breakfast", suggested: false },
          { type: "wellness", text: "Sleep In & Light Breakfast", suggested: false },
        ],
      },
      {
        time: "8:00 - 10:00",
        days: [
          { type: "coding", text: "Project Work Session 1", suggested: false },
          { type: "coding", text: "Project Work Session 1", suggested: false },
          { type: "coding", text: "Project Work Session 1", suggested: false },
          { type: "coding", text: "Project Work Session 1", suggested: false },
          { type: "coding", text: "Project Work Session 1", suggested: false },
          { type: "wellness", text: "Outdoor Activity", suggested: true },
          { type: "wellness", text: "Personal Time", suggested: false },
        ],
      },
      {
        time: "10:00 - 10:30",
        days: [
          { type: "break", text: "Coffee Break & Snack", suggested: false },
          { type: "break", text: "Coffee Break & Snack", suggested: false },
          { type: "break", text: "Coffee Break & Snack", suggested: false },
          { type: "break", text: "Coffee Break & Snack", suggested: false },
          { type: "break", text: "Coffee Break & Snack", suggested: false },
          { type: "break", text: "Coffee & Relax", suggested: false },
          { type: "break", text: "Coffee & Relax", suggested: false },
        ],
      },
      {
        time: "10:30 - 12:30",
        days: [
          { type: "coding", text: "Project Work Session 2", suggested: false },
          { type: "coding", text: "Project Work Session 2", suggested: false },
          { type: "learning", text: "Peer Learning Session", suggested: true },
          { type: "coding", text: "Project Work Session 2", suggested: false },
          { type: "coding", text: "Project Work Session 2", suggested: false },
          { type: "social", text: "Social Activity", suggested: true },
          { type: "learning", text: "Skill Development", suggested: false },
        ],
      },
      {
        time: "12:30 - 13:30",
        days: [
          { type: "break", text: "Lunch Break", suggested: false },
          { type: "break", text: "Lunch Break", suggested: false },
          { type: "break", text: "Lunch Break", suggested: false },
          { type: "break", text: "Lunch Break", suggested: false },
          { type: "break", text: "Lunch Break", suggested: false },
          { type: "break", text: "Lunch Out", suggested: true },
          { type: "break", text: "Lunch & Relax", suggested: false },
        ],
      },
      {
        time: "13:30 - 15:30",
        days: [
          { type: "coding", text: "Project Work Session 3", suggested: false },
          { type: "coding", text: "Project Work Session 3", suggested: false },
          { type: "coding", text: "Project Work Session 3", suggested: false },
          { type: "coding", text: "Project Work Session 3", suggested: false },
          { type: "coding", text: "Project Work Session 3", suggested: false },
          { type: "social", text: "Explore Heilbronn", suggested: true },
          { type: "learning", text: "Online Course", suggested: false },
        ],
      },
      {
        time: "15:30 - 16:00",
        days: [
          { type: "break", text: "Afternoon Break", suggested: false },
          { type: "break", text: "Afternoon Break", suggested: false },
          { type: "break", text: "Afternoon Break", suggested: false },
          { type: "break", text: "Afternoon Break", suggested: false },
          { type: "break", text: "Afternoon Break", suggested: false },
          { type: "break", text: "Snack Break", suggested: false },
          { type: "break", text: "Snack Break", suggested: false },
        ],
      },
      {
        time: "16:00 - 18:00",
        days: [
          { type: "learning", text: "Code Review & Debugging", suggested: false },
          { type: "learning", text: "New Technology Exploration", suggested: true },
          { type: "social", text: "Peer Programming", suggested: true },
          { type: "learning", text: "Algorithm Practice", suggested: false },
          { type: "social", text: "Project Collaboration", suggested: true },
          { type: "wellness", text: "Fitness & Exercise", suggested: false },
          { type: "wellness", text: "Meditation & Reflection", suggested: true },
        ],
      },
      {
        time: "18:00 - 19:30",
        days: [
          { type: "break", text: "Dinner Break", suggested: false },
          { type: "break", text: "Dinner Break", suggested: false },
          { type: "break", text: "Dinner Break", suggested: false },
          { type: "break", text: "Dinner Break", suggested: false },
          { type: "social", text: "Social Dinner", suggested: true },
          { type: "social", text: "Dinner with Friends", suggested: true },
          { type: "break", text: "Dinner & Plan Week", suggested: false },
        ],
      },
      {
        time: "19:30 - 21:00",
        days: [
          { type: "learning", text: "Light Study Session", suggested: false },
          { type: "learning", text: "Light Study Session", suggested: false },
          { type: "social", text: "42 Events/Workshops", suggested: true },
          { type: "learning", text: "Light Study Session", suggested: false },
          { type: "social", text: "Movie/Games Night", suggested: true },
          { type: "social", text: "Evening Social", suggested: true },
          { type: "learning", text: "Weekly Review", suggested: false },
        ],
      },
      {
        time: "21:00 - 22:30",
        days: [
          { type: "wellness", text: "Wind Down & Relax", suggested: false },
          { type: "wellness", text: "Wind Down & Relax", suggested: false },
          { type: "wellness", text: "Wind Down & Relax", suggested: false },
          { type: "wellness", text: "Wind Down & Relax", suggested: false },
          { type: "social", text: "Social Time", suggested: true },
          { type: "social", text: "Social Time", suggested: true },
          { type: "wellness", text: "Prepare for Week", suggested: false },
        ],
      },
    ],
    suggestions: [
      { text: "Add a 15-minute walk after lunch to improve digestion and focus", accepted: false },
      { text: "Schedule a peer programming session on Wednesday afternoon", accepted: false },
      { text: "Try the 52/17 work-break pattern for better productivity", accepted: false },
    ],
  };

  // Load schedule from localStorage or use default
  let currentSchedule = JSON.parse(localStorage.getItem("blackHoleSchedule")) || defaultSchedule;

  // Enhanced AI Suggestion Engine
  class PersonalizedAISuggestions {
    constructor(userProfile, scheduleData) {
      this.userProfile = userProfile;
      this.scheduleData = scheduleData;
    }

    generatePersonalizedSuggestions() {
      const suggestions = [];
      const analysis = this.analyzeSchedule();

      suggestions.push(...this.generateCodingSuggestions(analysis));
      suggestions.push(...this.generateWellnessSuggestions(analysis));
      suggestions.push(...this.generateSocialSuggestions(analysis));
      suggestions.push(...this.generateProductivitySuggestions(analysis));
      suggestions.push(...this.generateGoalBasedSuggestions(analysis));

      return this.filterSuggestions(suggestions);
    }

    analyzeSchedule() {
      const analysis = {
        codingHours: 0,
        breakHours: 0,
        socialHours: 0,
        learningHours: 0,
        wellnessHours: 0,
        consecutiveCoding: 0,
        maxConsecutiveCoding: 0,
        lateNightSessions: 0,
        mealConsistency: 0,
      };

      let currentConsecutive = 0;

      this.scheduleData.timeSlots.forEach(slot => {
        const duration = this.getSlotDuration(slot.time);

        slot.days.forEach(day => {
          switch (day.type) {
            case "coding":
              analysis.codingHours += duration;
              currentConsecutive++;
              analysis.maxConsecutiveCoding = Math.max(analysis.maxConsecutiveCoding, currentConsecutive);
              break;
            case "break":
              analysis.breakHours += duration;
              currentConsecutive = 0;
              if (this.isMealSlot(slot.time)) analysis.mealConsistency++;
              break;
            case "social":
              analysis.socialHours += duration;
              currentConsecutive = 0;
              break;
            case "learning":
              analysis.learningHours += duration;
              currentConsecutive = 0;
              break;
            case "wellness":
              analysis.wellnessHours += duration;
              currentConsecutive = 0;
              break;
          }

          if (this.isLateNightSlot(slot.time) && day.type === "coding") {
            analysis.lateNightSessions++;
          }
        });
      });

      analysis.balanceScore = this.calculateBalanceScore(analysis);
      return analysis;
    }

    generateCodingSuggestions(analysis) {
      const suggestions = [];
      const userFocus = this.userProfile.focusArea;
      const currentProject = this.userProfile.currentProject;

      if (analysis.maxConsecutiveCoding > 3) {
        suggestions.push({
          text:
            `You have ${analysis.maxConsecutiveCoding} consecutive coding sessions. Add more breaks to maintain focus.`,
          priority: "high",
          category: "productivity",
        });
      }

      if (analysis.codingHours > 35) {
        suggestions.push({
          text: `You're scheduling ${
            analysis.codingHours.toFixed(1)
          } coding hours. That's intensive! Balance with adequate rest.`,
          priority: "medium",
          category: "wellness",
        });
      }

      if (analysis.lateNightSessions > 2) {
        suggestions.push({
          text:
            `You have ${analysis.lateNightSessions} late-night coding sessions. Move these to daytime for better sleep.`,
          priority: "high",
          category: "wellness",
        });
      }

      if (currentProject && userFocus === "web-dev") {
        suggestions.push({
          text: `For ${currentProject}, schedule frontend/backend separation days to maintain context.`,
          priority: "low",
          category: "coding",
        });
      }

      return suggestions;
    }

    generateWellnessSuggestions(analysis) {
      const suggestions = [];
      const sleepPattern = this.userProfile.sleepPattern;
      const exerciseFreq = this.userProfile.exerciseFrequency;

      if (analysis.mealConsistency < 10) {
        suggestions.push({
          text: `You're missing ${
            14 - analysis.mealConsistency
          } scheduled meals. Consistent nutrition is key for energy.`,
          priority: "medium",
          category: "wellness",
        });
      }

      if (analysis.wellnessHours < 5) {
        suggestions.push({
          text: `Add more wellness activities. You have only ${analysis.wellnessHours.toFixed(1)} hours scheduled.`,
          priority: "medium",
          category: "wellness",
        });
      }

      if (sleepPattern === "night-owl" && analysis.lateNightSessions > 3) {
        suggestions.push({
          text: "As a night owl with many late sessions, maintain consistent wake-up times.",
          priority: "medium",
          category: "wellness",
        });
      }

      return suggestions;
    }

    generateSocialSuggestions(analysis) {
      const suggestions = [];
      const socialPref = this.userProfile.socialPreference;

      if (socialPref === "low" && analysis.socialHours < 2) {
        suggestions.push({
          text: "Even with low social preference, schedule 2-3 hours weekly for mental health.",
          priority: "low",
          category: "social",
        });
      }

      if (socialPref === "high" && analysis.socialHours < 8) {
        suggestions.push({
          text: `You prefer high social activity but only have ${analysis.socialHours.toFixed(1)} hours scheduled.`,
          priority: "medium",
          category: "social",
        });
      }

      return suggestions;
    }

    generateProductivitySuggestions(analysis) {
      const suggestions = [];
      const breakStyle = this.userProfile.breakStyle;

      if (analysis.breakHours < 10 && analysis.codingHours > 20) {
        suggestions.push({
          text: `High coding (${analysis.codingHours.toFixed(1)}h) with low breaks (${
            analysis.breakHours.toFixed(1)
          }h). Try the 52/17 rule.`,
          priority: "high",
          category: "productivity",
        });
      }

      if (breakStyle === "pomodoro" && analysis.maxConsecutiveCoding > 4) {
        suggestions.push({
          text: "You use Pomodoro but have long coding blocks. Maintain 25-minute focused sessions.",
          priority: "medium",
          category: "productivity",
        });
      }

      return suggestions;
    }

    generateGoalBasedSuggestions(analysis) {
      const suggestions = [];
      const focusArea = this.userProfile.focusArea;

      switch (focusArea) {
        case "web-dev":
          suggestions.push({
            text: "For web development, schedule design review sessions separate from coding.",
            priority: "low",
            category: "learning",
          });
          break;
        case "algorithms":
          suggestions.push({
            text: "Algorithm practice is most effective in daily 1-2 hour sessions.",
            priority: "medium",
            category: "learning",
          });
          break;
        case "ai-ml":
          suggestions.push({
            text: "Schedule separate blocks for AI/ML implementation vs. research.",
            priority: "medium",
            category: "learning",
          });
          break;
      }

      if (analysis.balanceScore < 0.6) {
        suggestions.push({
          text: `Your balance score is low (${
            (analysis.balanceScore * 100).toFixed(0)
          }%). Distribute activities more evenly.`,
          priority: "high",
          category: "wellness",
        });
      }

      return suggestions;
    }

    filterSuggestions(suggestions) {
      const uniqueSuggestions = suggestions.filter((s, i, self) => i === self.findIndex(t => t.text === s.text));

      uniqueSuggestions.sort((a, b) => {
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      });

      return uniqueSuggestions.slice(0, 5);
    }

    getSlotDuration(timeString) {
      const [start, end] = timeString.split(" - ");
      const startTime = this.parseTime(start);
      const endTime = this.parseTime(end);
      return (endTime - startTime) / (1000 * 60 * 60);
    }

    parseTime(timeString) {
      const time = timeString.trim();
      let [hours, minutes] = time.split(":").map(Number);
      return new Date().setHours(hours, minutes || 0, 0, 0);
    }

    isLateNightSlot(timeString) {
      const [start] = timeString.split(" - ");
      const time = this.parseTime(start);
      const hours = new Date(time).getHours();
      return hours >= 22 || hours <= 2;
    }

    isMealSlot(timeString) {
      const mealTimes = ["7:00", "8:00", "12:00", "13:00", "18:00", "19:00"];
      return mealTimes.some(mealTime => timeString.includes(mealTime));
    }

    calculateBalanceScore(analysis) {
      const totalHours = analysis.codingHours + analysis.breakHours + analysis.socialHours
        + analysis.learningHours + analysis.wellnessHours;

      if (totalHours === 0) return 0;

      const idealRatios = {
        coding: 0.4,
        break: 0.2,
        social: 0.15,
        learning: 0.15,
        wellness: 0.1,
      };

      const actualRatios = {
        coding: analysis.codingHours / totalHours,
        break: analysis.breakHours / totalHours,
        social: analysis.socialHours / totalHours,
        learning: analysis.learningHours / totalHours,
        wellness: analysis.wellnessHours / totalHours,
      };

      let similarity = 0;
      for (const category in idealRatios) {
        similarity += 1 - Math.abs(idealRatios[category] - actualRatios[category]);
      }

      return similarity / Object.keys(idealRatios).length;
    }
  }

  // Enhanced AI recommendation function
  function updateAIRecommendation() {
    const aiEngine = new PersonalizedAISuggestions(currentSchedule, currentSchedule);
    const analysis = aiEngine.analyzeSchedule();

    let recommendation = "";
    const userName = currentSchedule.studentName ? ` ${currentSchedule.studentName}` : "";

    if (analysis.balanceScore < 0.5) {
      recommendation = `Hi${userName}! Your schedule shows significant imbalance. `;

      if (analysis.codingHours > analysis.socialHours * 3) {
        recommendation += "You're heavily focused on coding with minimal social time. ";
      }

      if (analysis.consecutiveCoding > 4) {
        recommendation += "Long coding sessions without breaks can lead to burnout. ";
      }

      recommendation += "Try distributing activities more evenly throughout your week.";
    } else if (analysis.balanceScore > 0.8) {
      recommendation =
        `Excellent balance${userName}! Your schedule shows great distribution between work, breaks, and wellness. Keep maintaining this healthy routine!`;
    } else {
      recommendation = `Good schedule structure${userName}! `;

      if (currentSchedule.focusArea === "web-dev") {
        recommendation +=
          "As a web development student, consider scheduling design review sessions separately from coding.";
      } else if (currentSchedule.focusArea === "algorithms") {
        recommendation +=
          "For algorithm practice, daily shorter sessions are more effective than occasional long ones.";
      } else {
        recommendation += "Check the suggestions panel for personalized tips to optimize your schedule.";
      }
    }

    document.getElementById("ai-recommendation").textContent = recommendation;
  }

  // Function to generate personalized suggestions
  function generatePersonalizedSuggestions() {
    const aiEngine = new PersonalizedAISuggestions(currentSchedule, currentSchedule);
    const personalizedSuggestions = aiEngine.generatePersonalizedSuggestions();

    // Convert to the format expected by our system
    currentSchedule.suggestions = personalizedSuggestions.map(suggestion => ({
      text: suggestion.text,
      accepted: false,
    }));

    populateSuggestionsList();
    updateAIRecommendation();
  }

  // Populate the timetable with schedule data
  function populateTimetable() {
    const tbody = document.querySelector("#schedule-table tbody");
    tbody.innerHTML = "";

    currentSchedule.timeSlots.forEach(slot => {
      const row = document.createElement("tr");

      // Time header cell
      const timeCell = document.createElement("td");
      timeCell.className = "time-header";
      timeCell.textContent = slot.time;
      row.appendChild(timeCell);

      // Day cells
      slot.days.forEach(day => {
        const dayCell = document.createElement("td");
        const activityDiv = document.createElement("div");
        activityDiv.className = `activity ${day.type}`;
        activityDiv.textContent = day.text;
        activityDiv.dataset.type = day.type;

        // Add suggestion indicator if this is a suggested activity
        if (day.suggested) {
          const indicator = document.createElement("div");
          indicator.className = "suggestion-indicator";
          activityDiv.appendChild(indicator);
        }

        dayCell.appendChild(activityDiv);
        row.appendChild(dayCell);
      });

      tbody.appendChild(row);
    });

    // Populate suggestions list
    populateSuggestionsList();

    // Update AI recommendation
    updateAIRecommendation();
  }

  // Populate suggestions list
  function populateSuggestionsList() {
    const suggestionsList = document.getElementById("suggestions-list");
    suggestionsList.innerHTML = "";

    currentSchedule.suggestions.forEach((suggestion, index) => {
      if (!suggestion.accepted) {
        const suggestionItem = document.createElement("div");
        suggestionItem.className = "suggestion-item";

        const suggestionText = document.createElement("div");
        suggestionText.className = "suggestion-text";
        suggestionText.textContent = suggestion.text;

        const suggestionActions = document.createElement("div");
        suggestionActions.className = "suggestion-actions";

        const acceptBtn = document.createElement("button");
        acceptBtn.className = "suggestion-btn accept";
        acceptBtn.innerHTML = "<i class=\"fas fa-check\"></i>";
        acceptBtn.title = "Accept suggestion";
        acceptBtn.addEventListener("click", function() {
          acceptSuggestion(index);
        });

        const ignoreBtn = document.createElement("button");
        ignoreBtn.className = "suggestion-btn ignore";
        ignoreBtn.innerHTML = "<i class=\"fas fa-times\"></i>";
        ignoreBtn.title = "Ignore suggestion";
        ignoreBtn.addEventListener("click", function() {
          ignoreSuggestion(index);
        });

        suggestionActions.appendChild(acceptBtn);
        suggestionActions.appendChild(ignoreBtn);

        suggestionItem.appendChild(suggestionText);
        suggestionItem.appendChild(suggestionActions);

        suggestionsList.appendChild(suggestionItem);
      }
    });

    // If no suggestions, show a message
    if (suggestionsList.children.length === 0) {
      suggestionsList.innerHTML =
        "<p style=\"text-align: center; color: #adb5bd; padding: 20px;\">No active suggestions. Your schedule looks great!</p>";
    }
  }

  // Accept a suggestion
  function acceptSuggestion(index) {
    currentSchedule.suggestions[index].accepted = true;
    localStorage.setItem("blackHoleSchedule", JSON.stringify(currentSchedule));
    populateSuggestionsList();

    // In a real app, we would implement the suggestion here
    alert("Suggestion accepted! We would implement this change in your schedule.");
  }

  // Ignore a suggestion
  function ignoreSuggestion(index) {
    currentSchedule.suggestions.splice(index, 1);
    localStorage.setItem("blackHoleSchedule", JSON.stringify(currentSchedule));
    populateSuggestionsList();
  }

  // Populate the customization form
  function populateCustomizationForm() {
    document.getElementById("student-name").value = currentSchedule.studentName;
    document.getElementById("focus-area").value = currentSchedule.focusArea;
    document.getElementById("current-project").value = currentSchedule.currentProject;
    document.getElementById("sleep-pattern").value = currentSchedule.sleepPattern;
    document.getElementById("social-preference").value = currentSchedule.socialPreference;
    document.getElementById("exercise-frequency").value = currentSchedule.exerciseFrequency;
    document.getElementById("break-style").value = currentSchedule.breakStyle;
    document.getElementById("study-environment").value = currentSchedule.studyEnvironment;
    document.getElementById("suggestions-preference").value = currentSchedule.suggestionsPreference;

    const timeSlotsContainer = document.getElementById("time-slots-container");
    timeSlotsContainer.innerHTML = "";

    currentSchedule.timeSlots.forEach((slot, slotIndex) => {
      const timeSlotDiv = document.createElement("div");
      timeSlotDiv.className = "time-slot";

      // Time label
      const timeLabel = document.createElement("div");
      timeLabel.className = "time-label";
      timeLabel.textContent = slot.time;
      timeSlotDiv.appendChild(timeLabel);

      // Day inputs
      slot.days.forEach((day, dayIndex) => {
        const select = document.createElement("select");
        select.className = "activity-edit";
        select.dataset.slotIndex = slotIndex;
        select.dataset.dayIndex = dayIndex;

        const options = [
          { value: "coding", text: "Coding" },
          { value: "break", text: "Break" },
          { value: "social", text: "Social" },
          { value: "learning", text: "Learning" },
          { value: "wellness", text: "Wellness" },
        ];

        options.forEach(option => {
          const optionElement = document.createElement("option");
          optionElement.value = option.value;
          optionElement.textContent = option.text;
          optionElement.selected = day.type === option.value;
          select.appendChild(optionElement);
        });

        timeSlotDiv.appendChild(select);
      });

      timeSlotsContainer.appendChild(timeSlotDiv);
    });
  }

  // Modal functionality
  const modal = document.getElementById("customization-modal");
  const customizeBtn = document.getElementById("customize-schedule");
  const closeModal = document.getElementById("close-modal");
  const resetBtn = document.getElementById("reset-schedule");
  const generateSuggestionsBtn = document.getElementById("generate-suggestions");
  const form = document.getElementById("customization-form");

  customizeBtn.addEventListener("click", function() {
    populateCustomizationForm();
    modal.style.display = "block";
  });

  closeModal.addEventListener("click", function() {
    modal.style.display = "none";
  });

  window.addEventListener("click", function(event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });

  resetBtn.addEventListener("click", function() {
    if (confirm("Are you sure you want to reset to the default schedule? This will erase all your customizations.")) {
      currentSchedule = JSON.parse(JSON.stringify(defaultSchedule));
      populateCustomizationForm();
      populateTimetable();
      localStorage.removeItem("blackHoleSchedule");
    }
  });

  generateSuggestionsBtn.addEventListener("click", function() {
    // Generate completely new personalized suggestions
    generatePersonalizedSuggestions();
    alert("New personalized suggestions generated based on your current schedule!");
  });

  form.addEventListener("submit", function(event) {
    event.preventDefault();

    // Update currentSchedule with form values
    currentSchedule.studentName = document.getElementById("student-name").value;
    currentSchedule.focusArea = document.getElementById("focus-area").value;
    currentSchedule.currentProject = document.getElementById("current-project").value;
    currentSchedule.sleepPattern = document.getElementById("sleep-pattern").value;
    currentSchedule.socialPreference = document.getElementById("social-preference").value;
    currentSchedule.exerciseFrequency = document.getElementById("exercise-frequency").value;
    currentSchedule.breakStyle = document.getElementById("break-style").value;
    currentSchedule.studyEnvironment = document.getElementById("study-environment").value;
    currentSchedule.suggestionsPreference = document.getElementById("suggestions-preference").value;

    // Update activity types from the form
    const activitySelects = document.querySelectorAll(".activity-edit");
    activitySelects.forEach(select => {
      const slotIndex = parseInt(select.dataset.slotIndex);
      const dayIndex = parseInt(select.dataset.dayIndex);
      currentSchedule.timeSlots[slotIndex].days[dayIndex].type = select.value;
    });

    // Generate personalized suggestions based on new data
    generatePersonalizedSuggestions();

    // Save to localStorage
    localStorage.setItem("blackHoleSchedule", JSON.stringify(currentSchedule));

    // Update the timetable
    populateTimetable();

    // Close the modal
    modal.style.display = "none";

    // Show success message
    alert("Your schedule has been updated with personalized suggestions!");
  });

  // Initialize the timetable
  populateTimetable();

  // Generate initial personalized suggestions
  generatePersonalizedSuggestions();
});
