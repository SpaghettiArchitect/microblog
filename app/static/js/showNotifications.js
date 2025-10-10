"use strict";

// Show the total new messages in the notification badge.
function set_message_count(n) {
  const badge1 = document.getElementById("badge1");
  const badge2 = document.getElementById("badge2");

  if (n) {
    badge2.innerText = n;
    badge1.classList.replace("hidden", "visible");
    badge2.classList.replace("hidden", "visible");
  }
}

// Set the progress of any currently running task.
function set_task_progress(task_id, progress) {
  const progressEl = document.getElementById(`${task_id}-progress`);
  const progressbarEl = document.getElementById(`${task_id}-progressbar`);

  if (progressEl && progressbarEl) {
    progressEl.innerText = `${progress}%`;
    progressbarEl.style.width = `${progress}%`;
  }
}

function initialize_notifications() {
  let since = 0;
  setInterval(async function () {
    const response = await fetch(`/notifications?since=${since}`);
    const notifications = await response.json();

    for (let i = 0; i < notifications.length; i++) {
      switch (notifications[i].name) {
        case "unread_message_count":
          set_message_count(notifications[i].data);
          break;
        case "task_progress":
          set_task_progress(
            notifications[i].data.task_id,
            notifications[i].data.progress
          );
          break;
        default:
          break;
      }

      since = notifications[i].timestamp;
    }
  }, 10000);
}

document.addEventListener("DOMContentLoaded", initialize_notifications);
