(function() {
    const repoUrl = "https://github.com/cloudmesh-ai/cloudmesh-ai-lecture";
    const branch = "main";

    function injectSourceLinks() {
        // 1. Calculate the source URL
        const path = window.location.pathname;
        const projectName = repoUrl.split('/').pop();
        
        // Split path into segments and remove the project name if it's the first segment
        const segments = path.split('/').filter(s => s.length > 0);
        if (segments.length > 0 && segments[0] === projectName) {
            segments.shift();
        }

        // Join remaining segments and convert .html to .md
        let relativePath = segments.join('/');
        relativePath = relativePath.replace(/\/index\.html$/, "").replace(/\.html$/, ".md");
        
        // Handle the root/index case
        if (!relativePath || relativePath === "index.html") {
            relativePath = "index.md";
        } else if (!relativePath.endsWith(".md")) {
            // If it's a directory path (ends in /), we usually want the index.md of that directory
            if (path.endsWith('/')) {
                relativePath += "/index.md";
            } else {
                relativePath += ".md";
            }
        }

        // Ensure there is a leading slash for the final URL construction
        const finalRelativePath = relativePath.startsWith('/') ? relativePath : '/' + relativePath;
        const sourceUrl = `${repoUrl}/blob/${branch}/docs${finalRelativePath}`;

        // 2. Inject into Right Sidebar (TOC)
        const tocSelectors = [".md-navigate__inner", ".md-sidebar--secondary .md-navigate", ".md-toc"];
        let tocContainer = null;
        for (const selector of tocSelectors) {
            const el = document.querySelector(selector);
            if (el && !document.getElementById("custom-show-source-toc")) {
                tocContainer = el;
                break;
            }
        }

        if (tocContainer) {
            const sourceLink = document.createElement("a");
            sourceLink.id = "custom-show-source-toc";
            sourceLink.href = sourceUrl;
            sourceLink.innerHTML = '📁 Show Source';
            sourceLink.style.display = "block";
            sourceLink.style.marginBottom = "1rem";
            sourceLink.style.fontWeight = "bold";
            sourceLink.style.color = "var(--md-primary-fg-color, #2196f3)";
            sourceLink.style.textDecoration = "none";
            sourceLink.style.padding = "0.5rem 0";
            sourceLink.style.borderBottom = "1px solid rgba(0,0,0,0.1)";
            tocContainer.prepend(sourceLink);
        }

        // 3. Inject into Header
        const headerSelectors = [".md-header__inner", ".md-header", ".md-toolbar"];
        let headerContainer = null;
        for (const selector of headerSelectors) {
            const el = document.querySelector(selector);
            if (el && !document.getElementById("custom-show-source-header")) {
                headerContainer = el;
                break;
            }
        }

        if (headerContainer) {
            const pencilLink = document.createElement("a");
            pencilLink.id = "custom-show-source-header";
            pencilLink.href = sourceUrl;
            // Use a combination of Font Awesome and a Unicode fallback for visibility
            pencilLink.innerHTML = '<span style="font-family: Arial, sans-serif; margin-right: 5px;">✎</span> Source';
            pencilLink.title = "View source on GitHub";
            pencilLink.style.marginRight = "15px";
            pencilLink.style.fontSize = "0.9rem";
            pencilLink.style.color = "#FFFFFF";
            pencilLink.style.textDecoration = "none";
            pencilLink.style.zIndex = "9999";
            pencilLink.style.display = "inline-flex";
            pencilLink.style.alignItems = "center";
            pencilLink.style.cursor = "pointer";
            pencilLink.style.backgroundColor = "rgba(255,255,255,0.2)";
            pencilLink.style.padding = "2px 8px";
            pencilLink.style.borderRadius = "4px";
            pencilLink.style.border = "1px solid rgba(255,255,255,0.3)";
            pencilLink.style.fontWeight = "bold";
            
            pencilLink.onmouseover = () => {
                pencilLink.style.backgroundColor = "rgba(255,255,255,0.4)";
            };
            pencilLink.onmouseout = () => {
                pencilLink.style.backgroundColor = "rgba(255,255,255,0.2)";
            };
            
            headerContainer.prepend(pencilLink);
        }
    }

    // Use MutationObserver to wait for the theme to render the UI
    const observer = new MutationObserver((mutations, obs) => {
        injectSourceLinks();
        // We don't disconnect because Material may re-render on page transitions
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Also try immediately
    injectSourceLinks();
})();
