"user strict";

window.addEventListener("load", () => {
  const textarea = document.querySelector("#new-post-txt");
  const charsLeftSpan = document.querySelector("#new-post-chars");

  function handleInputChange() {
    const maxChars = textarea.maxLength;
    const currentChars = textarea.value ? textarea.value.length : 0;
    const charsLeft = maxChars - currentChars;
    charsLeftSpan.textContent = charsLeft.toString();
  }

  textarea.addEventListener("input", handleInputChange);
  handleInputChange();
});
