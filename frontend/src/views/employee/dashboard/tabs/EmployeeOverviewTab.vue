<template>
  <section class="space-y-10">

    <!-- TOP HERO CARD -->
    <section
      class="relative overflow-hidden rounded-[32px] border border-slate-200 
             bg-gradient-to-br from-slate-100 via-white to-indigo-50 
             shadow-[0_32px_80px_rgba(15,23,42,0.18)] backdrop-blur-xl"
    >
      <div class="flex flex-col gap-10 p-10 lg:grid lg:grid-cols-2 lg:items-center lg:gap-16 
            border border-[#498528] rounded-[28px]">


        <!-- LEFT PROFILE + ILLUSTRATION -->
        <div class="space-y-7 animate-fade-in">
          <div class="space-y-3">
            <p class="text-xs font-semibold uppercase tracking-[0.45em] text-slate-500">
              Personal workspace
            </p>

            <h2 class="text-4xl font-semibold leading-tight text-slate-900 drop-sm">
              {{ displayName }}
            </h2>

            <p class="text-sm text-slate-600">
              {{ overviewSubtitle }}
            </p>
          </div>

          <div
            class="relative overflow-hidden rounded-[28px] border border-slate-100 
                   bg-white/80 shadow-[0_25px_60px_rgba(15,23,42,0.12)] transition hover:scale-[1.015]"
          >
            <img 
              src="@/assets/employee.png" 
              alt="Dashboard illustration" 
              class="block w-full object-cover" 
            />
          </div>
        </div>

        <!-- RIGHT CTA + DAILY SIGNAL -->
        <div class="flex flex-col justify-center space-y-8 h-full animate-slide-up">

          <!-- CTA BUTTONS -->
          <div class="flex flex-wrap gap-3 mt-2">

            <!-- Leave Button -->
            <button
  class="rounded-full px-6 py-2 text-sm font-semibold text-white 
         bg-[#F04770] hover:bg-[#C93A5B] shadow-md hover:shadow-lg 
         transition-all duration-300"
  type="button"
  @click="ctx.goToLeaveSection"
>
              Go to leave center
            </button>

            <!-- Chatbot Button -->
            <button
              class="rounded-full px-6 py-2 text-sm font-semibold text-white 
                     bg-emerald-600 hover:bg-emerald-700 shadow-md hover:shadow-lg 
                     transition-all duration-300"
              type="button"
              @click.stop="ctx.goToChatbot"
            >
              Open chatbot
            </button>

          </div>

          <!-- DAILY SIGNAL CARD -->
          <div
  class="relative overflow-hidden rounded-[28px] border border-[#498528] 
         bg-white/80 p-8 shadow-[0_24px_60px_rgba(15,23,42,0.1)] backdrop-blur-xl"
>
            <!-- glowing shapes -->
            <div class="absolute -right-8 -top-8 h-36 w-36 rounded-full bg-indigo-200/40 blur-3xl"></div>
            <div class="absolute -left-10 bottom-0 h-32 w-32 rounded-full bg-sky-200/40 blur-3xl"></div>

            <div class="relative space-y-5">
              <div class="flex items-center justify-between text-[11px] font-semibold uppercase tracking-[0.45em] text-slate-400">
                <span>Daily signal</span>
              </div>

              <!-- DAILY STATS -->
              <div class="space-y-4">

                <div
  v-for="stat in heroStats"
  :key="stat.id"
  class="flex flex-col items-center justify-center rounded-2xl p-6 text-center
         shadow-md transition-all hover:shadow-lg hover:-translate-y-1
         bg-[#DDEED1] text-[#2F4C1C]"
>
  <div>
    <p class="text-[11px] font-semibold uppercase tracking-[0.35em] opacity-70">
      {{ stat.label }}
    </p>
    <p class="text-2xl font-semibold">{{ stat.value }}</p>
  </div>

  <div class="text-xs mt-2 opacity-80">
    <p>{{ stat.context }}</p>

    <p
      v-if="stat.note"
      :class="[
        'mt-1 font-semibold',
        stat.intent === 'success'
          ? 'text-[#2F4C1C]'
          : stat.intent === 'warning'
          ? 'text-[#2F4C1C]'
          : 'text-[#2F4C1C]'
      ]"
    >
      {{ stat.note }}
    </p>
  </div>
</div>

              </div>
            </div>

          </div>

        </div>

      </div>
    </section>

    <!-- INSIGHT CARDS GRID -->
    <section class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">

  <div
  v-for="card in statCards"
  :key="card.id"
  class="flex flex-col items-center justify-center rounded-2xl p-6 text-center 
         shadow-md transition-all hover:shadow-lg hover:-translate-y-1
         bg-[#DDEED1] text-[#2F4C1C]"
>
  <p class="text-sm font-medium">{{ card.label }}</p>
  <p class="text-4xl font-semibold mt-1">{{ card.value }}</p>
  <p class="text-xs mt-2 opacity-80">{{ card.subtext }}</p>
</div>

    </section>

  </section>
</template>


<script>
export default {
  name: 'EmployeeOverviewTab',
  inject: ['employeeDashboardContext'],
  computed: {
    ctx() {
      return this.employeeDashboardContext;
    },
    displayName() {
      return this.ctx.displayName || 'Your workspace';
    },
    overviewSubtitle() {
      return this.ctx.overviewSubtitle;
    },
    workspaceHighlights() {
      return this.ctx.workspaceHighlights || [];
    },
    todayLabel() {
      return this.ctx.todayDateString || '';
    },
    heroStats() {
      return [
        {
          id: 'leave-balance',
          label: 'Leave balance',
          value: typeof this.ctx.leaveRemainingDays === 'number' ? `${this.ctx.leaveRemainingDays} days` : '--',
          // context: 'Remaining this year',
          // note: this.ctx.leaveSummary ? `${this.ctx.leaveSummary.pending || 0} pending requests` : '',
          intent: 'info',
        },
        {
          id: 'projects',
          label: 'Active projects',
          value: this.ctx.projectAnnouncement?.title || 'Awaiting latest update',
          // context: 'Assigned to you',
          // note: this.ctx.projectAnnouncement?.title || 'Awaiting latest update',
          intent: 'info',
        },
        // {
        //   id: 'events',
        //   label: 'Next event',
        //   value: this.ctx.upcomingEvents && this.ctx.upcomingEvents.length ? this.ctx.upcomingEvents[0].title : 'None',
        //   context: this.ctx.upcomingEvents && this.ctx.upcomingEvents.length ? this.ctx.upcomingEvents[0].timeRange : '',
        //   note: '',
        //   intent: 'info',
        // },
      ];
    },
    statCards() {
      return (this.ctx.insightCards || []).map((card) => ({
        id: card.id,
        label: card.label,
        value: card.value ?? '--',
        subtext: card.description || card.trend || '',
        icon: card.icon ,
      }));
    },
  },
};
</script>
