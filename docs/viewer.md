<div id="presentation-wrapper" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 9999; background: black; display: flex; flex-direction: column;">
    <div id="controls" style="position: absolute; top: 20px; right: 20px; z-index: 10000; opacity: 0.3; transition: opacity 0.3s;">
        <button id="fullscreen-btn" style="padding: 10px 20px; background: #333; color: white; border: 1px solid #555; border-radius: 5px; cursor: pointer; font-family: sans-serif;">
            Toggle Fullscreen
        </button>
        <a id="exit-btn" href="javascript:history.back()" style="margin-left: 10px; padding: 10px 20px; background: #333; color: white; border: 1px solid #555; border-radius: 5px; cursor: pointer; font-family: sans-serif; text-decoration: none; display: inline-block;">
            Exit
        </a>
    </div>
    <iframe id="presentation-frame" style="width: 100%; height: 100%; border: none;" src=""></iframe>
</div>

<script>
(function() {
    const frame = document.getElementById('presentation-frame');
    const controls = document.getElementById('controls');
    const btn = document.getElementById('fullscreen-btn');

    // 1. Extract URL from query string
    const params = new URLSearchParams(window.location.search);
    const presentationUrl = params.get('url');

    if (presentationUrl) {
        // Convert relative path to site-root relative path if necessary
        // mkdocs-slides and other pages end up as /path/to/page/
        let finalUrl = presentationUrl;
        if (!finalUrl.startsWith('http') && !finalUrl.startsWith('/')) {
            finalUrl = '/' + finalUrl;
        }
        // If it's a .md file, we need to make sure it points to the rendered .html
        // Actually, the hook will pass the path relative to docs root.
        // MkDocs typically serves 'section/linux/gh-talk.md' as '/section/linux/gh-talk/'
        if (finalUrl.endsWith('.md')) {
            finalUrl = finalUrl.replace('.md', '/');
        }
        
        frame.src = finalUrl;
    } else {
        document.getElementById('presentation-wrapper').innerHTML = 
            '<div style="color: white; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: sans-serif;">No presentation URL provided.</div>';
    }

    // 2. Fullscreen logic
    btn.onclick = () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                alert(`Error attempting to enable full-screen mode: ${err.message}`);
            });
        } else {
            document.exitFullscreen();
        }
    };

    // 3. Hover effects for controls
    controls.onmouseenter = () => controls.style.opacity = '1';
    controls.onmouseleave = () => controls.style.opacity = '0.3';
})();
</script>
