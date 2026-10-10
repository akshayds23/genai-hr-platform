<template>
  <section
    class="flex flex-col h-[calc(100vh-10rem)] w-full overflow-hidden
           rounded-[32px] border border-[#498528] bg-white/80 
           shadow-[0_32px_80px_rgba(15,23,42,0.18)] backdrop-blur-xl"
  >
    <!-- Header -->
    <div
      class="flex items-center justify-between px-6 py-4 border-b border-[#498528]/30 
             bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70 shadow-sm"
    >
      <div class="flex items-center gap-4">
        <div class="relative">
          <div
            class="flex h-12 w-12 items-center justify-center rounded-2xl 
                   bg-emerald-600 text-2xl text-white shadow-md ring-2 ring-emerald-300/60"
          >
            <span class="text-lg font-semibold">A</span>
          </div>
          <span
            class="absolute -bottom-1 -right-1 h-3.5 w-3.5 rounded-full 
                   bg-emerald-500 ring-2 ring-white"
          ></span>
        </div>
        <div>
          <h2
            class="text-lg font-bold text-slate-900 tracking-tight"
          >
            {{ ctx.chatbotHeadline || 'HR Assistant' }}
          </h2>
          <p
            class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-500"
          >
            {{ ctx.chatbotSubtitle || 'Always Online' }}
          </p>
        </div>
      </div>
      <button
        class="rounded-full border border-[#498528]/30 bg-white/80 px-4 py-2 
               text-xs font-semibold uppercase tracking-wide text-slate-600 
               shadow-sm transition-all hover:bg-[#DDEED1]/50 hover:text-[#2F4C1C]"
        type="button"
        @click="ctx.resetChatbot"
      >
        Clear History
      </button>
    </div>

    <!-- Chat Area -->
    <div
      class="flex-1 overflow-y-auto scroll-smooth 
             bg-gradient-to-b from-slate-50 via-emerald-50/30 to-slate-50"
      ref="chatContainer"
    >
      <div
        class="mx-auto flex min-h-full w-full max-w-4xl flex-col justify-end 
               space-y-8 px-4 py-8"
      >
        <!-- Empty state -->
        <div
          v-if="!ctx.chatHistory.length"
          class="flex flex-1 flex-col items-center justify-center py-20 text-center opacity-80"
        >
          <div
            class="mb-6 rounded-3xl border border-[#498528]/25 bg-white/90 p-6 
                   shadow-[0_18px_40px_rgba(15,23,42,0.14)]"
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
          <h3 class="text-xl font-semibold text-slate-900">
            Welcome to HR Support
          </h3>
          <p class="mt-2 max-w-xs text-sm text-slate-500">
            I can help with policies, leave balance, payroll, and more.
          </p>
          <div
            v-if="ctx.chatbotReply"
            class="mt-8 max-w-lg rounded-2xl border border-[#498528]/25 
                   bg-[#DDEED1]/70 px-6 py-4 text-left text-sm text-[#2F4C1C] shadow-sm"
          >
            <p class="whitespace-pre-line">
              {{ ctx.chatbotReply }}
            </p>
          </div>
        </div>

        <!-- Chat history -->
        <template v-else>
          <div class="text-center">
            <span
              class="rounded-full bg-slate-200/80 px-3 py-1 text-[10px] font-bold 
                     uppercase tracking-[0.25em] text-slate-500"
            >
              Today
            </span>
          </div>

          <div
            v-for="(entry, index) in ctx.chatHistory"
            :key="`chat-${index}`"
            class="flex w-full gap-4"
            :class="entry.sender === 'user' ? 'flex-row-reverse' : 'flex-row'"
          >
            <div
              class="flex h-10 w-10 items-center justify-center rounded-full border text-lg"
              :class="entry.sender === 'user'
                ? 'bg-white border-slate-200 text-slate-600'
                : 'bg-emerald-600 border-emerald-600 text-white'"
            >
              {{ entry.sender === 'user' ? '👤' : '💬' }}
            </div>

            <div class="flex max-w-[80%] flex-col gap-1 md:max-w-[70%]">
              <div
                class="whitespace-pre-line px-6 py-4 text-base leading-relaxed shadow-sm"
                :class="entry.sender === 'user'
                  ? 'rounded-2xl rounded-tr-sm bg-emerald-600 text-white'
                  : 'rounded-2xl rounded-tl-sm border border-[#498528]/20 bg-white/95 text-slate-700'"
              >
                {{ entry.content }}
              </div>
              <span
                class="px-1 text-xs font-medium text-slate-400"
                :class="entry.sender === 'user' ? 'text-right' : 'text-left'"
              >
                {{ formatRelativeDate(entry.timestamp) }}
              </span>
            </div>
          </div>
        </template>

        <!-- Typing indicator -->
        <div v-if="ctx.chatbotLoading" class="flex w-full gap-4">
          <div
            class="flex h-10 w-10 items-center justify-center rounded-full 
                   border border-emerald-600 bg-emerald-600 text-white"
          >
            🤖
          </div>
          <div
            class="flex items-center gap-1 rounded-2xl rounded-tl-sm border border-[#498528]/20 
                   bg-white px-6 py-4 shadow-sm"
          >
            <span class="h-2 w-2 animate-bounce rounded-full bg-slate-400"></span>
            <span
              class="h-2 w-2 animate-bounce rounded-full bg-slate-400 delay-75"
            ></span>
            <span
              class="h-2 w-2 animate-bounce rounded-full bg-slate-400 delay-150"
            ></span>
          </div>
        </div>

        <!-- Reference chips -->
        <div v-if="ctx.chatbotReferenceVisible" class="flex justify-center pb-2">
          <div class="flex flex-wrap justify-center gap-2">
            <span
              v-if="ctx.chatbotTicketId"
              class="rounded-full border border-[#498528]/30 bg-[#DDEED1]/70 
                     px-3 py-1 text-xs font-bold text-[#2F4C1C]"
            >
              Ticket #{{ ctx.chatbotTicketId }}
            </span>
            <span
              v-if="ctx.chatbotReference"
              class="rounded-full border border-slate-200 bg-white/80 
                     px-3 py-1 text-xs text-slate-500"
            >
              Ref: {{ ctx.chatbotReference }}
            </span>
            <span
              v-if="ctx.chatbotStatusLabel"
              class="rounded-full border border-amber-200 bg-amber-50 px-3 py-1 
                     text-xs font-bold uppercase text-amber-700"
            >
              {{ ctx.chatbotStatusLabel }}
            </span>
          </div>
        </div>

        <!-- Escalation prompt -->
        <div
          v-if="ctx.chatbotNeedsEscalation"
          class="w-full max-w-4xl rounded-2xl border border-amber-200 bg-amber-50/90 
                 px-6 py-6 text-sm text-amber-800 shadow-sm"
        >
          <div class="flex items-center gap-3">
            <div
              class="flex h-8 w-8 items-center justify-center rounded-full 
                     bg-amber-600 text-xs font-bold text-white"
            >
              HR
            </div>
            <div>
              <p class="font-bold text-amber-900">Forward to HR?</p>
              <p class="text-xs text-amber-700">
                I couldn't find this answer. Want me to send it to HR?
              </p>
            </div>
          </div>
          <div
            class="mt-4 rounded-xl border border-amber-200 bg-white px-4 py-3 
                   text-xs text-slate-600"
          >
            "{{ ctx.pendingEscalationQuestion }}"
          </div>
          <div class="mt-4 flex flex-wrap gap-3">
            <button
              class="rounded-2xl bg-amber-600 px-6 py-2.5 text-xs font-bold uppercase 
                     tracking-wider text-white transition hover:bg-amber-500 
                     disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="ctx.chatbotEscalating"
              @click="ctx.confirmChatbotEscalation"
            >
              {{ ctx.chatbotEscalating ? 'Sending...' : 'Send to HR' }}
            </button>
            <button
              class="rounded-2xl border border-amber-400 px-6 py-2.5 text-xs font-bold uppercase 
                     tracking-wider text-amber-700 transition hover:bg-white 
                     disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              :disabled="ctx.chatbotEscalating"
              @click="ctx.cancelChatbotEscalation"
            >
              No thanks
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div
      class="shrink-0 border-t border-[#498528]/30 bg-white/95 px-4 py-4 md:px-6 md:py-6"
    >
      <div class="mx-auto w-full max-w-4xl">
        <form
          class="relative flex items-end gap-3 rounded-[999px] border border-[#498528]/40 
                 bg-white/95 p-2 shadow-[0_18px_40px_rgba(15,23,42,0.16)] 
                 transition-all focus-within:border-emerald-500 
                 focus-within:ring-2 focus-within:ring-emerald-500/20"
          @submit.prevent="ctx.submitChatbotPrompt"
        >
          <textarea
            v-model="ctx.chatbotPrompt"
            rows="1"
            class="custom-scrollbar h-full min-h-[50px] max-h-40 w-full resize-none 
                   border-0 bg-transparent px-4 py-3.5 text-base text-slate-700 
                   placeholder-slate-400 focus:ring-0"
            placeholder="Ask about leave policy, benefits, or HR processes..."
            @keydown.enter.exact.prevent="ctx.submitChatbotPrompt"
          ></textarea>
          <button
            class="mb-0.5 mr-0.5 flex h-12 w-12 items-center justify-center rounded-2xl 
                   bg-emerald-600 text-white shadow-md transition 
                   hover:scale-105 hover:bg-emerald-700 
                   disabled:cursor-not-allowed disabled:opacity-50"
            type="submit"
            :disabled="ctx.chatbotLoading || !ctx.chatbotPrompt"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
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
          AI answers are guidance only. Confirm important policies with HR.
        </p>
      </div>
    </div>
  </section>
</template>


<script>
export default {
  name: 'ChatbotTab',
  inject: ['employeeDashboardContext'],
  computed: {
    ctx() {
      return this.employeeDashboardContext;
    },
  },
  mounted() {
    this.scrollToBottom();
  },
  watch: {
    'employeeDashboardContext.chatHistory': {
      handler() {
        this.scrollToBottom();
      },
      deep: true,
    },
  },
  methods: {
    scrollToBottom() {
      this.$nextTick(() => {
        const el = this.$refs.chatContainer;
        if (el) {
          el.scrollTop = el.scrollHeight;
        }
      });
    },
    formatRelativeDate(value) {
      if (!value) return '';
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return '';
      const now = new Date();
      const sameDay = date.toDateString() === now.toDateString();
      const timePart = date.toLocaleTimeString('en-IN', {
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'Asia/Kolkata',
      });
      if (sameDay) {
        return timePart;
      }
      const datePart = date.toLocaleDateString('en-IN', {
        month: 'short',
        day: 'numeric',
        timeZone: 'Asia/Kolkata',
      });
      return `${datePart} ${timePart}`;
    },
  },
};
</script>

<style scoped>
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
