"use strict";
window.addEventListener("load", () => {
  async function translate(
    sourceElem,
    destElem,
    linkElem,
    sourceLang,
    destLang
  ) {
    const post = document.getElementById(sourceElem);
    const link = document.getElementById(linkElem);
    const translation = document.getElementById(destElem);

    link.innerHTML = `
    <div class="animate-spin inline-block size-4 border-3 border-current border-t-transparent text-blue-600 rounded-full dark:text-blue-500" role="status" aria-label="${link.dataset.label}">
      <span class="sr-only">${link.dataset.label}</span>
    </div>`;

    const response = await fetch("/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify({
        text: post.innerText,
        src_lang: sourceLang,
        dest_lang: destLang,
      }),
    });
    const data = await response.json();

    translation.innerText = data.text;
    translation.parentElement.classList.toggle("hidden");
    link.innerHTML = "";
  }

  document
    .getElementById("posts-container")
    .addEventListener("click", (event) => {
      if (!event.target.matches(".translate-link")) return;

      event.preventDefault();
      const link = event.target;
      const postId = link.dataset.postId;
      const language = link.dataset.language;
      const locale = link.dataset.locale;

      translate(
        `post${postId}`,
        `translation${postId}`,
        `link${postId}`,
        language,
        locale
      );
    });
});
