<template>
  <section
    class="flex flex-col h-[calc(100vh-10rem)] w-full overflow-hidden
           rounded-[32px] border border-[#498528] bg-white/80
           shadow-[0_32px_80px_rgba(15,23,42,0.18)] backdrop-blur-xl"
  >
    <!-- HEADER -->
    <div
      class="flex items-center justify-between px-6 py-4 shrink-0 z-10
             border-b border-[#498528]/30 
             bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70
             shadow-sm"
    >
      <div class="flex items-center gap-4">
        <div class="relative">
          <div
            class="flex h-12 w-12 items-center justify-center rounded-2xl
                   bg-emerald-600 text-2xl shadow-md text-white
                   ring-2 ring-emerald-300/70"
          >
            <span class="text-lg font-semibold">A</span>
          </div>
          <span
            class="absolute -bottom-1 -right-1 h-3.5 w-3.5 rounded-full
                   bg-emerald-500 ring-2 ring-white"
          ></span>
        </div>
        <div>
          <h2 class="text-lg font-bold text-slate-900 tracking-tight">
            {{ chatbotHeadline || 'HR Assistant' }}
          </h2>
          <p
            class="text-[11px] text-slate-500 font-medium uppercase tracking-[0.35em]
                   flex items-center gap-1"
          >
            {{ chatbotSubtitle || 'Always Online' }}
          </p>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="$emit('reset-chatbot')"
          class="px-4 py-2 text-xs font-bold text-slate-600 uppercase tracking-wider
                 border border-[#498528]/30 rounded-full bg-white/80
                 hover:bg-[#DDEED1]/60 hover:text-[#2F4C1C]
                 shadow-sm transition-all"
        >
          Clear History
        </button>
      </div>
    </div>

    <!-- CHAT SCROLL AREA -->
    <div
      class="flex-1 overflow-y-auto scroll-smooth
             bg-gradient-to-b from-slate-50 via-emerald-50/30 to-slate-50"
      ref="chatContainer"
    >
      <div
        class="max-w-4xl mx-auto w-full px-4 py-8 space-y-8 min-h-full
               flex flex-col justify-end"
      >
        <!-- EMPTY STATE -->
        <div
          v-if="!chatHistory.length"
          class="flex-1 flex flex-col items-center justify-center text-center
                 opacity-80 py-20"
        >
          <div
            class="mb-6 rounded-3xl bg-white/90 p-6 shadow-sm
                   border border-[#498528]/25"
          >
            <svg
              class="h-12 w-12 text-emerald-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.5"
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-slate-900">
            Welcome to HR Support
          </h3>
          <p class="text-sm text-slate-500 mt-2 max-w-xs">
            I can help you with leave balance, policy questions, payroll details, and more.
          </p>

          <div
            v-if="chatbotReply"
            class="mt-8 bg-white/90 px-6 py-4 rounded-2xl shadow-sm
                   border border-[#498528]/25 text-left max-w-lg"
          >
            <p class="text-sm text-slate-700 whitespace-pre-line">
              {{ chatbotReply }}
            </p>
          </div>
        </div>

        <!-- HISTORY -->
        <template v-else>
          <div class="text-center">
            <span
              class="px-3 py-1 bg-slate-200/80 text-slate-500 text-[10px]
                     font-bold uppercase rounded-full tracking-[0.25em]"
            >
              Today
            </span>
          </div>

          <div
            v-for="(entry, index) in chatHistory"
            :key="'chat-' + index"
            class="flex w-full gap-4"
            :class="entry.sender === 'user' ? 'flex-row-reverse' : 'flex-row'"
          >
            <div
              class="h-10 w-10 rounded-full flex items-center justify-center shrink-0
                     text-lg border"
              :class="entry.sender === 'user'
                ? 'bg-white border-slate-200 text-slate-600'
                : 'bg-emerald-600 border-emerald-600 text-white'"
            >
              {{ entry.sender === 'user' ? '👤' : '🤖' }}
            </div>

            <div class="flex flex-col gap-1 max-w-[80%] md:max-w-[70%]">
              <div
                class="px-6 py-4 text-base shadow-sm whitespace-pre-line leading-relaxed"
                :class="entry.sender === 'user'
                  ? 'bg-emerald-600 text-white rounded-2xl rounded-tr-sm'
                  : 'bg-white/95 border border-[#498528]/20 text-slate-700 rounded-2xl rounded-tl-sm'"
              >
                {{ entry.content }}
              </div>
              <span
                class="text-xs text-slate-400 font-medium px-1"
                :class="entry.sender === 'user' ? 'text-right' : 'text-left'"
              >
                {{ formatRelativeDate(entry.timestamp) }}
              </span>
            </div>
          </div>
        </template>

        <!-- TYPING INDICATOR -->
        <div v-if="chatbotLoading" class="flex w-full gap-4">
          <div
            class="h-10 w-10 rounded-full bg-emerald-600 flex items-center justify-center
                   shrink-0 text-white border border-emerald-600"
          >
            🤖
          </div>
          <div
            class="bg-white/95 border border-[#498528]/20 px-6 py-4 rounded-2xl rounded-tl-sm
                   shadow-sm flex items-center gap-1.5"
          >
            <span class="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>
            <span
              class="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-75"
            ></span>
            <span
              class="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-150"
            ></span>
          </div>
        </div>

        <!-- REFERENCE CHIPS -->
        <div v-if="chatbotReferenceVisible" class="flex justify-center pb-2">
          <div class="flex flex-wrap justify-center gap-2">
            <span
              v-if="chatbotTicketId"
              class="px-3 py-1 bg-[#DDEED1]/80 text-[#2F4C1C] text-xs font-bold
                     rounded-full border border-[#498528]/30"
            >
              Ticket #{{ chatbotTicketId }}
            </span>
            <span
              v-if="chatbotReference"
              class="px-3 py-1 bg-white/80 text-slate-500 text-xs rounded-full
                     border border-slate-200"
            >
              Ref: {{ chatbotReference }}
            </span>
            <span
              v-if="chatbotStatusLabel"
              class="px-3 py-1 bg-amber-50 text-amber-700 text-xs font-bold
                     rounded-full border border-amber-100 uppercase"
            >
              {{ chatbotStatusLabel }}
            </span>
          </div>
        </div>

        <!-- ESCALATION BANNER -->
        <div
          v-if="chatbotNeedsEscalation"
          class="max-w-4xl mx-auto w-full px-4 pb-4"
        >
          <div
            class="rounded-2xl border border-amber-200 bg-amber-50/90 px-6 py-6
                   text-sm text-amber-800 space-y-4 shadow-sm"
          >
            <div class="flex items-center gap-3">
              <div
                class="flex h-8 w-8 items-center justify-center rounded-full
                       bg-amber-600 text-white text-xs font-bold"
              >
                HR
              </div>
              <div>
                <p class="font-bold text-amber-900">Forward to HR?</p>
                <p class="text-amber-700 text-xs">
                  I couldn't find this answer in our guide. Would you like me to send it to HR?
                </p>
              </div>
            </div>

            <div
              class="rounded-xl bg-white px-4 py-3 text-xs text-slate-600
                     border border-amber-200"
            >
              "{{ pendingEscalationQuestion }}"
            </div>

            <div class="flex flex-wrap gap-3">
              <button
                @click="$emit('confirm-escalation')"
                :disabled="chatbotEscalating"
                class="rounded-2xl bg-amber-600 px-6 py-2.5 text-xs font-bold
                       uppercase tracking-wider text-white transition
                       hover:bg-amber-500 disabled:cursor-not-allowed
                       disabled:opacity-60 shadow-md hover:shadow-lg"
              >
                {{ chatbotEscalating ? 'Sending...' : 'Send to HR' }}
              </button>
              <button
                @click="$emit('cancel-escalation')"
                :disabled="chatbotEscalating"
                class="rounded-2xl border border-amber-400 px-6 py-2.5 text-xs
                       font-bold uppercase tracking-wider text-amber-700
                       transition hover:bg-white disabled:cursor-not-allowed
                       disabled:opacity-60"
              >
                No thanks
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- INPUT BAR -->
    <div
      class="bg-white/95 border-t border-[#498528]/30 p-4 md:p-6 shrink-0"
    >
      <div class="max-w-4xl mx-auto w-full">
        <form
          class="relative flex items-end gap-3 bg-white/95 rounded-[999px]
                 shadow-[0_18px_40px_rgba(15,23,42,0.16)]
                 border border-[#498528]/40 p-2
                 focus-within:ring-2 focus-within:ring-emerald-500/20
                 focus-within:border-emerald-500 transition-all"
          @submit.prevent="$emit('submit-chatbot-prompt')"
        >
          <textarea
            :value="chatbotPrompt"
            @input="$emit('update:chatbot-prompt', $event.target.value)"
            @keydown.enter.exact.prevent="$emit('submit-chatbot-prompt')"
            rows="1"
            class="w-full max-h-40 min-h-[50px] bg-transparent border-0
                   px-4 py-3.5 text-base text-slate-700
                   placeholder-slate-400 focus:ring-0 resize-none custom-scrollbar"
            placeholder="Type your message here..."
            style="field-sizing: content;"
          ></textarea>

          <button
            type="submit"
            :disabled="chatbotLoading || !chatbotPrompt"
            class="h-12 w-12 flex items-center justify-center rounded-2xl
                   bg-emerald-600 text-white shadow-md hover:bg-emerald-700
                   disabled:opacity-50 disabled:cursor-not-allowed
                   transition-all hover:scale-105 active:scale-95
                   shrink-0 mb-0.5 mr-0.5"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5 ml-0.5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"
              />
            </svg>
          </button>
        </form>

        <p class="mt-3 text-center text-xs text-slate-400">
          AI responses are for guidance only. Consult official HR documentation for binding policies.
        </p>
      </div>
    </div>
  </section>
</template>


<script>
export default {
  name: 'ManagerChatbot',
  props: {
    chatbotHeadline: String,
    chatbotSubtitle: String,
    chatHistory: {
      type: Array,
      default: () => []
    },
    chatbotStatusLabel: String,
    chatbotReference: String,
    chatbotReferenceSource: String,
    chatbotReferenceVisible: Boolean,
    chatbotTicketId: [String, Number],
    chatbotReply: String,
    chatbotPrompt: String,
    chatbotLoading: Boolean,
    chatbotNeedsEscalation: Boolean,
    pendingEscalationQuestion: String,
    chatbotEscalating: Boolean,
  },
  emits: ['reset-chatbot', 'submit-chatbot-prompt', 'update:chatbot-prompt', 'confirm-escalation', 'cancel-escalation'],
  watch: {
    chatHistory: {
      handler() {
        this.$nextTick(() => {
          if (this.$refs.chatContainer) {
            this.$refs.chatContainer.scrollTop = this.$refs.chatContainer.scrollHeight;
          }
        });
      },
      deep: true
    }
  },
  methods: {
    formatRelativeDate(value) {
      if (!value) return '';
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return '';
      const now = new Date();
      const sameDay = date.toDateString() === now.toDateString();
      const timePart = date.toLocaleTimeString(undefined, {
        hour: '2-digit',
        minute: '2-digit',
      });
      if (sameDay) {
        return timePart;
      }
      const datePart = date.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
      });
      return `${datePart} ${timePart}`;
    },
  }
};
</script>

<style scoped>
/* Sleek Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
  border: 2px solid transparent;
  background-clip: content-box;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}
</style>
