<template>
  <div class="chat-container">
    <div class="chat-box">
      <div
        v-for="(message, index) in chatMessages"
        :key="index"
        :class="message.role === 'user' ? 'user-message' : 'server-message'"
      >
        <p>{{ message.content }}</p>
      </div>
    </div>
    <div class="chat-input">
      <input
        v-model="newMessage"
        @keyup.enter="sendMessage"
        placeholder="Type your message..."
      />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
export default {
  props: ["chatId"],
  data() {
    return {
      chatMessages: [],
      newMessage: "",
      streamingMessageIndex: null, // Index of the message being streamed
    };
  },
  mounted() {
    if (this.chatId) {
      const initialMessage = decodeURIComponent(this.chatId).replace(
        /%3A/g,
        ":"
      );
      this.chatMessages.push({
        role: "user",
        content: initialMessage,
      });
      this.sendMessageToServer();
    }
  },
  methods: {
    sendMessage() {
      if (this.newMessage.trim() === "") return;

      this.chatMessages.push({
        role: "user",
        content: this.newMessage,
      });

      this.sendMessageToServer();
      this.newMessage = "";
    },
    async sendMessageToServer() {
      const params = new URLSearchParams({
        chatMessages: JSON.stringify(this.chatMessages),
      });

      const eventSource = new EventSource(
        `http://localhost:5000/message_stream?${params.toString()}`
      );

      // Add a placeholder message while waiting for the server's response
      const placeholderIndex = this.chatMessages.length;
      this.chatMessages.push({
        role: "system",
        content: "...", // Placeholder message
      });

      let streamingContent = "";

      eventSource.onmessage = (event) => {
        const data = event.data;

        // Replace the placeholder message with the actual content
        if (this.chatMessages[placeholderIndex].content === "...") {
          this.$set(this.chatMessages, placeholderIndex, {
            role: "system",
            content: "",
          });
        }

        streamingContent += data;

        // Update the message with the streamed content
        this.$set(this.chatMessages, placeholderIndex, {
          role: "system",
          content: streamingContent,
        });

        // Scroll to the latest message
        this.$nextTick(() => {
          const chatBox = document.querySelector(".chat-box");
          chatBox.scrollTop = chatBox.scrollHeight;
        });
      };

      eventSource.onerror = (error) => {
        console.error("Error streaming response:", error);
        eventSource.close();
      };
    },
  },
};
</script>

<style scoped>
* {
  box-sizing: border-box;
}

body,
html {
  margin: 0;
  padding: 0;
  height: 100%;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%; /* Ensure the container takes up full height */
}

.chat-box {
  flex-grow: 1; /* Chat box takes available space */
  overflow-y: auto; /* Enable scrolling if the messages exceed the screen height */
  padding: 20px;
  background-color: #f9f9f9;
  border-bottom: 1px solid #ccc;
}

.chat-input {
  position: absolute;
  bottom: 0;
  width: 100%;
  padding: 10px;
  background-color: #fff;
  border-top: 1px solid #ccc;
  display: flex;
  justify-content: space-between; /* Align input and button */
  box-sizing: border-box;
}

.chat-input input {
  width: 85%; /* Input field takes most of the width */
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.chat-input button {
  width: 15%; /* Button takes up remaining width */
  padding: 10px;
  margin-left: 5px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
}

/* Style for user messages */
.user-message {
  text-align: right;
  background-color: #d1e7dd;
  padding: 8px;
  margin-bottom: 5px;
  border-radius: 5px;
  max-width: 75%; /* Limit the width of the user's message */
  margin-left: auto; /* Align the user's messages to the right */
}

/* Style for server messages */
.server-message {
  text-align: left;
  background-color: #f8d7da;
  padding: 8px;
  margin-bottom: 5px;
  border-radius: 5px;
  max-width: 75%; /* Limit the width of the server's message */
  margin-right: auto; /* Align the server's messages to the left */
}

.user-message,
.server-message {
  white-space: pre-wrap; /* Preserve line breaks and wrap text */
  word-wrap: break-word; /* Ensure long words wrap */
}
</style>
