const API_BASE_URL = "http://127.0.0.1:5050";

const messagesArea = document.getElementById("messagesArea");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const submitButton = document.getElementById("submitButton");
const recommendedSection = document.getElementById("recommendedSection");
const schemeGrid = document.getElementById("schemeGrid");
const promptChips = document.querySelectorAll(".prompt-chip");


function createElement(tag, className, text) {
  const element = document.createElement(tag);

  if (className) {
    element.className = className;
  }

  if (text !== undefined && text !== null) {
    element.textContent = text;
  }

  return element;
}


function scrollMessagesToBottom() {
  messagesArea.scrollTop = messagesArea.scrollHeight;
}


function appendUserMessage(content) {
  const row = createElement("div", "message-row user-row");

  const bubble = createElement(
    "div",
    "message-bubble user-message"
  );

  const label = createElement(
    "div",
    "message-label",
    "You"
  );

  const body = createElement(
    "div",
    "message-content",
    content
  );

  bubble.append(label, body);
  row.appendChild(bubble);

  messagesArea.appendChild(row);

  scrollMessagesToBottom();
}


function appendAssistantMessage(content) {
  const row = createElement(
    "div",
    "message-row assistant-row"
  );

  const avatar = createElement(
    "div",
    "assistant-avatar",
    "YM"
  );

  const bubble = createElement(
    "div",
    "message-bubble assistant-message"
  );

  const label = createElement(
    "div",
    "message-label",
    "Yojana Mitra"
  );

  const body = createElement(
    "div",
    "message-content"
  );

  renderSimpleMarkdown(body, content);

  bubble.append(label, body);

  row.append(
    avatar,
    bubble
  );

  messagesArea.appendChild(row);

  scrollMessagesToBottom();
}


function renderSimpleMarkdown(container, markdown) {
  const lines = String(markdown || "").split("\n");

  let list = null;

  function closeList() {
    list = null;
  }

  for (const rawLine of lines) {
    const line = rawLine.trim();

    if (!line) {
      closeList();

      container.appendChild(
        document.createElement("br")
      );

      continue;
    }


    if (line.startsWith("### ")) {
      closeList();

      const heading = createElement("h3");

      appendInlineMarkdown(
        heading,
        line.slice(4)
      );

      container.appendChild(heading);

      continue;
    }


    if (line.startsWith("## ")) {
      closeList();

      const heading = createElement("h2");

      appendInlineMarkdown(
        heading,
        line.slice(3)
      );

      container.appendChild(heading);

      continue;
    }


    if (/^[-*]\s+/.test(line)) {
      if (!list) {
        list = document.createElement("ul");

        container.appendChild(list);
      }

      const item = document.createElement("li");

      appendInlineMarkdown(
        item,
        line.replace(/^[-*]\s+/, "")
      );

      list.appendChild(item);

      continue;
    }


    closeList();

    const paragraph = document.createElement("p");

    appendInlineMarkdown(
      paragraph,
      line
    );

    container.appendChild(paragraph);
  }
}


function appendInlineMarkdown(element, text) {
  const value = String(text || "");

  const pattern =
    /(\*\*[^*]+\*\*|\[[^\]]+\]\(https?:\/\/[^\s)]+\)|https?:\/\/[^\s]+)/g;

  let lastIndex = 0;


  for (const match of value.matchAll(pattern)) {
    const index = match.index ?? 0;


    if (index > lastIndex) {
      element.appendChild(
        document.createTextNode(
          value.slice(lastIndex, index)
        )
      );
    }


    const token = match[0];


    if (
      token.startsWith("**") &&
      token.endsWith("**")
    ) {
      const strong = document.createElement("strong");

      strong.textContent =
        token.slice(2, -2);

      element.appendChild(strong);
    }


    else if (token.startsWith("[")) {
      const parts = token.match(
        /^\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)$/
      );


      if (parts) {
        const anchor =
          document.createElement("a");

        anchor.href = parts[2];
        anchor.textContent = parts[1];

        anchor.target = "_blank";
        anchor.rel = "noopener noreferrer";

        element.appendChild(anchor);
      }
    }


    else {
      const anchor =
        document.createElement("a");

      anchor.href = token;
      anchor.textContent = token;

      anchor.target = "_blank";
      anchor.rel = "noopener noreferrer";

      element.appendChild(anchor);
    }


    lastIndex =
      index + token.length;
  }


  if (lastIndex < value.length) {
    element.appendChild(
      document.createTextNode(
        value.slice(lastIndex)
      )
    );
  }
}


function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  messageInput.disabled = isLoading;

  const buttonText =
    submitButton.querySelector(
      "span:first-child"
    );


  if (buttonText) {
    buttonText.textContent =
      isLoading
        ? "Checking schemes..."
        : "Ask Yojana Mitra";
  }
}


function showLoadingMessage() {
  removeLoadingMessage();

  const loading = createElement(
    "div",
    "loading-message",
    "Yojana Mitra is checking relevant schemes..."
  );

  loading.id = "loadingMessage";

  messagesArea.appendChild(loading);

  scrollMessagesToBottom();
}


function removeLoadingMessage() {
  document
    .getElementById("loadingMessage")
    ?.remove();
}


function showError(message) {
  document
    .getElementById("errorMessage")
    ?.remove();


  const error = createElement(
    "div",
    "error-message",
    message || "Something went wrong."
  );

  error.id = "errorMessage";

  messagesArea.appendChild(error);

  scrollMessagesToBottom();
}


function clearError() {
  document
    .getElementById("errorMessage")
    ?.remove();
}


function renderRecommendedSchemes(response) {
  schemeGrid.innerHTML = "";


  const recommendedIds =
    response?.grounding
      ?.recommendedSchemeIds || [];


  const schemes =
    Array.isArray(response?.schemes)
      ? response.schemes
      : [];


  const recommendedSchemes =
    schemes.filter((scheme) =>
      recommendedIds.includes(
        scheme.id
      )
    );


  if (recommendedSchemes.length === 0) {
    recommendedSection.classList.add(
      "hidden"
    );

    return;
  }


  for (const scheme of recommendedSchemes) {
    const card = createElement(
      "article",
      "scheme-card"
    );


    const header = createElement(
      "div",
      "scheme-card-header"
    );


    const badge = createElement(
      "span",
      "scheme-badge",
      "Government Scheme"
    );


    const shortName = createElement(
      "span",
      "scheme-short-name",
      scheme.short_name || ""
    );


    header.append(
      badge,
      shortName
    );


    const title = createElement(
      "h3",
      "",
      scheme.name ||
        "Government Scheme"
    );


    card.append(
      header,
      title
    );


    if (scheme.official_source) {
      const link = createElement(
        "a",
        "scheme-link",
        "View official source →"
      );


      link.href =
        scheme.official_source;

      link.target = "_blank";

      link.rel =
        "noopener noreferrer";


      card.appendChild(link);
    }


    schemeGrid.appendChild(card);
  }


  recommendedSection.classList.remove(
    "hidden"
  );
}


async function sendChatMessage(message) {
  let response;


  try {
    response = await fetch(
      `${API_BASE_URL}/api/chat`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json"
        },

        body: JSON.stringify({
          message: message.trim()
        })
      }
    );
  }


  catch {
    throw new Error(
      "Cannot connect to the Python backend. Make sure FastAPI is running on port 5050."
    );
  }


  let data;


  try {
    data = await response.json();
  }


  catch {
    throw new Error(
      "Backend returned an invalid response."
    );
  }


  if (!response.ok) {
    const errorMessage =
      data?.detail ||
      data?.error ||
      `Request failed with status ${response.status}.`;


    throw new Error(
      typeof errorMessage === "string"
        ? errorMessage
        : "Backend request failed."
    );
  }


  return data;
}


async function handleSubmit(event) {
  event.preventDefault();


  const message =
    messageInput.value.trim();


  if (
    !message ||
    submitButton.disabled
  ) {
    return;
  }


  clearError();


  recommendedSection.classList.add(
    "hidden"
  );


  schemeGrid.innerHTML = "";


  appendUserMessage(message);


  messageInput.value = "";


  setLoading(true);

  showLoadingMessage();


  try {
    const response =
      await sendChatMessage(message);


    removeLoadingMessage();


    appendAssistantMessage(
      response?.answer ||
        "I could not generate a response for that request."
    );


    renderRecommendedSchemes(
      response
    );
  }


  catch (error) {
    removeLoadingMessage();

    showError(
      error.message
    );
  }


  finally {
    setLoading(false);

    messageInput.focus();
  }
}


chatForm.addEventListener(
  "submit",
  handleSubmit
);


messageInput.addEventListener(
  "keydown",
  (event) => {

    if (
      event.key === "Enter" &&
      !event.shiftKey &&
      !event.isComposing
    ) {

      event.preventDefault();

      chatForm.requestSubmit();
    }
  }
);


for (const chip of promptChips) {

  chip.addEventListener(
    "click",
    () => {

      messageInput.value =
        chip.dataset.prompt || "";

      messageInput.focus();
    }
  );
}


appendAssistantMessage(
  "Hello! I am **Yojana Mitra**. Tell me about your situation, occupation, age, state, or the type of government support you are looking for. I will retrieve relevant schemes and return only grounded recommendations."
);