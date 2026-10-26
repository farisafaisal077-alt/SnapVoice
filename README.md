# SnapVoice AI Studio

A starter AI image-generation website with a responsive frontend and a Node.js backend.

## Project files

- `index.html` — website structure
- `style.css` — website design
- `script.js` — browser-side interaction
- `server.js` — backend endpoint that calls the AI image API
- `package.json` — Node.js dependencies and start command
- `.env.example` — template for your private API key

## Important

The website interface can be hosted as static files, but AI image generation requires the Node.js backend to be running on a server. GitHub Pages alone cannot run `server.js`. Do not put your API key in `script.js`, `index.html`, or a public GitHub repository.

## Run on your laptop

1. Install Node.js (LTS) from https://nodejs.org if it is not already installed.
2. Open a terminal in this folder.
3. Install dependencies:

   ```bash
   npm install
   ```

4. Copy `.env.example` to a new file named `.env`.
5. Open `.env` and replace `your_api_key_here` with your own API key. Keep `.env private.
6. Start the site:

   ```bash
   npm start
   ```

7. Open http://localhost:3000 in your browser.

## API and billing

Image generation requires an API key with access to the image model and may incur API charges. Check your provider's current model availability, pricing, and usage limits. Never share your API key.
