"use strict";

window.addEventListener("load", () => {
  document
    .getElementById("posts-container")
    .addEventListener("mouseover", async (e) => {
      if (!e.target.matches(".hs-tooltip a")) return;
      console.log(e.target.innerText);

      const response = await fetch(`/user/${e.target.innerText.trim()}/popup`);
      const data = await response.text();
      const popover = e.target.parentElement.querySelector(
        ".hs-tooltip-content"
      );

      if (popover && data) {
        popover.innerHTML = data;
        flask_moment_render_all();
      }
    });
});
