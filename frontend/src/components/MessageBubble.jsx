import ReactMarkdown from "react-markdown";

function MessageBubble({ role, content }) {
  const isUser = role === "user";

  return (
    <div className={`message-row ${isUser ? "user-row" : "assistant-row"}`}>
      {!isUser && (
        <div className="assistant-avatar">
          YM
        </div>
      )}

      <div
        className={`message-bubble ${
          isUser ? "user-message" : "assistant-message"
        }`}
      >
        <div className="message-label">
          {isUser ? "You" : "Yojana Mitra"}
        </div>

        <div className="message-content">
          {isUser ? (
            content
          ) : (
            <ReactMarkdown>{content}</ReactMarkdown>
          )}
        </div>
      </div>
    </div>
  );
}

export default MessageBubble;