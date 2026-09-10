function movePresentationButton() {
    const button = document.getElementById("presentation-button");
    const tocContainer = document.querySelector(".md-sidebar--secondary .md-nav");
    if (button && tocContainer) {
        if (button.parentElement !== tocContainer) {
            tocContainer.prepend(button);
            button.style.marginBottom = "20px";
            button.style.display = "flex";
        }
    }
}

// Run on initial load
document.addEventListener("DOMContentLoaded", movePresentationButton);

// Material for MkDocs uses instant loading. Observe the main content area for changes.
document.addEventListener("DOMContentLoaded", function() {
    const contentArea = document.querySelector(".md-content");
    if (contentArea) {
        const observer = new MutationObserver(() => {
            movePresentationButton();
        });
        observer.observe(contentArea, { childList: true, subtree: true });
    }
});
