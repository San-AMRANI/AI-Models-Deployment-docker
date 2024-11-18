function formatResponse(responseText) {
  // Split the response into two parts: introduction and list of cities
  const [introduction, citiesPart] = responseText.split(":")[0]
    ? [responseText.split(":")[0], responseText.split(":").slice(1).join(":")]
    : [responseText, ""];

  // Clean the introduction part
  const formattedIntroduction = introduction.trim().replace(/\n/g, "<br/>"); // Replace newlines with <br> tags for HTML rendering

  // Make words between **bold**
  const formattedBoldText = formattedIntroduction.replace(
    /\*\*(.*?)\*\*/g,
    "<strong>$1</strong>"
  );

  // Format the list of cities
  const cityList = citiesPart
    .trim()
    .split("\n")
    .map((line, index) => {
      // Check for city data (city name and visitor count)
      const match = line.match(
        /^(\d+)\.\s*(.*?)\s*[:\s]+([0-9.,]+)\s*visitors/
      );
      if (match) {
        return `<li><strong>${match[1]}. ${match[2]}:</strong> ${match[3]} visitors</li>`;
      }
      return null;
    })
    .filter(Boolean)
    .join("");

  // Combine the formatted introduction and city list
  return `
      <p>${formattedBoldText}</p>
      <ul>${cityList}</ul>
    `;
}

//////////////////////////////////////////////////////////////////////////

const chatInput = document.getElementById("chat-input"); // Text input field
const chatSubmit = document.getElementById("chat-submit"); // Submit button
const chatBlockMain = document.querySelector(".chat__block-main");
const clearChatButton = document.getElementById("clear-chat"); // Clear chat button

// Event listener for clearing the chat
clearChatButton.addEventListener("click", () => {
  // Remove all messages from the chat container
  chatBlockMain.innerHTML = "";
});

// Event listener for submitting the chat input
chatSubmit.addEventListener("click", async () => {
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

  // Add custom loading indicator
  const loadingMessage = document.createElement("div");
  loadingMessage.classList.add("chat__block-main-message", "loading");

  // Create the loading indicator container
  const loadingIndicator = document.createElement("div");
  loadingIndicator.classList.add("loader");
  loadingIndicator.id = "indicator"; // Optional: Add an ID for CSS targeting

  // Append four unique <div> elements to the loadingIndicator
  for (let i = 0; i < 4; i++) {
    const div = document.createElement("div");
    loadingIndicator.appendChild(div);
  }

  loadingMessage.appendChild(loadingIndicator);
  chatBlockMain.appendChild(loadingMessage);

  try {
    // Send the message to the backend for processing
    const response = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ chatInput: userMessage }), // Ensure the key is chatInput
    });

    const data = await response.json();

    if (response.ok) {
      // Remove loading indicator
      chatBlockMain.removeChild(loadingMessage);

      // Format the assistant's response for readability
      const formattedResponse = formatResponse(data.response);

      // Add assistant's response to the chat
      const assistantMessageElement = document.createElement("div");
      assistantMessageElement.classList.add("chat__block-main-message");

      // Add the formatted response
      assistantMessageElement.innerHTML = `<div class="response">${formattedResponse}</div>`;
      chatBlockMain.appendChild(assistantMessageElement);

      // Add event listener to the response text for copying
      const responseText = assistantMessageElement.querySelector(".response");
      responseText.addEventListener("click", () => {
        const textToCopy = responseText.innerText;
        navigator.clipboard
          .writeText(textToCopy)
          .then(() => {
            // Provide feedback to the user (change text temporarily)
            responseText.innerText = "Copied!";
            setTimeout(() => {
              // Reset text back to original response after 1 second
              responseText.innerHTML = formattedResponse;
            }, 1000);
          })
          .catch((err) => {
            console.error("Error copying text: ", err);
          });
      });
    } else {
      // Handle errors
      alert("Error: " + data.error);
    }
  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred while processing your request.");
  }
});
