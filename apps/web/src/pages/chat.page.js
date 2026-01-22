import { listRooms, listMessages } from "../api/chat.api.js";

export function renderChat(container, goBack) {
  container.innerHTML = `
    <div class="topbar">
      <div>
        <h1 class="h1" style="margin:0">Chat</h1>
        <p class="small" style="margin-top:6px">WebSocket live chat + message history.</p>
      </div>
      <div class="topActions">
        <button class="btn" id="backBtn" type="button">Back</button>
      </div>
    </div>

    <div id="msg" class="msg" aria-live="polite"></div>

    <div class="section" style="border-top:none; padding-top:0">
      <div class="row">
        <div class="field" style="flex:1; min-width:200px">
          <label>Room</label>
          <input id="roomInput" value="general" />
        </div>
        <div class="field" style="flex:1; min-width:200px">
          <label>User</label>
          <input id="userInput" value="${escapeHtml(getJwtSub() || "anonymous")}" />
        </div>
        <div style="display:flex; align-items:flex-end; gap:10px">
          <button class="btn" id="roomsBtn" type="button">Rooms</button>
          <button class="btn" id="historyBtn" type="button">Load history</button>
          <button class="btn primary" id="connectBtn" type="button">Connect</button>
        </div>
      </div>

      <div id="chatBox" class="chatBox">Not connected.</div>

      <div class="row" style="margin-top:12px">
        <div class="field" style="flex:1; min-width:240px">
          <label>Message</label>
          <input id="textInput" placeholder="Type and hit Send..." />
        </div>
        <div style="display:flex; align-items:flex-end; gap:10px">
          <button class="btn primary" id="sendBtn" type="button">Send</button>
        </div>
      </div>
    </div>
  `;

  const msg = container.querySelector("#msg");
  const chatBox = container.querySelector("#chatBox");
  const roomInput = container.querySelector("#roomInput");
  const userInput = container.querySelector("#userInput");
  const textInput = container.querySelector("#textInput");
  const connectBtn = container.querySelector("#connectBtn");

  let ws = null;

  const setMsg = (text, ok) => {
    msg.className = `msg ${ok ? "ok" : "bad"}`;
    msg.textContent = text;
  };

  const appendLine = (who, text, ts, type = "message") => {
    const line = document.createElement("div");
    line.className = "bubble";
    line.innerHTML = `
      <div class="bubbleTop">
        <span class="bubbleWho">${escapeHtml(who)}</span>
        <span class="bubbleAt">${escapeHtml(ts || "")}</span>
      </div>
      <div class="bubbleText">${escapeHtml(type === "system" ? `[system] ${text}` : text)}</div>
    `;
    chatBox.appendChild(line);
    chatBox.scrollTop = chatBox.scrollHeight;
  };

  const setConnectedUI = (connected) => {
    connectBtn.textContent = connected ? "Disconnect" : "Connect";
    setMsg(connected ? "Connected ✅" : "Disconnected.", true);
  };

  function wsUrl(room, user) {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    // Use Vite proxy (same host/port as frontend)
    const qs = new URLSearchParams({ room, user }).toString();
    return `${proto}://${location.host}/chat/ws?${qs}`;
  }

  function connect() {
    const room = roomInput.value.trim() || "general";
    const user = userInput.value.trim() || "anonymous";

    chatBox.innerHTML = "";
    chatBox.textContent = "Connecting...";

    try {
      ws = new WebSocket(wsUrl(room, user));
    } catch (e) {
      setMsg(`WebSocket failed: ${e.message}`, false);
      return;
    }

    ws.onopen = () => {
      chatBox.textContent = "";
      setConnectedUI(true);
      appendLine("system", `Connected to room "${room}" as "${user}"`, nowIso(), "system");
    };

    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);

        if (data.type === "system") {
          appendLine("system", data.message || "", data.ts || "", "system");
          return;
        }

        if (data.type === "message") {
          appendLine(data.user || "user", data.message || "", data.ts || "", "message");
          return;
        }

        // Fallback
        appendLine("system", ev.data, nowIso(), "system");
      } catch {
        appendLine("system", ev.data, nowIso(), "system");
      }
    };

    ws.onclose = () => {
      ws = null;
      setConnectedUI(false);
      appendLine("system", "Disconnected.", nowIso(), "system");
    };

    ws.onerror = () => {
      setMsg("WebSocket error (check proxy / service).", false);
    };
  }

  function disconnect() {
    if (ws) ws.close();
    ws = null;
    setConnectedUI(false);
  }

  async function loadHistory() {
    const room = roomInput.value.trim() || "general";
    setMsg("Loading history...", true);
    chatBox.innerHTML = "";
    chatBox.textContent = "Loading...";

    try {
      const data = await listMessages(room, 100);
      const items = data?.items ?? [];
      chatBox.textContent = "";
      items.forEach((m) => appendLine(m.user, m.message, m.created_at));
      setMsg(`History loaded ✅ (${items.length})`, true);
    } catch (e) {
      setMsg(`History failed: ${e.message}`, false);
      chatBox.textContent = "Failed to load history.";
    }
  }

  function send() {
    const text = textInput.value.trim();
    if (!text) return;

    if (!ws || ws.readyState !== WebSocket.OPEN) {
      setMsg("Not connected. Click Connect first.", false);
      return;
    }

    ws.send(text);
    textInput.value = "";
    textInput.focus();
  }

  container.querySelector("#backBtn").onclick = () => {
    if (ws) ws.close();
    goBack();
  };

  container.querySelector("#connectBtn").onclick = () => {
    if (ws && ws.readyState === WebSocket.OPEN) disconnect();
    else connect();
  };

  container.querySelector("#sendBtn").onclick = send;
  textInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") send();
  });

  container.querySelector("#historyBtn").onclick = loadHistory;

  container.querySelector("#roomsBtn").onclick = async () => {
    setMsg("Loading rooms...", true);
    try {
      const rooms = await listRooms();
      const text = Array.isArray(rooms) && rooms.length
        ? rooms.map((r) => `${r.room} (${r.connections})`).join(" | ")
        : "No rooms.";
      setMsg(text, true);
    } catch (e) {
      setMsg(`Rooms failed: ${e.message}`, false);
    }
  };
}

function getJwtSub() {
  try {
    const token = localStorage.getItem("token");
    if (!token) return "";
    const payload = token.split(".")[1];
    const json = JSON.parse(atob(payload.replaceAll("-", "+").replaceAll("_", "/")));
    return json.sub || "";
  } catch {
    return "";
  }
}

function nowIso() {
  return new Date().toISOString();
}

function escapeHtml(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
