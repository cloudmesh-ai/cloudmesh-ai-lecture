function movePresentationButton() {
    const button = document.getElementById("presentation-button");
    if (!button) return;

    // Target the secondary sidebar's inner container to ensure it's inside the scroll area and matches the layout
    const tocInner = document.querySelector(".md-sidebar--secondary .md-sidebar__inner");
    
    if (tocInner) {
        // Only move it if it's not already a child of the target container
        if (button.parentElement !== tocInner) {
            tocInner.prepend(button);
            
            // Apply styles to ensure it looks like a professional button and fits the sidebar layout
            button.style.marginBottom = "20px";
            button.style.display = "flex";
            button.style.alignItems = "center";
            button.style.justifyContent = "center";
            button.style.width = "auto";
            button.style.marginRight = "auto";
            button.style.marginLeft = "auto";
            button.style.padding = "8px 12px";
            button.style.zIndex = "100";
        }
    }
}

// Run on initial load
document.addEventListener("DOMContentLoaded", movePresentationButton);

// Material for MkDocs uses instant loading.
// We observe the entire body for changes to catch TOC re-renders and page transitions.
document.addEventListener("DOMContentLoaded", function() {
    const observer = new MutationObserver((mutations) => {
        // Use a small debounce or check to avoid excessive calls
        movePresentationButton();
    });
    
    // Observe the body for any changes in the DOM structure (childList) and nested elements (subtree)
    observer.observe(document.body, { childList: true, subtree: true });
});
