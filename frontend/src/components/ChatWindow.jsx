import { useState } from "react";

import { sendChatMessage } from "../api";
import MessageBubble from "./MessageBubble";
import SchemeCard from "./SchemeCard";

function ChatWindow() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I am Yojana Mitra. Tell me about your situation, occupation, age, state, or the type of government support you are looking for.",
    },
  ]);

  const [input, setInput] = useState("");
  const [recommendedSchemes, setRecommendedSchemes] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    const message = input.trim();

    if (!message || isLoading) {
      return;
    }

    setError("");
    setInput("");
    setRecommendedSchemes([]);

    setMessages((currentMessages) => [
      ...currentMessages,
      {
        role: "user",
        content: message,
      },
    ]);

    setIsLoading(true);

    try {
      const response = await sendChatMessage(message);

      const recommendedIds =
        response.grounding?.recommendedSchemeIds || [];

      const filteredSchemes = (response.schemes || []).filter((scheme) =>
        recommendedIds.includes(scheme.id)
      );

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "assistant",
          content: response.answer,
        },
      ]);

      setRecommendedSchemes(filteredSchemes);
    } catch (requestError) {
      setError(
        requestError.message ||
          "Something went wrong while contacting Yojana Mitra."
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="chat-window">
      <div className="chat-header">
        <div>
          <p className="eyebrow">Government Scheme Assistant</p>
          <h1>Yojana Mitra</h1>
          <p className="chat-subtitle">
            Find relevant government schemes using grounded AI.
          </p>
        </div>

        <div className="status-pill">
          <span className="status-dot" />
          Grounded AI
        </div>
      </div>

      <div className="messages-area">
        {messages.map((message, index) => (
          <MessageBubble
            key={`${message.role}-${index}`}
            role={message.role}
            content={message.content}
          />
        ))}

        {isLoading && (
          <div className="loading-message">
            Yojana Mitra is checking relevant schemes...
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </div>

      {recommendedSchemes.length > 0 && (
        <div className="recommended-section">
          <div className="section-heading">
            <p className="eyebrow">Grounded Recommendations</p>
            <h2>Relevant schemes</h2>
          </div>

          <div className="scheme-grid">
            {recommendedSchemes.map((scheme) => (
              <SchemeCard
                key={scheme.id}
                scheme={scheme}
              />
            ))}
          </div>
        </div>
      )}

      <form
        className="chat-input-area"
        onSubmit={handleSubmit}
      >
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Example: I am a farmer and need crop insurance..."
          rows="3"
          disabled={isLoading}
        />

        <button
          type="submit"
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? "Checking..." : "Ask Yojana Mitra"}
        </button>
      </form>

      <p className="disclaimer">
        Yojana Mitra provides scheme discovery assistance. Always verify final
        eligibility and current conditions through official government sources.
      </p>
    </section>
  );
}

export default ChatWindow;