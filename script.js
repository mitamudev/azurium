const copyButton = document.querySelector("[data-copy-loadstring]");
const loadstring = document.querySelector("#loadstring");
const toast = document.querySelector(".toast");
const logoZone = document.querySelector(".logo-zone");

let toastTimer;

async function copyText(text) {
  if (window.navigator && navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // Fall back to the selection-based path below.
    }
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.select();
  const copied = document.execCommand("copy");
  textarea.remove();
  return copied;
}

function showToast() {
  clearTimeout(toastTimer);
  toast.classList.add("is-visible");
  toastTimer = window.setTimeout(() => {
    toast.classList.remove("is-visible");
  }, 1700);
}

if (copyButton && loadstring) {
  copyButton.addEventListener("click", async () => {
    const originalText = copyButton.textContent;

    try {
      const copied = await copyText(loadstring.textContent.trim());
      copyButton.textContent = copied ? "Copied" : "Select";
      copyButton.classList.toggle("is-copied", copied);
      if (copied) showToast();
    } catch {
      copyButton.textContent = "Failed";
    }

    window.setTimeout(() => {
      copyButton.textContent = originalText;
      copyButton.classList.remove("is-copied");
    }, 1500);
  });
}

if (logoZone) {
  logoZone.addEventListener("pointermove", (event) => {
    const rect = logoZone.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;

    logoZone.style.setProperty("--ry", `${x * 10}deg`);
    logoZone.style.setProperty("--rx", `${y * -10}deg`);
  });

  logoZone.addEventListener("pointerleave", () => {
    logoZone.style.setProperty("--ry", "0deg");
    logoZone.style.setProperty("--rx", "0deg");
  });
}
