/* ============================================================
   AI SAARTHI FRONTEND
============================================================ */


/* ============================================================
   ELEMENTS
============================================================ */

const messageInput =
    document.getElementById("messageInput");

const sendBtn =
    document.getElementById("sendBtn");

const messages =
    document.getElementById("messages");

const welcomeScreen =
    document.getElementById("welcomeScreen");

const newChatBtn =
    document.getElementById("newChatBtn");

const themeBtn =
    document.getElementById("themeBtn");

const themeIcon =
    document.getElementById("themeIcon");

const historyList =
    document.getElementById("historyList");

const menuBtn =
    document.getElementById("menuBtn");

const closeSidebar =
    document.getElementById("closeSidebar");

const sidebar =
    document.getElementById("sidebar");

const sidebarOverlay =
    document.getElementById("sidebarOverlay");


/* ============================================================
   STATE
============================================================ */

let isLoading = false;

let conversations = [];

let currentConversation = [];


/* ============================================================
   INITIALIZE
============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadTheme();

        setupSuggestionCards();

        setupInput();

        setupSidebar();

        setupTheme();

    }
);


/* ============================================================
   SUGGESTION CARDS
============================================================ */

function setupSuggestionCards() {

    const cards =
        document.querySelectorAll(
            ".suggestion-card"
        );


    cards.forEach(card => {

        card.addEventListener(
            "click",
            () => {

                const message =
                    card.dataset.message;

                messageInput.value =
                    message;

                autoResize();

                sendMessage();

            }
        );

    });

}


/* ============================================================
   INPUT
============================================================ */

function setupInput() {

    messageInput.addEventListener(
        "input",
        autoResize
    );


    messageInput.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();

            }

        }
    );


    sendBtn.addEventListener(
        "click",
        sendMessage
    );

}


function autoResize() {

    messageInput.style.height =
        "auto";


    messageInput.style.height =
        Math.min(
            messageInput.scrollHeight,
            150
        ) + "px";

}


/* ============================================================
   SEND MESSAGE
============================================================ */

async function sendMessage() {

    if (isLoading) {
        return;
    }


    const message =
        messageInput.value.trim();


    if (!message) {
        return;
    }


    /* Hide welcome screen */

    welcomeScreen.style.display =
        "none";


    /* Add user message */

    addMessage(
        "user",
        message
    );


    /* Save conversation */

    currentConversation.push({

        role: "user",

        content: message

    });


    /* Clear input */

    messageInput.value = "";

    autoResize();


    /* Loading */

    setLoading(true);


    const typingId =
        showTyping();


    try {

        const response =
            await fetch(
                "/chat",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        message: message

                    })

                }
            );


        removeTyping(
            typingId
        );


        if (!response.ok) {

            const error =
                await response.json()
                    .catch(
                        () => ({})
                    );

            throw new Error(
                error.detail ||
                "Something went wrong."
            );

        }


        const data =
            await response.json();


        /* Display response */

        addAssistantMessage(
            data
        );


        /* Save conversation */

        currentConversation.push({

            role: "assistant",

            content:
                data.response

        });


        saveConversation();


    }

    catch (error) {

        removeTyping(
            typingId
        );


        console.error(
            error
        );


        addMessage(

            "assistant",

            "I'm having trouble connecting to Saarthi right now. Please make sure the FastAPI server is running and try again."

        );

    }


    finally {

        setLoading(false);

    }

}


/* ============================================================
   ADD USER MESSAGE
============================================================ */

function addMessage(
    role,
    text
) {

    const message =
        document.createElement(
            "div"
        );


    message.className =
        `message ${role}`;


    const avatar =
        document.createElement(
            "div"
        );

    avatar.className =
        "message-avatar";

    avatar.textContent =
        role === "user"
            ? "👤"
            : "🌱";


    const content =
        document.createElement(
            "div"
        );

    content.className =
        "message-content";


    const label =
        document.createElement(
            "div"
        );

    label.className =
        "message-label";

    label.textContent =
        role === "user"
            ? "You"
            : "Saarthi";


    const bubble =
        document.createElement(
            "div"
        );

    bubble.className =
        "message-bubble";

    bubble.textContent =
        text;


    content.appendChild(
        label
    );

    content.appendChild(
        bubble
    );


    message.appendChild(
        avatar
    );

    message.appendChild(
        content
    );


    messages.appendChild(
        message
    );


    scrollToBottom();

}


/* ============================================================
   ASSISTANT MESSAGE
============================================================ */

function addAssistantMessage(
    data
) {

    const message =
        document.createElement(
            "div"
        );

    message.className =
        "message assistant";


    const avatar =
        document.createElement(
            "div"
        );

    avatar.className =
        "message-avatar";

    avatar.textContent =
        "🌱";


    const content =
        document.createElement(
            "div"
        );

    content.className =
        "message-content";


    const label =
        document.createElement(
            "div"
        );

    label.className =
        "message-label";

    label.textContent =
        "Saarthi";


    const bubble =
        document.createElement(
            "div"
        );

    bubble.className =
        "message-bubble";

    bubble.textContent =
        data.response || "I couldn't generate a response.";


    content.appendChild(
        label
    );

    content.appendChild(
        bubble
    );


    /* Sources */

    if (
        data.sources &&
        data.sources.length > 0
    ) {

        const sources =
            createSources(
                data.sources
            );

        content.appendChild(
            sources
        );

    }


    message.appendChild(
        avatar
    );

    message.appendChild(
        content
    );


    messages.appendChild(
        message
    );


    scrollToBottom();

}


/* ============================================================
   CREATE SOURCE CARDS
============================================================ */

function createSources(
    sourceData
) {

    const wrapper =
        document.createElement(
            "div"
        );

    wrapper.className =
        "sources";


    const heading =
        document.createElement(
            "div"
        );

    heading.className =
        "message-label";

    heading.textContent =
        "📖 Gita passages";


    wrapper.appendChild(
        heading
    );


    sourceData.forEach(
        source => {

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "source-card";


            const top =
                document.createElement(
                    "div"
                );

            top.className =
                "source-top";


            const title =
                document.createElement(
                    "div"
                );

            title.className =
                "source-title";

            title.textContent =
                source.chapter_title ||
                `Chapter ${source.chapter || ""}`;


            const verse =
                document.createElement(
                    "div"
                );

            verse.className =
                "source-verse";

            verse.textContent =
                `Verse ${source.verse || "—"}`;


            top.appendChild(
                title
            );

            top.appendChild(
                verse
            );


            const score =
                document.createElement(
                    "div"
                );

            score.className =
                "source-score";

            if (
                typeof source.score ===
                "number"
            ) {

                score.textContent =
                    `Relevance ${(
                        source.score * 100
                    ).toFixed(1)}%`;

            }


            card.appendChild(
                top
            );

            card.appendChild(
                score
            );


            wrapper.appendChild(
                card
            );

        }
    );


    return wrapper;

}


/* ============================================================
   TYPING INDICATOR
============================================================ */

function showTyping() {

    const id =
        "typing-" +
        Date.now();


    const message =
        document.createElement(
            "div"
        );

    message.className =
        "message assistant";

    message.id =
        id;


    const avatar =
        document.createElement(
            "div"
        );

    avatar.className =
        "message-avatar";

    avatar.textContent =
        "🌱";


    const content =
        document.createElement(
            "div"
        );

    content.className =
        "message-content";


    const label =
        document.createElement(
            "div"
        );

    label.className =
        "message-label";

    label.textContent =
        "Saarthi is reflecting...";


    const bubble =
        document.createElement(
            "div"
        );

    bubble.className =
        "message-bubble typing-bubble";


    for (
        let i = 0;
        i < 3;
        i++
    ) {

        const dot =
            document.createElement(
                "span"
            );

        dot.className =
            "typing-dot";

        bubble.appendChild(
            dot
        );

    }


    content.appendChild(
        label
    );

    content.appendChild(
        bubble
    );


    message.appendChild(
        avatar
    );

    message.appendChild(
        content
    );


    messages.appendChild(
        message
    );


    scrollToBottom();


    return id;

}


function removeTyping(id) {

    const element =
        document.getElementById(
            id
        );


    if (element) {

        element.remove();

    }

}


/* ============================================================
   LOADING STATE
============================================================ */

function setLoading(
    state
) {

    isLoading =
        state;


    sendBtn.disabled =
        state;

}


/* ============================================================
   SCROLL
============================================================ */

function scrollToBottom() {

    const chatArea =
        document.getElementById(
            "chatArea"
        );


    setTimeout(
        () => {

            chatArea.scrollTo({

                top:
                    chatArea.scrollHeight,

                behavior:
                    "smooth"

            });

        },
        50
    );

}


/* ============================================================
   NEW CHAT
============================================================ */

newChatBtn.addEventListener(
    "click",
    startNewChat
);


function startNewChat() {

    if (
        currentConversation.length >
        0
    ) {

        saveConversation();

    }


    currentConversation = [];


    messages.innerHTML =
        "";


    welcomeScreen.style.display =
        "block";


    messageInput.value =
        "";

    autoResize();


    closeSidebarMobile();

}


/* ============================================================
   SAVE CONVERSATION
============================================================ */

function saveConversation() {

    if (
        currentConversation.length <
        2
    ) {

        return;

    }


    const firstMessage =
        currentConversation.find(
            item =>
                item.role === "user"
        );


    if (!firstMessage) {
        return;
    }


    const conversation = {

        id:
            Date.now(),

        title:
            firstMessage.content
                .substring(0, 45),

        messages:
            [...currentConversation]

    };


    conversations.push(
        conversation
    );


    if (
        conversations.length >
        10
    ) {

        conversations.shift();

    }


    localStorage.setItem(
        "saarthi_conversations",
        JSON.stringify(
            conversations
        )
    );


    renderHistory();

}


/* ============================================================
   LOAD HISTORY
============================================================ */

function loadConversations() {

    const saved =
        localStorage.getItem(
            "saarthi_conversations"
        );


    if (!saved) {
        return;
    }


    try {

        conversations =
            JSON.parse(saved);

        renderHistory();

    }

    catch (error) {

        console.error(
            "Could not load conversations",
            error
        );

    }

}


function renderHistory() {

    historyList.innerHTML =
        "";


    if (
        conversations.length ===
        0
    ) {

        historyList.innerHTML =

            `<div class="empty-history">
                Your conversations will appear here.
            </div>`;

        return;

    }


    [...conversations]
        .reverse()
        .forEach(
            conversation => {

                const item =
                    document.createElement(
                        "button"
                    );

                item.className =
                    "history-item";

                item.textContent =
                    conversation.title;


                item.addEventListener(
                    "click",
                    () => {

                        loadConversation(
                            conversation
                        );

                    }
                );


                historyList.appendChild(
                    item
                );

            }
        );

}


function loadConversation(
    conversation
) {

    messages.innerHTML =
        "";

    welcomeScreen.style.display =
        "none";


    currentConversation =
        [
            ...conversation.messages
        ];


    conversation.messages.forEach(
        item => {

            if (
                item.role ===
                "user"
            ) {

                addMessage(
                    "user",
                    item.content
                );

            }

            else {

                addMessage(
                    "assistant",
                    item.content
                );

            }

        }
    );


    closeSidebarMobile();

}


/* ============================================================
   THEME
============================================================ */

function setupTheme() {

    themeBtn.addEventListener(
        "click",
        toggleTheme
    );

}


function toggleTheme() {

    document.body.classList.toggle(
        "dark"
    );


    const isDark =
        document.body.classList.contains(
            "dark"
        );


    localStorage.setItem(
        "saarthi_theme",
        isDark
            ? "dark"
            : "light"
    );


    updateThemeIcon();

}


function loadTheme() {

    const theme =
        localStorage.getItem(
            "saarthi_theme"
        );


    if (theme === "dark") {

        document.body.classList.add(
            "dark"
        );

    }


    updateThemeIcon();

    loadConversations();

}


function updateThemeIcon() {

    const isDark =
        document.body.classList.contains(
            "dark"
        );


    themeIcon.textContent =
        isDark
            ? "☀"
            : "☾";

}


/* ============================================================
   MOBILE SIDEBAR
============================================================ */

function setupSidebar() {

    menuBtn.addEventListener(
        "click",
        () => {

            sidebar.classList.add(
                "open"
            );

            sidebarOverlay.classList.add(
                "active"
            );

        }
    );


    closeSidebar.addEventListener(
        "click",
        closeSidebarMobile
    );


    sidebarOverlay.addEventListener(
        "click",
        closeSidebarMobile
    );

}


function closeSidebarMobile() {

    sidebar.classList.remove(
        "open"
    );

    sidebarOverlay.classList.remove(
        "active"
    );

}