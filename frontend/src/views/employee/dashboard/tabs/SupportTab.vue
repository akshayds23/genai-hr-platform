<template>
  <section class="space-y-10">
    <div
      id="section-support"
      class="rounded-[28px] border border-[#498528] bg-white/80 shadow-[0_24px_60px_rgba(15,23,42,0.12)] backdrop-blur-xl"
    >
      <header
        class="flex flex-col gap-3 border-b border-[#498528]/30 px-6 py-5 
               bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70
               md:flex-row md:items-center md:justify-between"
      >
        <div>
          <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
            Escalations
          </p>
          <h2 class="text-lg font-semibold text-slate-900">HR support updates</h2>
          <p class="text-sm text-slate-500">
            See the responses HR has shared for your questions.
          </p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            type="button"
            @click="refreshQuestions"
            class="inline-flex items-center gap-2 rounded-full border border-[#498528]/30 
                   bg-white/80 px-4 py-2 text-xs font-semibold uppercase tracking-wide 
                   text-slate-600 shadow-sm transition-all hover:bg-[#DDEED1]/40 hover:text-[#2F4C1C]"
          >
            <svg class="h-4 w-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9M20 20v-5h-.581m-15.357-2a8.003 8.003 0 0015.357 2"
              />
            </svg>
            Refresh
          </button>
          <button
            type="button"
            @click="ctx.openChatbot"
            class="inline-flex items-center gap-2 rounded-full 
                   bg-emerald-600 px-4 py-2 text-xs font-semibold uppercase tracking-wide 
                   text-white shadow-md transition-all duration-300 
                   hover:bg-emerald-700 hover:shadow-lg active:scale-95
                   focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
          >
            <svg class="h-4 w-4 text-emerald-50" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6l4 2" />
            </svg>
            Ask HR
          </button>
        </div>
      </header>

      <div class="px-6 pb-6 pt-4">
        <!-- Loading state -->
        <div
          v-if="ctx.hrQuestionsLoading"
          class="rounded-2xl border border-[#498528]/25 bg-[#DDEED1]/60 px-4 py-10 text-center text-sm text-[#2F4C1C]"
        >
          Checking for updates...
        </div>

        <!-- Error state -->
        <div
          v-else-if="ctx.hrQuestionsError"
          class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-4 text-sm text-rose-700"
        >
          {{ ctx.hrQuestionsError }}
        </div>

        <!-- Normal state -->
        <template v-else>
          <div v-if="questions.length" class="space-y-6">
            <!-- Summary strip -->
            <div
              class="grid gap-3 rounded-2xl border border-[#498528]/30 bg-[#DDEED1]/70 
                     px-4 py-4 text-center sm:grid-cols-3"
            >
              <div class="space-y-1">
                <p class="text-[10px] font-bold uppercase tracking-[0.25em] text-slate-600">
                  Total escalations
                </p>
                <p class="text-2xl font-semibold text-[#2F4C1C] tabular-nums">
                  {{ questions.length }}
                </p>
              </div>
              <div class="space-y-1">
                <p class="text-[10px] font-bold uppercase tracking-[0.25em] text-slate-600">
                  Awaiting response
                </p>
                <p class="text-2xl font-semibold text-amber-600 tabular-nums">
                  {{ pendingCount }}
                </p>
              </div>
              <div class="space-y-1">
                <p class="text-[10px] font-bold uppercase tracking-[0.25em] text-slate-600">
                  Answered this week
                </p>
                <p class="text-2xl font-semibold text-emerald-600 tabular-nums">
                  {{ answeredThisWeek }}
                </p>
              </div>
            </div>

            <!-- Question cards -->
            <div class="space-y-4">
              <article
                v-for="question in questions"
                :key="question.id"
                class="rounded-[24px] border border-slate-100 bg-white/90 px-5 py-4 shadow-sm 
                       transition-all hover:shadow-md hover:-translate-y-[1px]"
              >
                <div
                  class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"
                >
                  <div>
                    <p
                      class="text-[11px] font-semibold uppercase tracking-[0.25em] text-slate-400"
                    >
                      Submitted {{ question.submittedAtReadable }}
                    </p>
                    <h3 class="mt-1 text-sm font-semibold text-slate-900 leading-snug">
                      {{ ctx.truncateText(question.question, 160) }}
                    </h3>
                  </div>
                  <span
                    :class="[
                      'inline-flex items-center justify-center rounded-full px-3 py-1 text-[11px] font-bold uppercase tracking-wide border',
                      statusChipClass(question.statusClass),
                    ]"
                  >
                    {{ ctx.formatStatus(question.status) }}
                  </span>
                </div>

                <div
                  v-if="question.hasAnswer"
                  class="mt-4 rounded-2xl border border-emerald-100 bg-emerald-50/70 px-4 py-3"
                >
                  <p
                    class="text-[10px] font-bold uppercase tracking-[0.25em] text-emerald-600"
                  >
                    HR response
                  </p>
                  <p
                    class="mt-2 text-sm text-[#2F4C1C] whitespace-pre-line leading-relaxed"
                  >
                    {{ question.answer }}
                  </p>
                </div>
              </article>
            </div>
          </div>

          <!-- Empty state -->
          <p
            v-else
            class="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-10 text-center text-sm text-slate-500"
          >
            No questions have been escalated yet.
          </p>
        </template>
      </div>
    </div>
  </section>
</template>


<script>
export default {
  name: 'SupportTab',
  inject: ['employeeDashboardContext'],
  computed: {
    ctx() {
      return this.employeeDashboardContext;
    },
    questions() {
      return Array.isArray(this.ctx.hrQuestions) ? this.ctx.hrQuestions : [];
    },
    pendingCount() {
      return this.questions.filter((item) => (item.status || '').toLowerCase() !== 'resolved').length;
    },
    answeredThisWeek() {
      const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
      return this.questions.filter((item) => {
        if (!item.hasAnswer) {
          return false;
        }
        const updated = item.updatedAt ? new Date(item.updatedAt).getTime() : null;
        return updated && updated >= weekAgo;
      }).length;
    },
  },
  methods: {
    statusChipClass(statusClass) {
      switch (statusClass) {
        case 'success':
          return 'border-emerald-200 bg-emerald-50 text-emerald-700';
        case 'warning':
          return 'border-amber-200 bg-amber-50 text-amber-700';
        case 'danger':
          return 'border-rose-200 bg-rose-50 text-rose-700';
        default:
          return 'border-slate-200 bg-slate-50 text-slate-600';
      }
    },
    refreshQuestions() {
      if (typeof this.ctx.loadHrQuestions === 'function') {
        this.ctx.loadHrQuestions(true);
      }
    },
  },
};
</script>
