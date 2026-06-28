document.addEventListener("DOMContentLoaded", () => {
    // API URL Configurations
    const API_BASE = ""; // Relative to the served page
    
    // DOM Elements
    const docList = document.getElementById("doc-list");
    const refreshDocsBtn = document.getElementById("refresh-docs-btn");
    const uploadDropzone = document.getElementById("upload-dropzone");
    const fileInput = document.getElementById("file-input");
    const uploadStatus = document.getElementById("upload-status");
    
    const chatLog = document.getElementById("chat-log");
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const clearChatBtn = document.getElementById("clear-chat-btn");

    // Enable/disable send button based on input text
    userInput.addEventListener("input", () => {
        sendBtn.disabled = userInput.value.trim() === "";
    });

    // Fetch and display documents in sidebar
    async function loadDocuments() {
        try {
            const res = await fetch(`${API_BASE}/documents`);
            if (!res.ok) throw new Error("Failed to load documents");
            
            const docs = await res.json();
            
            if (docs.length === 0) {
                docList.innerHTML = `<div class="doc-loading">No documents ingested yet.<br><small style="color:var(--text-muted)">Generate or upload files to start.</small></div>`;
                return;
            }
            
            docList.innerHTML = "";
            docs.forEach(doc => {
                const docItem = document.createElement("div");
                docItem.className = "doc-item";
                docItem.innerHTML = `
                    <div class="doc-info">
                        <i class="fa-solid fa-file-pdf"></i>
                        <div style="overflow: hidden;">
                            <div class="doc-name" title="${doc.filename}">${doc.filename}</div>
                            <div class="doc-meta">
                                <span>${doc.max_page} pages</span>
                                <span>•</span>
                                <span>${doc.chunk_count} chunks</span>
                            </div>
                        </div>
                    </div>
                    <button class="doc-delete" data-filename="${doc.filename}" title="Delete document">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                `;
                docList.appendChild(docItem);
            });
            
            // Add Delete Listeners
            document.querySelectorAll(".doc-delete").forEach(btn => {
                btn.addEventListener("click", async (e) => {
                    const filename = e.currentTarget.getAttribute("data-filename");
                    if (confirm(`Are you sure you want to delete ${filename}? This will remove it from the knowledge base.`)) {
                        await deleteDocument(filename);
                    }
                });
            });
            
        } catch (error) {
            console.error("Error loading documents:", error);
            docList.innerHTML = `<div class="doc-loading" style="color:var(--danger-color)">Error loading documents.</div>`;
        }
    }

    // Delete Document API Call
    async function deleteDocument(filename) {
        try {
            const res = await fetch(`${API_BASE}/document/${encodeURIComponent(filename)}`, {
                method: "DELETE"
            });
            const data = await res.json();
            if (res.ok) {
                showUploadStatus(`Deleted ${filename}`, "success");
                loadDocuments();
            } else {
                showUploadStatus(data.detail || "Delete failed", "error");
            }
        } catch (err) {
            console.error(err);
            showUploadStatus("Network error deleting document", "error");
        }
    }

    // Helper to show upload status messages
    function showUploadStatus(message, type) {
        uploadStatus.className = `upload-status ${type}`;
        uploadStatus.textContent = message;
        uploadStatus.style.display = "block";
        setTimeout(() => {
            uploadStatus.style.display = "none";
        }, 5000);
    }

    // File Upload triggers
    uploadDropzone.addEventListener("click", () => fileInput.click());
    
    uploadDropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadDropzone.classList.add("dragover");
    });
    
    uploadDropzone.addEventListener("dragleave", () => {
        uploadDropzone.classList.remove("dragover");
    });
    
    uploadDropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadDropzone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });
    
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            handleFileUpload(fileInput.files[0]);
        }
    });

    // Upload file API call
    async function handleFileUpload(file) {
        const allowedExtensions = /(\.pdf|\.txt|\.md)$/i;
        if (!allowedExtensions.exec(file.name)) {
            showUploadStatus("Only PDF, TXT, and MD files are supported.", "error");
            return;
        }

        if (file.size > 10 * 1024 * 1024) { // 10MB
            showUploadStatus("File is too large (Max 10MB).", "error");
            return;
        }

        showUploadStatus(`Uploading ${file.name}...`, "info");
        
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch(`${API_BASE}/upload`, {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            if (res.ok) {
                showUploadStatus("File uploaded and ingested successfully!", "success");
                loadDocuments();
            } else {
                showUploadStatus(data.detail || "Upload failed", "error");
            }
        } catch (err) {
            console.error(err);
            showUploadStatus("Network error uploading file", "error");
        }
    }

    // Handle suggested queries click
    document.querySelectorAll(".suggest-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const query = e.target.getAttribute("data-query");
            userInput.value = query;
            sendBtn.disabled = false;
            submitQuestion(query);
        });
    });

    // Clear chat conversation
    clearChatBtn.addEventListener("click", () => {
        const firstMsg = chatLog.querySelector(".welcome-msg");
        chatLog.innerHTML = "";
        if (firstMsg) {
            chatLog.appendChild(firstMsg);
        }
    });

    // Form submit listener
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (text) {
            submitQuestion(text);
        }
    });

    // Submit question and query API
    async function submitQuestion(question) {
        userInput.value = "";
        sendBtn.disabled = true;
        
        // Add User Message Bubble
        addUserBubble(question);
        
        // Scroll to bottom
        chatLog.scrollTop = chatLog.scrollHeight;
        
        // Add Loading Skeleton Bubble
        const loadingId = addSkeletonBubble();
        chatLog.scrollTop = chatLog.scrollHeight;
        
        try {
            const res = await fetch(`${API_BASE}/ask`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ question })
            });
            
            const data = await res.json();
            
            // Remove skeleton loading
            removeBubble(loadingId);
            
            if (res.ok) {
                addAssistantBubble(data);
            } else {
                addErrorBubble(data.detail || "Failed to generate response.");
            }
        } catch (err) {
            console.error(err);
            removeBubble(loadingId);
            addErrorBubble("A network error occurred. Please check if the server is running.");
        }
        
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    // Add User Bubble to chat log
    function addUserBubble(text) {
        const bubble = document.createElement("div");
        bubble.className = "message user-message";
        bubble.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-user"></i></div>
            <div class="message-content">
                <p>${escapeHTML(text)}</p>
            </div>
        `;
        chatLog.appendChild(bubble);
    }

    // Add Loading Skeleton
    function addSkeletonBubble() {
        const id = "skeleton_" + Date.now();
        const bubble = document.createElement("div");
        bubble.className = "message assistant-message skeleton-msg";
        bubble.id = id;
        bubble.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="message-content">
                <div class="skeleton-line"></div>
                <div class="skeleton-line"></div>
                <div class="skeleton-line"></div>
            </div>
        `;
        chatLog.appendChild(bubble);
        return id;
    }

    // Remove Bubble
    function removeBubble(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    // Add Assistant Bubble with answers and citations
    function addAssistantBubble(data) {
        const bubble = document.createElement("div");
        bubble.className = "message assistant-message";
        
        // Calculate confidence rating
        let confClass = "confidence-high";
        let confRating = "High";
        if (data.confidence < 0.4) {
            confClass = "confidence-low";
            confRating = "Low";
        } else if (data.confidence < 0.75) {
            confClass = "confidence-medium";
            confRating = "Medium";
        }
        
        // Format answer content (support simple bold elements)
        let formattedAnswer = escapeHTML(data.answer)
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code>$1</code>');
            
        // Build citations list
        let citationsHTML = "";
        let sourcesToggleHTML = "";
        
        if (data.sources && data.sources.length > 0) {
            const uniqueId = "cit_" + Date.now();
            sourcesToggleHTML = `
                <button class="citations-toggle" data-target="${uniqueId}">
                    <i class="fa-solid fa-angle-right"></i> Cited Sources (${data.sources.length})
                </button>
            `;
            
            let listItems = data.sources.map(src => `
                <div class="citation-item">
                    <i class="fa-solid fa-file-pdf"></i>
                    <span class="citation-doc">${escapeHTML(src.document)}</span>
                    <span class="citation-page">Page ${src.page}</span>
                </div>
            `).join("");
            
            citationsHTML = `
                <div class="citations-container" id="${uniqueId}">
                    <div class="citations-title">Sources used in this response</div>
                    <div class="citations-list">
                        ${listItems}
                    </div>
                </div>
            `;
        }

        bubble.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="message-content">
                <p>${formattedAnswer}</p>
                <div class="meta-panel">
                    <div class="confidence-badge ${confClass}">
                        <i class="fa-solid fa-shield-halved"></i>
                        <span>Confidence: ${confRating} (${Math.round(data.confidence * 100)}%)</span>
                    </div>
                    ${sourcesToggleHTML}
                </div>
                ${citationsHTML}
            </div>
        `;
        
        chatLog.appendChild(bubble);
        
        // Add Toggle listener
        if (data.sources && data.sources.length > 0) {
            const toggleBtn = bubble.querySelector(".citations-toggle");
            const container = bubble.querySelector(".citations-container");
            toggleBtn.addEventListener("click", () => {
                const isVisible = container.style.display === "block";
                container.style.display = isVisible ? "none" : "block";
                toggleBtn.querySelector("i").className = isVisible ? "fa-solid fa-angle-right" : "fa-solid fa-angle-down";
                chatLog.scrollTop = chatLog.scrollHeight;
            });
        }
    }

    // Add Error Bubble
    function addErrorBubble(errorText) {
        const bubble = document.createElement("div");
        bubble.className = "message assistant-message";
        bubble.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-circle-exclamation" style="color:var(--danger-color)"></i></div>
            <div class="message-content">
                <p style="color:var(--danger-color)"><strong>System Error:</strong> ${escapeHTML(errorText)}</p>
            </div>
        `;
        chatLog.appendChild(bubble);
    }

    // Simple HTML escaper
    function escapeHTML(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Initializations
    refreshDocsBtn.addEventListener("click", loadDocuments);
    loadDocuments();
});
