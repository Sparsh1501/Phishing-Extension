// Endpoint of the local FastAPI server (see app.py).
const API_URL = "http://127.0.0.1:8000/predict";

document.addEventListener("DOMContentLoaded", () => {
    const urlInput = document.getElementById("url-input");
    const checkButton = document.getElementById("checkButton");
    const resultDisplay = document.getElementById("result");

    // Pre-fill the input with the URL of the active tab, when available.
    if (chrome?.tabs?.query) {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs && tabs[0] && tabs[0].url) {
                urlInput.value = tabs[0].url;
            }
        });
    }

    checkButton.addEventListener("click", async () => {
        const url = urlInput.value.trim();

        if (!url) {
            resultDisplay.textContent = "Please enter a URL";
            resultDisplay.style.color = "#333";
            return;
        }

        resultDisplay.textContent = "Checking...";
        resultDisplay.style.color = "#333";

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url }),
            });

            if (!response.ok) {
                resultDisplay.textContent = "Error: Unable to check URL.";
                resultDisplay.style.color = "red";
                return;
            }

            const data = await response.json();

            if (data.is_phishing === true) {
                resultDisplay.textContent = "Warning: This URL is likely a phishing site!";
                resultDisplay.style.color = "red";
            } else if (data.is_phishing === false) {
                resultDisplay.textContent = "This URL appears to be safe.";
                resultDisplay.style.color = "green";
            } else {
                resultDisplay.textContent = data.Prediction || "Unable to determine.";
                resultDisplay.style.color = "#333";
            }
        } catch (error) {
            console.error("Error:", error);
            resultDisplay.textContent = "Error: Unable to reach the server.";
            resultDisplay.style.color = "red";
        }
    });
});
