<template>
  <section class="questions-shell space-y-6 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
      <article class="questions-hero relative overflow-hidden rounded-[32px] border border-[#498528] bg-white shadow-[0_32px_80px_rgba(15,23,42,0.18)]">
        <div class="questions-hero-inner grid gap-8 lg:grid-cols-2 lg:items-center p-8 lg:p-10">
          <div class="space-y-6">
            <div class="flex items-center gap-2">
              <span class="relative flex h-2.5 w-2.5">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-500"></span>
              </span>
              <span class="text-xs font-bold uppercase tracking-widest text-rose-600">Priority Support</span>
            </div>
            <h2 class="text-3xl font-bold tracking-tight text-slate-900">Escalated Questions</h2>
            <p class="text-slate-500 mt-1 text-sm leading-relaxed max-w-2xl">
              Address complex inquiries and support tickets escalated to Human Resources.
            </p>
          </div>
          <div class="flex items-center justify-end">
            <div class="inline-flex items-center gap-3 px-5 py-3 rounded-full bg-white border border-slate-200 shadow">
              <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Open Tickets</span>
              <span class="text-xl font-black text-slate-900 leading-none">{{ ctx.questions.length }}</span>
            </div>
          </div>
        </div>
      </article>

      <div class="questions-content space-y-6">
        <div v-if="ctx.questionsLoading" class="card-shell shaded-panel dashed-border text-center">
          <div class="animate-spin h-8 w-8 border-4 border-slate-100 border-t-indigo-600 rounded-full mb-4 mx-auto"></div>
          <p class="text-xs font-bold uppercase tracking-widest text-slate-400">Loading inquiries…</p>
        </div>

        <div v-else-if="!ctx.questions.length" class="card-shell shaded-panel text-center space-y-3">
          <div class="mx-auto h-24 w-24 bg-slate-50 rounded-full flex items-center justify-center mb-2 ring-8 ring-slate-50/50">
            <svg class="h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-slate-900">Support clear</h3>
          <p class="text-sm text-slate-500 max-w-sm mx-auto mt-2">All escalated questions have been resolved.</p>
        </div>

        <div v-else class="space-y-4">
          <article 
            v-for="question in ctx.questions" 
            :key="question.id" 
            class="card-shell question-card overflow-hidden"
          >
            <div class="px-6 py-3 border-b border-slate-100 bg-white/70 flex items-center justify-between text-[10px] font-semibold uppercase tracking-wider text-slate-400">
              <span>{{ formatStatus(question.status) }}</span>
              <span>{{ formatDate(question.created_at || question.updated_at) }}</span>
            </div>
            <div class="flex flex-col lg:flex-row">
              <div class="p-6 lg:w-[280px] shrink-0 bg-slate-50/50 border-b lg:border-b-0 lg:border-r border-slate-100 flex flex-col justify-center">
                <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-3">Raised By</span>
                <div class="flex items-center gap-4">
                  <div 
                    class="h-12 w-12 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-sm shrink-0 ring-2 ring-white"
                    :style="{ backgroundColor: getAvatarColor(question.asked_by) }"
                  >
                    {{ getInitials(question.asked_by) }}
                  </div>
                  <div class="min-w-0">
                    <h3 class="font-bold text-slate-900 text-sm md:text-base leading-tight truncate">{{ question.asked_by || 'Unknown' }}</h3>
                    
                  </div>
                </div>
              </div>

              <div class="flex-1 p-6 flex flex-col justify-center gap-5">
                <div>
                  <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    Subject
                  </span>
                  <h4 class="text-base font-bold text-slate-900">
                    {{ question.subject || 'General Inquiry' }}
                  </h4>
                </div>

                <div>
                  <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Inquiry Details
                  </span>
                  <div class="relative group/text">
                    <div class="absolute left-0 top-0 bottom-0 w-1 bg-indigo-500 rounded-l-lg"></div>
                    <p class="text-sm text-slate-600 leading-relaxed bg-slate-50 p-4 pl-5 rounded-r-lg border-y border-r border-slate-100 group-hover/text:bg-slate-50/80 transition-colors">
                      {{ question.body || question.question || 'No description provided.' }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="p-6 lg:w-[220px] shrink-0 bg-gradient-to-br from-white to-slate-50 border-t lg:border-t-0 lg:border-l border-slate-100 flex flex-col justify-center gap-3">
                <span class="hidden lg:block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1 text-center">
                  Action Required
                </span>

                <div class="flex items-center justify-center mb-2 lg:mb-0">
                  <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-50 border border-rose-100 text-[10px] font-bold text-rose-600 uppercase tracking-wide">
                    <span class="h-1.5 w-1.5 rounded-full bg-rose-500 animate-pulse"></span>
                    Escalated
                  </span>
                </div>

                <button
                  class="w-full shadow-md hover:shadow-lg bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 flex items-center justify-center gap-2 transition"
                  type="button"
                  @click="ctx.openAnswerModal(question)"
                >
                  <span>Respond</span>
                  <svg
                    class="w-4 h-4 text-white transition-colors"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'HrDashboardQuestionsTab',
  inject: ['hrDashboardContext'],
  computed: {
    ctx() {
      return this.hrDashboardContext
    },
  },
  methods: {
    formatStatus(status) {
      if (!status) return 'Unknown';
      return status.replace(/_/g, ' ');
    },
    formatDate(value) {
      if (!value) return 'Just now';
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return 'Recently';
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    },
    getInitials(name) {
      if (!name) return '??';
      return name
        .split(' ')
        .map(n => n[0])
        .slice(0, 2)
        .join('')
        .toUpperCase();
    },
    getAvatarColor(name) {
      const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f59e0b', '#10b981'];
      if (!name) return colors[0];
      let hash = 0;
      for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
      }
      return colors[Math.abs(hash) % colors.length];
    }
  }
}
</script>

<style scoped>
.questions-hero {
  background: linear-gradient(135deg, #f9fafb, #dbeafe 70%);
  border-radius: 2rem;
  border: 1px solid #498528;
  box-shadow: 0 32px 80px rgba(15, 23, 42, 0.18);
}
.questions-primary-btn {
  background: #0f172a;
  box-shadow: 0 15px 30px rgba(15, 23, 42, 0.35);
}
.questions-primary-btn:hover:not(:disabled) {
  background: #0a0f16;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.45);
}
.question-card {
  background: #ffffff;
  border-radius: 1.5rem;
  border: 1px solid rgba(73, 133, 40, 0.25);
  padding: 0;
}
.dashed-border {
  background-image: url("data:image/svg+xml,%3csvg width='100%25' height='100%25' xmlns='http://www.w3.org/2000/svg'%3e%3crect width='100%25' height='100%25' fill='none' rx='16' ry='16' stroke='%2394a3b8' stroke-width='2' stroke-dasharray='6%2c 10' stroke-dashoffset='0' stroke-linecap='square' opacity='0.3'/%3e%3c/svg%3e");
  border: none;
}
.questions-shell {
  background: #f5faf5;
}
.questions-hero-inner {
  background: linear-gradient(135deg, rgba(237, 250, 255, 0.9), rgba(221, 238, 209, 0.7));
  border-radius: 1.75rem;
}
.questions-content {
  background: #ffffff;
  border-radius: 1.75rem;
  padding: 1.5rem;
  border: 1px solid rgba(73, 133, 40, 0.25);
  box-shadow: 0 25px 45px rgba(15, 23, 42, 0.08);
}
.shaded-panel {
  background: #f7fff7;
  border: 1px solid rgba(73, 133, 40, 0.2);
  box-shadow: inset 0 0 0 1px rgba(73, 133, 40, 0.08);
}
</style>
