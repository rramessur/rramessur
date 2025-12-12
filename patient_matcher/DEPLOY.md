# Deploying Patient Matcher

To make this application accessible to anyone on the internet, you can use a free static hosting service. Since this application is purely client-side (HTML/CSS/JS), it is very easy to host.

## Option 1: Netlify Drop (Easiest)
1. Go to [Netlify Drop](https://app.netlify.com/drop).
2. Locate the `patient_matcher` folder on your computer:
   `c:\Users\rrame\rramessur\patient_matcher`
3. Drag and drop the **entire folder** into the Netlify Drop area.
4. It will immediately publish and give you a unique URL (e.g., `https://random-name-12345.netlify.app`).
5. You can share this URL with anyone.

## Option 2: GitHub Pages
If you are pushing this code to GitHub:
1. Ensure the `patient_matcher` folder is in your repository.
2. Go to your repository **Settings** > **Pages**.
3. Under **Source**, select `main` branch (or your working branch).
4. If possible, set the folder to `/patient_matcher` (GitHub Pages usually serves from root or `/docs`). 
   - *Tip:* You might want to move the contents of `patient_matcher` to the root of a new repository specifically for this site to make it easier.
5. Your site will be live at `https://<username>.github.io/<repo-name>/`.
