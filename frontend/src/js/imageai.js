const chatInput = document.getElementById("chat-input"); // Text input field
const chatSubmit = document.getElementById("chat-submit"); // Submit button
const chatBlockMain = document.querySelector(".chat__block-main");
const clearChatButton = document.getElementById("clear-chat"); // Clear chat button

const backendBaseUrl = "http://127.0.0.1:5000/"; // Backend base URL

// Event listener for clearing the chat
clearChatButton.addEventListener("click", () => {
  // Remove all messages from the chat container
  chatBlockMain.innerHTML = "";
});

// Function to handle chat submission
const handleChatSubmit = async () => {
  const userMessage = chatInput.value.trim();

  if (userMessage === "") {
    return; // Do nothing if the input is empty
  }

  // Add the user's message to the chat
  const userMessageElement = document.createElement("div");
  userMessageElement.classList.add("chat__block-main-message");
  userMessageElement.innerHTML = `<div class="question">${userMessage}</div>`;
  chatBlockMain.appendChild(userMessageElement);

  // Clear the input field
  chatInput.value = "";

  // Create the loading message container
  const loadingMessage = document.createElement("div");
  loadingMessage.classList.add("chat__block-main-message", "loading");

  // Create the loader container
  const loaderContainer = document.createElement("div");
  loaderContainer.classList.add("loader-container");

  // Create the loader itself
  const loader = document.createElement("div");
  loader.classList.add("loader");
  for (let i = 0; i < 4; i++) {
    const div = document.createElement("div");
    loader.appendChild(div);
  }

  // Append loader to the container
  loaderContainer.appendChild(loader);
  loadingMessage.appendChild(loaderContainer);

  // Add the loading message to the chat block
  chatBlockMain.appendChild(loadingMessage);

  try {
    // Send the image generation prompt to the backend
    const response = await fetch("http://127.0.0.1:5000/image", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt: userMessage }), // Sending the prompt for image generation
    });

    const data = await response.json();

    if (response.ok) {
      // Remove loading indicator
      chatBlockMain.removeChild(loadingMessage);

      // Construct the full image URL by combining the backend URL and the image path
      const imageUrl = backendBaseUrl + data.image_path; // Prepend the backend URL to the image path

      const imageMessageElement = document.createElement("div");
      imageMessageElement.classList.add("chat__block-main-message");

      // Add image element to the message
      const img = document.createElement("img");
      img.classList.add("image");
      img.src = imageUrl; // The full URL to the generated image
      img.alt = "Generated Image";

      imageMessageElement.appendChild(img);
      chatBlockMain.appendChild(imageMessageElement);
    } else {
      // Handle errors
      alert("Error: " + data.error);
    }
  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred while processing your request.");
  }
};

// Event listener for clicking the submit button
chatSubmit.addEventListener("click", handleChatSubmit);

// Event listener for pressing Enter in the input field
chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    handleChatSubmit();
  }
});
