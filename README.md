# Ashish Portfolio

This is a simple static portfolio site. I fixed image asset handling and included instructions to run it locally.

## Run locally

Requirements:

- Python 3.x installed and available in PATH
- Git (for cloning/updating)

Start a local static server from the project root:

```powershell
# starts a static server on port 8000
python -m http.server 8000
# then open http://localhost:8000 in your browser
```

Or use npm (convenience) if you have Node.js installed:

```powershell
npm install
npm run start
```

## Notes

- I removed `assets/img/` from `.gitignore` and committed the images so they are served correctly on GitHub and GitHub Pages.
- A missing background image reference (`assets/img/bg.png`) was removed from `assets/css/style.css` and replaced with a neutral background color to avoid 404s. If you want a background image, add it to `assets/img/` and restore the CSS reference.
- If you host via GitHub Pages, make sure Pages is configured to serve from the `main` branch (or your chosen branch). After pushing, Pages usually updates within a minute.

If you'd like, I can also:

- Add a tiny GitHub Action to auto-deploy or check for missing assets.
- Restore or add a background image and tune styles.
- Keep the local server running or stop it for you.

Tell me which follow-up you want next.
