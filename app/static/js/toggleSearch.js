"use strict";
window.addEventListener("DOMContentLoaded", () => {
  const searchButton = document.getElementById("searchButton");
  const searchForm = document.getElementById("searchForm");
  const searchInput = document.getElementById("searchInput");
  const searchContainer = document.getElementById("searchContainer");

  let isExpanded = false;

  // Function to expand the search box
  function expandSearch() {
    isExpanded = true;
    searchButton.classList.add("hidden");
    searchForm.classList.remove("hidden");

    // Small delay to ensure the element is rendered before animating
    setTimeout(() => {
      searchForm.classList.remove("opacity-0");
      searchForm.classList.add("opacity-100");
      searchInput.focus();
    }, 10);
  }

  // Function to collapse the search box
  function collapseSearch() {
    isExpanded = false;
    searchForm.classList.remove("opacity-100");
    searchForm.classList.add("opacity-0");

    // Wait for the fade animation to complete before hiding
    setTimeout(() => {
      searchForm.classList.add("hidden");
      searchButton.classList.remove("hidden");
    }, 300);
  }

  // Event listener for search button click
  searchButton.addEventListener("click", expandSearch);

  // Event listener for clicking outside the search box
  document.addEventListener("click", (event) => {
    if (isExpanded && !searchContainer.contains(event.target)) {
      collapseSearch();
    }
  });

  // Event listener for Escape key
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && isExpanded) {
      collapseSearch();
    }
  });

  // Prevent form from collapsing when clicking inside the input
  searchInput.addEventListener("click", (event) => {
    event.stopPropagation();
  });
});
