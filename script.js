const promptInput = document.getElementById("prompt");
const styleSelect = document.getElementById("style");
const shapeSelect = document.getElementById("shape");
const generateBtn = document.getElementById("generateBtn");
const statusText = document.getElementById("status");
const preview = document.getElementById("preview");
const downloadLink = document.getElementById("downloadLink");

generateBtn.addEventListener("click", async () => {
  const prompt = promptInput.value.trim();
  if (!prompt) {
    statusText.textContent = "Please describe the image you want first.";
    promptInput.focus();
    return;
  }

  generateBtn.disabled = true;
  generateBtn.textContent = "Generating...";
  statusText.textContent = "Connecting to the AI image service...";
  downloadLink.classList.add("hidden");

  try {
    // The API key stays safely on the server, not in this browser code.
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt,
        style: styleSelect.value,
        size: shapeSelect.value
      })
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Image generation failed.");

    preview.innerHTML = "";
    const img = document.createElement("img");
    img.src = data.image;
    img.alt = "AI-generated image";
    preview.appendChild(img);
    downloadLink.href = data.image;
    downloadLink.classList.remove("hidden");
    statusText.textContent = "Your image is ready!";
  } catch (error) {
    statusText.textContent = error.message.includes("Failed to fetch")
      ? "The AI server is not running yet. Follow README.md to set it up."
      : error.message;
  } finally {
    generateBtn.disabled = false;
    generateBtn.textContent = "✦ Generate image";
  }
});


// Photo upload and preview
const photoUpload = document.getElementById("photoUpload");
const photoPreview = document.getElementById("photoPreview");
photoUpload.addEventListener("change", () => {
  const file = photoUpload.files && photoUpload.files[0];
  if (!file) return;
  photoPreview.src = URL.createObjectURL(file);
  photoPreview.classList.remove("hidden");
});

// Camera access (works on localhost or HTTPS in supported browsers)
const cameraBtn = document.getElementById("cameraBtn");
const cameraArea = document.getElementById("cameraArea");
const cameraVideo = document.getElementById("cameraVideo");
const captureBtn = document.getElementById("captureBtn");
const captureCanvas = document.getElementById("captureCanvas");
let cameraStream = null;

cameraBtn.addEventListener("click", async () => {
  try {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      cameraStream = null;
      cameraArea.classList.add("hidden");
      cameraBtn.textContent = "Open camera";
      return;
    }
    cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false });
    cameraVideo.srcObject = cameraStream;
    cameraArea.classList.remove("hidden");
    cameraBtn.textContent = "Close camera";
  } catch (error) {
    alert("Camera access was blocked or is unavailable. Allow camera permission and use localhost or HTTPS.");
  }
});

captureBtn.addEventListener("click", () => {
  if (!cameraStream) return;
  captureCanvas.width = cameraVideo.videoWidth;
  captureCanvas.height = cameraVideo.videoHeight;
  captureCanvas.getContext("2d").drawImage(cameraVideo, 0, 0);
  photoPreview.src = captureCanvas.toDataURL("image/png");
  photoPreview.classList.remove("hidden");
});

// Social content demo (template-based until an AI text API is connected)
document.getElementById("socialBtn").addEventListener("click", () => {
  const prompt = document.getElementById("socialPrompt").value.trim();
  if (!prompt) {
    document.getElementById("socialOutput").value = "First describe your photo or its mood above.";
    return;
  }
  document.getElementById("socialOutput").value =
    `${prompt}\n\nA little moment, a lasting memory ✨\n\n#SnapVoice #PhotoOfTheDay #GoodVibes\n\nSong idea: choose a track that matches the mood of your photo.`;
});

document.getElementById("copySocialBtn").addEventListener("click", async () => {
  const output = document.getElementById("socialOutput");
  if (!output.value.trim()) {
    output.value = "Create a social post first.";
    return;
  }
  try {
    await navigator.clipboard.writeText(output.value);
    document.getElementById("copySocialBtn").textContent = "Copied!";
    setTimeout(() => document.getElementById("copySocialBtn").textContent = "Copy post", 1500);
  } catch {
    output.select();
    document.execCommand("copy");
  }
});

// Makeover idea prompt (image transformation itself needs an image-editing model)
document.getElementById("makeoverBtn").addEventListener("click", () => {
  const idea = document.getElementById("makeoverStyle").value;
  document.getElementById("makeoverOutput").value =
    `Makeover idea: ${idea}. Keep the person's identity and natural facial features consistent. Apply a realistic, flattering style with natural lighting and a polished result.`;
});
