<template>
  <section class="space-y-10">
    <!-- HERO / TEAM OPERATIONS HUB -->
    <section
      class="relative overflow-hidden rounded-[32px] border border-[#498528] 
             bg-gradient-to-br from-slate-100 via-white to-emerald-50 
             shadow-[0_32px_80px_rgba(15,23,42,0.18)] backdrop-blur-xl"
    >
      <div
        class="flex flex-col gap-8 p-8 
               lg:grid lg:grid-cols-[1fr_1fr] lg:items-start lg:gap-12"
      >
        <!-- LEFT: TITLE + IMAGE -->
        <div class="space-y-6">
          <div class="space-y-3">
            <p
              class="text-sm font-semibold uppercase tracking-[0.45em] 
                     text-slate-500"
            >
              Team operations hub
            </p>
            <h2
              class="text-3xl font-semibold leading-tight text-slate-900"
            >
              {{ displayName }}
            </h2>
            <p class="text-sm text-slate-600">
              {{ headlineText }}
            </p>
          </div>

          <div
            class="relative overflow-hidden rounded-[28px] border border-[#498528]/30 
                   bg-white/80 shadow-[0_28px_70px_rgba(15,23,42,0.18)]"
          >
            <img
              src="@/assets/Manager.svg"
              alt="Dashboard illustration"
              class="block w-full object-cover"
            >
          </div>
        </div>

        <!-- RIGHT: CHIPS + CTAS + TEAM SIGNAL -->
        <div class="space-y-6">
          <!-- Highlight chips -->
          <ul
            v-if="managerWorkspaceHighlights.length"
            class="flex flex-wrap gap-3 text-xs"
          >
            <li
              v-for="chip in managerWorkspaceHighlights.slice(0, 2)"
              :key="`manager-chip-${chip.id}`"
              class="inline-flex items-center gap-2 rounded-full 
                     border border-[#498528]/30 bg-[#DDEED1]/70 
                     px-3 py-1 text-[#2F4C1C] shadow-sm"
            >
              <span class="text-sm text-[#2F4C1C]/80">
                {{ chip.label }}
              </span>
              <span class="font-semibold text-[#2F4C1C]">
                {{ chip.title }}
              </span>
            </li>
          </ul>

          <!-- CTA buttons -->
          <div class="flex flex-wrap gap-3">
            <button
              class="rounded-full px-6 py-2 text-sm font-semibold text-white
                    bg-[#F04770] hover:bg-[#C93A5B]
                    shadow-md hover:shadow-lg transition-all duration-300"
              type="button"
              @click="$emit('set-active-tab', 'approvals')"
            >
              Review approvals
            </button>
            <button
              class="rounded-full border border-emerald-200 bg-emerald-600 
                     px-5 py-2 text-sm font-semibold text-white shadow-md 
                     transition hover:bg-emerald-700 hover:shadow-lg"
              type="button"
              @click.stop="$emit('go-to-chatbot')"
            >
              Open chatbot
            </button>
          </div>

          <!-- TEAM SIGNAL CARD -->
          <div
            class="relative overflow-hidden rounded-[28px] border border-[#498528] 
                   bg-white/80 p-6 shadow-[0_24px_60px_rgba(15,23,42,0.1)] 
                   backdrop-blur-xl"
          >
            <!-- glowing shapes -->
            <div
              class="absolute -right-8 -top-8 h-32 w-32 rounded-full 
                     bg-emerald-200/40 blur-3xl"
            ></div>
            <div
              class="absolute -left-10 bottom-0 h-28 w-28 rounded-full 
                     bg-sky-200/40 blur-3xl"
            ></div>

            <div class="relative space-y-4">
              <div
                class="flex items-center justify-between text-[11px] font-semibold 
                       uppercase tracking-[0.45em] text-slate-400"
              >
                <span>Team signal</span>
                <span>{{ todayLabel }}</span>
              </div>

              <div class="space-y-3">
                <div
                  v-for="stat in managerHeroStats"
                  :key="stat.id"
                  class="flex items-center justify-between rounded-2xl 
                         border border-slate-100/80 bg-white/95 px-4 py-3 
                         text-slate-700 shadow-sm"
                >
                  <div>
                    <p
                      class="text-[11px] font-semibold uppercase tracking-[0.35em] 
                             text-slate-400"
                    >
                      {{ stat.label }}
                    </p>
                    <p class="text-2xl font-semibold text-slate-900">
                      {{ stat.value }}
                    </p>
                  </div>
                  <div class="text-right text-xs text-slate-500">
                    <p>{{ stat.context }}</p>
                    <p
                      v-if="stat.note"
                      :class="[
                        'mt-1 font-semibold',
                        stat.intent === 'success'
                          ? 'text-emerald-600'
                          : stat.intent === 'warning'
                          ? 'text-amber-500'
                          : 'text-slate-500'
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

    <!-- STAT CARDS GRID -->
    <section
      class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3"
    >
      <div
        v-for="stat in managerStatCards"
        :key="stat.title"
        class="flex items-center justify-between rounded-2xl 
               border border-[#498528]/30 bg-[#DDEED1]/80 p-6 
               shadow-[0_16px_30px_rgba(15,23,42,0.08)]"
      >
        <div>
          <p class="text-sm font-medium text-[#2F4C1C]/80">
            {{ stat.title }}
          </p>
          <p class="text-3xl font-semibold text-[#2F4C1C]">
            {{ stat.value }}
          </p>
          <p class="text-xs text-[#2F4C1C]/80">
            {{ stat.subtext }}
          </p>
        </div>
        <div
          class="flex h-12 w-12 items-center justify-center rounded-full 
                 bg-white/80 text-lg text-[#2F4C1C] shadow-sm"
        >
          {{ stat.icon }}
        </div>
      </div>
    </section>
  </section>
</template>


<script>
export default {
  name: 'ManagerOverview',
  props: {
    displayName: String,
    headlineText: String,
    managerWorkspaceHighlights: Array,
    managerHeroStats: Array,
    managerStatCards: Array,
    todayLabel: String,
  },
  emits: ['set-active-tab', 'go-to-chatbot'],
};
</script>
