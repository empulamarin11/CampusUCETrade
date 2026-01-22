# Web App (PWA) — `apps/web`

This folder contains the **Web/PWA frontend** for CampusUCETrade, built with **Vite**.  
It is designed to work with **two backends**:
- **QA backend** (QA ALB DNS)
- **PROD backend** (PROD ALB DNS)

To support both environments cleanly, the project includes:
- environment files (`.env`, `.env.production`)
- Netlify configs (`netlify.qa.toml`, `netlify.prod.toml`)
- standard Vite build output (`dist/`)

---

## 1) Folder Structure

apps/web/
public/ # static assets
src/ # application source code
dist/ # build output (generated)
index.html
vite.config.js
package.json
package-lock.json
.env
.env.production
netlify.qa.toml
netlify.prod.toml
Dockerfile


---

## 2) Environments (QA vs PROD)

### Local development
- Uses `.env` by default.
- Start dev server:
```bash
cd apps/web
npm install
npm run dev

