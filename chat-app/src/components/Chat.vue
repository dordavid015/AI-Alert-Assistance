<template>
  <div class="chat-container">
    <div id="chatHistory" class="chat-history">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['message', message.role === 'user' ? 'user-message' : 'assistant-message']"
      >
        <div v-if="message.role === 'assistant'" class="formatted-response">
          <pre>{{ message.content }}</pre>
        </div>
        <div v-else v-html="message.content"></div>
        <div class="timestamp">{{ formatTimestamp(message.timestamp) }}</div>
      </div>
    </div>
    <div class="input-area">
      <textarea
        v-model="questionInput"
        id="questionInput"
        placeholder="Type your message..."
        rows="2"
        @keydown.enter.prevent="handleEnter"
      ></textarea>
      <button
        id="askButton"
        :disabled="isLoading || !questionInput.trim()"
        @click="askQuestion"
      >
        Send
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    suburl: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      messages: [],
      questionInput: '',
      isLoading: false,
    };
  },
  async created() {
    if (this.suburl) {
      this.addMessage(this.suburl, 'user');
      this.askQuestion();
      await this.submitQuestions(this.suburl)
    }
  },
  methods: {
    addMessage(content, role) {
      this.messages.push({
        content,
        role,
        timestamp: new Date(),
      });
      this.$nextTick(() => {
        const chatHistory = this.$el.querySelector('#chatHistory');
        chatHistory.scrollTop = chatHistory.scrollHeight;
      });
    },
    async askQuestion() {
      if (!this.questionInput.trim() && !this.isLoading) return;

      const question = this.isLoading ? this.messages[this.messages.length - 1].content : this.questionInput.trim();
      if (!this.isLoading) {
        this.addMessage(question, 'user');
        this.questionInput = '';
      }
      await this.submitQuestions(question);
    },
    async submitQuestions(question) {
      this.isLoading = true;

      try {
        const response = await fetch('http://localhost:5000/dor', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: question,
            history: this.messages.map((msg) => ({
              role: msg.role,
              content: msg.content,
            })),
          }),
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullResponse = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const text = decoder.decode(value);
          fullResponse += text;
          this.updateLastMessage(fullResponse, 'assistant');
        }

        this.updateLastMessage(fullResponse, 'assistant', true);
      } catch (error) {
        console.error('Error:', error);
        this.addMessage('Error occurred while fetching response', 'assistant');
      } finally {
        this.isLoading = false;
      }
    },
    updateLastMessage(content, role, finalize = false) {
      const lastMessage = this.messages[this.messages.length - 1];
      if (lastMessage && lastMessage.role === role) {
        lastMessage.content = content;
        if (finalize) lastMessage.timestamp = new Date();
      } else {
        this.addMessage(content, role);
      }
    },
    handleEnter(e) {
      if (!e.shiftKey) this.askQuestion();
    },
    formatTimestamp(timestamp) {
      return new Date(timestamp).toLocaleTimeString();
    },
  },
};
</script>

<style scoped>
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 20px;
  background-color: #f0f0f0;
}
.chat-container {
  max-width: 800px;
  margin: 0 auto;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 90vh;
}
.chat-history {
  flex-grow: 1;
  overflow-y: auto;
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.message {
  margin-bottom: 15px;
  padding: 10px;
  border-radius: 8px;
  max-width: 80%;
}
.user-message {
  background-color: #007bff;
  color: white;
  margin-left: auto;
}
.assistant-message {
  background-color: #e9ecef;
  color: black;
  margin-right: auto;
}
.input-area {
  display: flex;
  gap: 10px;
}
#questionInput {
  flex-grow: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: none;
}
#askButton {
  background-color: #4caf50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
#askButton:hover {
  background-color: #45a049;
}
#askButton:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
.timestamp {
  font-size: 0.8em;
  color: #666;
  margin-top: 5px;
}

.formatted-response pre {
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  margin: 0;
  white-space: pre-wrap;
  font-family: Consolas, "Courier New", monospace;
  overflow-x: auto;
  text-align: left;
}
</style>
