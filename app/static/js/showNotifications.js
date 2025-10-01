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

function initialize_notifications() {
  let since = 0;
  setInterval(async function () {
    const response = await fetch(`/notifications?since=${since}`);
    const notifications = await response.json();

    for (let i = 0; i < notifications.length; i++) {
      if (notifications[i].name === "unread_message_count") {
        set_message_count(notifications[i].data);
      }
      since = notifications[i].timestamp;
    }
  }, 10000);
}

document.addEventListener("DOMContentLoaded", initialize_notifications);
