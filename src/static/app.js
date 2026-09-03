document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const activityCount = document.getElementById("activity-count");
  const participantCount = document.getElementById("participant-count");
  const openSpots = document.getElementById("open-spots");
  const selectedActivity = document.getElementById("selected-activity");
  let activitiesData = {};

  function updateSelectedActivity() {
    const activity = activitiesData[activitySelect.value];
    if (!activity) {
      selectedActivity.classList.remove("is-visible");
      selectedActivity.innerHTML = "";
      return;
    }

    const spotsLeft = activity.max_participants - activity.participants.length;
    selectedActivity.innerHTML = `
      <strong>${activitySelect.value}</strong>
      <span>${activity.schedule} &middot; ${spotsLeft} spots left</span>
    `;
    selectedActivity.classList.add("is-visible");
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();
      activitiesData = activities;

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">Select from the lineup...</option>';

      const activityEntries = Object.entries(activities);
      const totalParticipants = activityEntries.reduce(
        (total, [, details]) => total + details.participants.length,
        0
      );
      const totalOpenSpots = activityEntries.reduce(
        (total, [, details]) => total + details.max_participants - details.participants.length,
        0
      );
      activityCount.textContent = String(activityEntries.length).padStart(2, "0");
      participantCount.textContent = totalParticipants;
      openSpots.textContent = totalOpenSpots;

      // Populate activities list
      activityEntries.forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participantsList = details.participants.map(p => `<li><span>${p}</span><button class="delete-participant" data-activity="${name}" data-email="${p}" title="Remove participant">✕</button></li>`).join('');

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <strong>Current Participants:</strong>
            <ul class="participants-list">
              ${participantsList}
            </ul>
          </div>
        `;

        // Add event listeners to delete buttons
        const deleteButtons = activityCard.querySelectorAll('.delete-participant');
        deleteButtons.forEach(btn => {
          btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const activity = btn.getAttribute('data-activity');
            const email = btn.getAttribute('data-email');
            
            try {
              const response = await fetch(
                `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
                { method: 'DELETE' }
              );
              
              if (response.ok) {
                // Refresh the activities list
                fetchActivities();
              } else {
                const error = await response.json();
                alert(error.detail || 'Failed to remove participant');
              }
            } catch (error) {
              alert('Failed to remove participant');
              console.error('Error removing participant:', error);
            }
          });
        });

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      activitySelect.value = activitiesData["Chess Club"] ? "Chess Club" : activityEntries[0]?.[0] || "";
      updateSelectedActivity();
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  activitySelect.addEventListener("change", updateSelectedActivity);

  // Initialize app
  fetchActivities();
});
