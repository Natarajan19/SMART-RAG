
import { useEffect, useRef, useState } from "react";
import "./app.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [documentName, setDocumentName] = useState("");
  const [uploadError, setUploadError] = useState("");
  const fileInputRef = useRef(null);

  useEffect(() => {
    const loadDocument = async () => {
      try {
        const response = await fetch(`${API_URL}/document`);
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Could not load document status.");
        }

        setDocumentName(data.filename || "");
      } catch (error) {
        setUploadError(`Could not connect to SmartRAG: ${error.message}`);
      }
    };

    loadDocument();
  }, []);

  const uploadDocument = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "PDF upload failed.");
      }

      setDocumentName(data.filename);
      setMessages([]);
      setQuestion("");
    } catch (error) {
      setUploadError(error.message);
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };

  const sendQuestion = async () => {
    if (!question.trim() || loading || !documentName) return;

    const userQuestion = question.trim();

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userQuestion
      }
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/ask`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            question: userQuestion
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Something went wrong"
        );
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.source_pages || []
        }
      ]);

    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Error: " + error.message,
          sources: []
        }
      ]);

    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendQuestion();
    }
  };

  return (
    <div className="app">

      <aside className="sidebar">
        <h2>✦ SmartRAG</h2>

        <p className="sidebar-subtitle">
          AI Knowledge Assistant
        </p>

        <button
          className="new-chat"
          onClick={() => setMessages([])}
        >
          + New Chat
        </button>

        <button
          className="upload-button"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading || loading}
        >
          {uploading ? "Uploading PDF..." : documentName ? "Replace PDF" : "Upload PDF"}
        </button>
        <input
          ref={fileInputRef}
          className="file-input"
          type="file"
          accept="application/pdf,.pdf"
          onChange={uploadDocument}
        />

        <div className="sidebar-info">
          <p>DOCUMENT ASSISTANT</p>
          <span>{documentName || "No PDF uploaded"}</span>
          <span>ChromaDB Connected</span>
          <span>Gemini AI Powered</span>
        </div>

        <div className="sidebar-footer">
          SmartRAG v1.0
        </div>
      </aside>

      <main className="main">

        <header className="topbar">
          <div>
            <h3>Knowledge Assistant</h3>
            <p>
              {documentName
                ? `Ask questions about ${documentName}`
                : "Upload a PDF to get started"}
            </p>
          </div>

          <span className="status">
            ● Online
          </span>
        </header>

        <section className="chat-area">

          {messages.length === 0 && (
            <div className="welcome">
              <div className="welcome-icon">✦</div>

              <h1>{documentName ? "Your PDF is ready" : "Upload a PDF to get started"}</h1>

              <p>
                {documentName
                  ? `Ask anything about ${documentName}. SmartRAG will answer using its contents.`
                  : "Choose a PDF document and then ask questions about its contents."}
              </p>

              {!documentName && (
                <button
                  className="welcome-upload"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading}
                >
                  {uploading ? "Uploading PDF..." : "Choose PDF"}
                </button>
              )}
            </div>
          )}

          {uploadError && (
            <p className="upload-error" role="alert">
              {uploadError}
            </p>
          )}

          {messages.map((message, index) => (
            <div
              className={`message ${message.role}`}
              key={index}
            >
              <div className="avatar">
                {message.role === "user" ? "You" : "✦"}
              </div>

              <div className="message-content">
                <strong>
                  {message.role === "user"
                    ? "You"
                    : "SmartRAG"}
                </strong>

                <p>{message.content}</p>

                {message.sources &&
                  message.sources.length > 0 && (
                    <div className="sources">
                      📄 Source pages:{" "}
                      {message.sources.join(", ")}
                    </div>
                  )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="loading">
              ✦ SmartRAG is thinking...
            </div>
          )}

        </section>

        {documentName ? (
          <div className="input-section">
            <div className="input-box">
              <textarea
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                onKeyDown={handleKeyDown}
                placeholder="Ask anything about your PDF..."
                rows="1"
              />

              <button
                onClick={sendQuestion}
                disabled={loading || !question.trim()}
              >
                ↑
              </button>
            </div>

            <p>
              SmartRAG answers using your document context.
            </p>
          </div>
        ) : (
          <div className="input-placeholder">
            Upload a PDF to start asking questions.
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
