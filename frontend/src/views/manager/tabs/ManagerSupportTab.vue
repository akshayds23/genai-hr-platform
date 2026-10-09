<template>
  <section class="space-y-6">
    <div
      id="section-manager-support"
      class="rounded-[28px] border border-[#498528] bg-white/80 
             shadow-[0_24px_60px_rgba(15,23,42,0.12)] backdrop-blur-xl"
    >
      <!-- HEADER -->
      <header
        class="flex flex-col gap-3 border-b border-[#498528]/30 px-6 py-5 
               md:flex-row md:items-center md:justify-between
               bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70"
      >
        <div>
          <p
            class="text-[11px] font-semibold uppercase tracking-[0.35em] 
                   text-slate-400"
          >
            Team escalations
          </p>
          <h2 class="text-lg font-semibold text-slate-900">
            HR support tracker
          </h2>
          <p class="text-sm text-slate-500">
            Review every question escalated from your org and see the latest HR answers.
          </p>
        </div>

        <div class="flex flex-wrap gap-2">
          <!-- Refresh button -->
          <button
            class="inline-flex items-center gap-2 rounded-full border border-[#498528]/30 
                   bg-white/80 px-4 py-2 text-xs font-semibold uppercase tracking-wide 
                   text-slate-600 shadow-sm transition hover:bg-[#DDEED1]/60 
                   hover:text-[#2F4C1C]"
            type="button"
            @click="$emit('refresh')"
          >
            <svg
              class="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9M20 20v-5h-.581m-15.357-2a8.003 8.003 0 0015.357 2"
              />
            </svg>
            Refresh
          </button>

          <!-- Ask HR button -->
          <button
            class="inline-flex items-center gap-2 rounded-full border border-emerald-300 
                   bg-emerald-600 px-4 py-2 text-xs font-semibold uppercase 
                   tracking-wide text-white shadow-md transition 
                   hover:bg-emerald-500 hover:shadow-lg"
            type="button"
            @click="$emit('open-chatbot')"
          >
            <svg
              class="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6l4 2" />
            </svg>
            Ask HR
          </button>
        </div>
      </header>

      <!-- BODY -->
      <div class="px-6 pb-6">
        <!-- Loading -->
        <div
          v-if="loading"
          class="rounded-2xl border border-[#498528]/25 bg-slate-50 px-4 py-10 
                 text-center text-sm text-slate-500"
        >
          Syncing escalations...
        </div>

        <!-- Error -->
        <div
          v-else-if="error"
          class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-4 
                 text-sm text-rose-600"
        >
          {{ error }}
        </div>

        <!-- Content -->
        <template v-else>
          <div v-if="hasQuestions" class="space-y-6">
            <!-- Summary chips -->
            <div
              class="grid gap-3 rounded-2xl border border-[#498528]/30 
                     bg-[#DDEED1]/70 px-4 py-4 text-center sm:grid-cols-3"
            >
              <div class="space-y-1">
                <p
                  class="text-[10px] font-bold uppercase tracking-wider 
                         text-[#2F4C1C]/80"
                >
                  Total escalations
                </p>
                <p
                  class="text-2xl font-semibold text-[#2F4C1C] tabular-nums"
                >
                  {{ questions.length }}
                </p>
              </div>
              <div class="space-y-1">
                <p
                  class="text-[10px] font-bold uppercase tracking-wider 
                         text-[#2F4C1C]/80"
                >
                  Awaiting HR response
                </p>
                <p
                  class="text-2xl font-semibold text-amber-600 tabular-nums"
                >
                  {{ pendingCount }}
                </p>
              </div>
              <div class="space-y-1">
                <p
                  class="text-[10px] font-bold uppercase tracking-wider 
                         text-[#2F4C1C]/80"
                >
                  Answered this week
                </p>
                <p
                  class="text-2xl font-semibold text-emerald-600 tabular-nums"
                >
                  {{ answeredThisWeek }}
                </p>
              </div>
            </div>

            <!-- Question list -->
            <div class="space-y-4">
              <article
                v-for="question in questions"
                :key="question.id || question.reference || question.createdAt"
                class="rounded-3xl border border-[#498528]/25 bg-white/95 
                       px-5 py-4 shadow-sm"
              >
                <div
                  class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"
                >
                  <div>
                    <p
                      class="text-[11px] font-semibold uppercase tracking-wider 
                             text-slate-400"
                    >
                      Submitted {{ question.submittedAtReadable || '—' }}
                    </p>
                    <h3
                      class="mt-1 text-sm font-semibold text-slate-900 
                             leading-snug"
                    >
                      {{
                        truncate(
                          question.question || question.details || 'Escalated question',
                          160
                        )
                      }}
                    </h3>
                  </div>

                  <span
                    :class="[
                      'inline-flex items-center justify-center rounded-full px-3 py-1 text-[11px] font-bold uppercase tracking-wide border',
                      statusChipClass(question.statusClass),
                    ]"
                  >
                    {{ question.statusText || formatStatus(question.status) }}
                  </span>
                </div>

                <!-- HR response -->
                <div
                  v-if="question.hasAnswer"
                  class="mt-4 rounded-2xl border border-emerald-100 
                         bg-emerald-50/70 px-4 py-3"
                >
                  <div
                    class="flex flex-wrap items-center gap-2 text-[10px] 
                           font-bold uppercase tracking-wider text-emerald-500"
                  >
                    <!-- <span>HR response</span> -->
                    <span
                      v-if="question.responderName"
                      class="text-[11px] font-semibold uppercase tracking-wide 
                             text-emerald-400"
                    >
                      • {{ question.responderName }}
                    </span>
                  </div>
                  <p
                    class="mt-2 text-sm text-emerald-900 whitespace-pre-line 
                           leading-relaxed"
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
            class="rounded-2xl border border-[#498528]/25 bg-slate-50 
                   px-4 py-10 text-center text-sm text-slate-500"
          >
            No questions have been escalated by your team yet.
          </p>
        </template>
      </div>
    </div>
  </section>
</template>


<script>
export default {
  name: 'ManagerSupportTab',
  props: {
    questions: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
    error: {
      type: String,
      default: '',
    },
  },
  emits: ['refresh', 'open-chatbot'],
  computed: {
    hasQuestions() {
      return Array.isArray(this.questions) && this.questions.length > 0;
    },
    pendingCount() {
      return this.questions.filter(
        (item) => ((item.status || '').toLowerCase() !== 'resolved' && item.statusClass !== 'success')
      ).length;
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
    truncate(value, max = 160) {
      if (!value || typeof value !== 'string') {
        return value;
      }
      return value.length > max ? `${value.slice(0, max)}...` : value;
    },
    formatStatus(status) {
      if (!status) {
        return 'Unknown';
      }
      const text = status.toString().toLowerCase();
      return text.charAt(0).toUpperCase() + text.slice(1);
    },
  },
};
</script>
