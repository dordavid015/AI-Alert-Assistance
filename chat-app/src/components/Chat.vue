<template>
  <div class="chat-container">
    <div class="chat-box">
      <div v-for="(message, index) in chatMessages" :key="index" :class="message.fromUser ? 'user-message' : 'server-message'">
        <p>{{ message.text }}</p>
      </div>
    </div>
    <div class="chat-input">
      <input v-model="newMessage" @keyup.enter="sendMessage" placeholder="Type your message..." />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['chatId'], // Get the chatId from the URL
  data() {
    return {
      chatMessages: [],
      newMessage: '',
    };
  },
  mounted() {
    // If the chatId is present in the URL, treat it as the user's first message
    if (this.chatId) {
      const initialMessage = decodeURIComponent(this.chatId).replace(/%3A/g, ':');
      this.chatMessages.push({
        text: initialMessage,
        fromUser: true,
      });
      this.sendMessageToServer(); // Send the first message to the server
    }
  },
  methods: {
    sendMessage() {
      if (this.newMessage.trim() === '') return;

      // Add the user's message to the chat
      this.chatMessages.push({
        text: this.newMessage,
        fromUser: true,
      });

      // Send the entire chat history to the server
      this.sendMessageToServer();
      this.newMessage = ''; // Clear the input field
    },
    async sendMessageToServer() {
      try {
        // Send the entire chat history (including the new message) to the server
        const response = await axios.post('http://localhost:5000/chat', {
          chatMessages: this.chatMessages,
        });

        // Add the server's response to the chat
        this.chatMessages.push({
          text: response.data.reply,
          fromUser: false,
        });
      } catch (error) {
        console.error('Error sending message to server:', error);
      }
    },
  },
};
</script>

<style scoped>
* {
  box-sizing: border-box;
}

body, html {
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
</style>
