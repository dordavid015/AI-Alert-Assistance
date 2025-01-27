<template>
  <div class="chat-container">
    <div id="chatHistory" class="chat-history">
      <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role === 'user' ? 'user-message' : 'assistant-message']"
      >
        <div v-if="message.role === 'assistant'" class="message-wrapper assistant-message">
          <img class="icon-assistant" src="/OfekUnit.png" alt="logo"/>
          <div class="message-content formatted-response">
            <pre>{{ message.content }}</pre>
            <div class="timestamp">{{ formatTimestamp(message.timestamp) }}</div>
          </div>
        </div>
        <div v-else class="message-wrapper user-message">
          <div class="message-content">
            <pre>{{ message.content }}</pre>
            <div class="timestamp">{{ formatTimestamp(message.timestamp) }}</div>
          </div>
        </div>
      </div>
    </div>
    <div class="input-area">
      <div class="input-wrapper">
        <textarea
            v-model="questionInput"
            id="questionInput"
            placeholder="Type your message..."
            rows="1"
            @keydown="handleKeydown"
        ></textarea>
        <button
            id="sendButton"
            :disabled="isLoading || !questionInput.trim()"
            @click="askQuestion"
        >
          <img src="@/assets/sendIcon.svg" alt="Send" class="send-icon"/>
        </button>
      </div>
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
      await this.submitQuestions(this.suburl);
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

      const question = this.isLoading
          ? this.messages[this.messages.length - 1].content
          : this.questionInput.trim();
      if (!this.isLoading) {
        this.addMessage(question, 'user');
        this.questionInput = '';
      }
      await this.submitQuestions(question);
    },
    async submitQuestions(question) {
      this.isLoading = true;

      try {
        const response = await fetch(process.env.VUE_APP_MODEL_URL, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
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
          const {done, value} = await reader.read();
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
    handleKeydown(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.askQuestion();
      }
    },
    formatTimestamp(timestamp) {
      return new Date(timestamp).toLocaleTimeString();
    },
  },
};
</script>

<style src="./Chat.css" scoped></style>
