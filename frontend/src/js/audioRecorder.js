const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");
const clearChatBtn = document.getElementById("clear_chat"); // The "Clear Chat" button
const chatBlockMain = document.querySelector(".chat__block-main");

let mediaRecorder;
let audioChunks = [];
const messages = []; // To store messages (audio and text)

// Replace this URL with your actual API endpoint
const API_URL = "http://127.0.0.1:5000/model1";

startBtn.addEventListener("click", async () => {
  // Request microphone access
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

  // Create a MediaRecorder instance
  mediaRecorder = new MediaRecorder(stream);

  // Capture audio data
  mediaRecorder.ondataavailable = (event) => {
    audioChunks.push(event.data);
  };

  // Save the recorded audio
  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
    audioChunks = []; // Clear chunks for a new recording
    const audioUrl = URL.createObjectURL(audioBlob);

    // Add the audio message to the chat immediately
    const audioMessage = document.createElement("div");
    audioMessage.classList.add("chat__block-main-message");
    audioMessage.innerHTML = `
      <audio class="audio-playback" controls>
        <source src="${audioUrl}" type="audio/webm">
        Your browser does not support the audio element.
      </audio>
    `;
    chatBlockMain.appendChild(audioMessage);

    // Create the loading indicator container
    const loadingIndicator = document.createElement("div");
    loadingIndicator.classList.add("loader");

    // Assign an ID to the indicator for CSS targeting
    loadingIndicator.id = "indicator";

    // Append four unique <div> elements to the loadingIndicator
    for (let i = 0; i < 4; i++) {
      const div = document.createElement("div");
      loadingIndicator.appendChild(div);
    }

    // Create the message container
    const loadingMessage = document.createElement("div");
    loadingMessage.classList.add("chat__block-main-message");

    // Append the loading indicator to the message container
    loadingMessage.appendChild(loadingIndicator);

    // Append the loading message to the chat block
    chatBlockMain.appendChild(loadingMessage);

    // Send audio to API and get the response
    const formData = new FormData();
    formData.append("audio", audioBlob);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to process audio");
      }

      const data = await response.json(); // Assuming the API returns JSON
      const responseText = data.text; // Replace with the correct field from the API response

      // Remove the loading message
      chatBlockMain.removeChild(loadingMessage);

      // Add the API response text to the chat
      const textMessage = document.createElement("div");
      textMessage.classList.add("chat__block-main-message");
      textMessage.innerHTML = `<div class="message">${responseText}</div>`;
      chatBlockMain.appendChild(textMessage);
    } catch (error) {
      console.error("Error sending audio to API:", error);
      // alert("Failed to process the audio. Please try again.");

      // In case of error, remove the loading message
      chatBlockMain.removeChild(loadingMessage);

      // Add an error message to the chat
      const errorMessage = document.createElement("div");
      errorMessage.classList.add("chat__block-main-message");
      errorMessage.innerHTML = `<div class="message">Error: ${error.message}</div>`;
      chatBlockMain.appendChild(errorMessage);
    }
  };

  mediaRecorder.start();
  startBtn.disabled = true;
  stopBtn.disabled = false;
});

stopBtn.addEventListener("click", () => {
  mediaRecorder.stop();
  startBtn.disabled = false;
  stopBtn.disabled = true;
});

// Clear Chat Functionality
clearChatBtn.addEventListener("click", () => {
  // Clear the chat history by removing all child elements from the chat container
  chatBlockMain.innerHTML = "";
  messages.length = 0; // Optionally clear the messages array if you're storing the data in it
});
