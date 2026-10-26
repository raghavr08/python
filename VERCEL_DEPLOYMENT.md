# Deploy ResumeIQ on Vercel

## What this deployment includes

This repository deploys the ResumeIQ frontend and its browser-based demonstration workflow to Vercel. The Python FastAPI source is included under `backend/`, but the current frontend does not yet call a deployed backend for PDF/DOCX extraction or live AI analysis.

## Required project files

Keep this structure intact:

```text
resumeiq/
  src/
    index.html
    app.js
    style.css
  backend/
    main.py
    requirements.txt
  package.json
  build.mjs
  vercel.json
  .env.example
  .gitignore
  README.md
  VERCEL_DEPLOYMENT.md
```

Do not upload only `index.html`. The JavaScript, CSS, build script, and package configuration are all needed.

## Recommended deployment: GitHub to Vercel

1. Extract the project ZIP into a folder named `resumeiq`.
2. Create a new empty GitHub repository.
3. In a terminal opened inside the `resumeiq` folder, run:

```bash
git init
git add .
git commit -m "Initial ResumeIQ project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/resumeiq.git
git push -u origin main
```

4. Sign in to Vercel and select **Add New > Project**.
5. Import the `resumeiq` GitHub repository.
6. Use these project settings:
   - Framework Preset: **Other**
   - Root Directory: `./`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: leave the automatic/default value
7. Select **Deploy**.

The included `vercel.json` normally fills in the build and output settings automatically.

## Alternative: Vercel CLI

With Node.js installed, open a terminal in the project folder and run:

```bash
npm install -g vercel
vercel
```

Follow the prompts and accept the detected project settings. To publish the production version later, run:

```bash
vercel --prod
```

## Environment variables

Do not put API keys in `src/app.js`, GitHub, or the ZIP. When the live backend integration is implemented, add `OPENAI_API_KEY` or the selected AI provider key in **Vercel Project Settings > Environment Variables**.

## Local preview

From the project folder:

```bash
npm run build
python -m http.server 4173 --directory dist
```

Then open `http://127.0.0.1:4173/`.
