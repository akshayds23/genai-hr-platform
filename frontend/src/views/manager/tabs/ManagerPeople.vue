<template>
  <section class="space-y-8">
    <!-- TOP GRID: TEAM ROSTER + BIRTHDAYS -->
    <div class="grid grid-cols-1 gap-8 xl:grid-cols-3 items-start">
      <!-- TEAM ROSTER -->
      <article
        class="xl:col-span-2 rounded-[28px] bg-white/80 border border-[#498528] 
               shadow-[0_24px_60px_rgba(15,23,42,0.12)] overflow-hidden flex flex-col h-full backdrop-blur-xl"
      >
        <header
          class="border-b border-[#498528]/30 px-6 py-4 flex items-center justify-between 
                 bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70"
        >
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
              Team roster
            </p>
            <h2 class="text-base font-bold text-slate-900">Team {{ teamLabel || 'Roster' }}</h2>
            <p class="text-xs font-medium text-slate-500 mt-0.5">
              Active members and roles
            </p>
          </div>
          <span
            class="px-2.5 py-1 rounded-full bg-[#DDEED1]/80 text-xs font-bold text-[#2F4C1C] 
                   border border-[#498528]/40"
          >
            {{ teamMembers.length }} Members
          </span>
        </header>

        <div v-if="teamMembers.length" class="divide-y divide-slate-100/80">
        <div
          v-for="member in teamMembers"
          :key="member.id"
          :class="[
            'group flex items-center justify-between px-6 py-3.5 transition-all',
            isManager(member)
              ? 'bg-[#DDEED1] border-l-4 border-[#498528] hover:bg-[#d2e6c4]'
              : 'hover:bg-[#DDEED1]/40'
          ]"
        >
            <div class="flex items-center gap-4">
              <div
                class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full 
                       bg-[#DDEED1] text-sm font-bold text-[#2F4C1C] 
                       ring-1 ring-inset ring-[#498528]/40"
                :class="isManager(member) ? 'ring-[#498528]/70' : ''"
              >
                {{ getInitials(member.name) }}
              </div>

              <div class="flex flex-col">
                <p class="text-sm font-semibold text-slate-900 flex items-center gap-2">
                  {{ member.name }}
                  <span
                    v-if="member.is_self"
                    class="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 
                           text-[10px] font-medium text-slate-600"
                  >
                    You
                  </span>
                  <span
                    v-else-if="isManager(member)"
                    class="inline-flex items-center rounded-full border border-[#498528]/40 bg-[#DDEED1] px-2 py-0.5 text-[10px] font-semibold text-[#2F4C1C]"
                  >
                    Manager
                  </span>
                </p>
                <p class="text-xs text-slate-500 font-medium">
                  {{ member.job_title || member.employment_role || 'Member' }}
                </p>
              </div>
            </div>

            
          </div>
        </div>
        <div v-else class="p-8 text-center">
          <p class="text-sm text-slate-500">{{ teamEmptyMessage }}</p>
        </div>
      </article>

      <!-- UPCOMING BIRTHDAYS -->
      <article
        class="rounded-[28px] bg-white/80 border border-[#498528] 
               shadow-[0_24px_60px_rgba(15,23,42,0.12)] overflow-hidden flex flex-col h-full backdrop-blur-xl"
      >
        <header
          class="border-b border-[#498528]/30 px-6 py-4 
                 bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70"
        >
          <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
            Celebrations
          </p>
          <h2 class="text-base font-bold text-slate-900">Upcoming Birthdays</h2>
          <p class="text-xs text-slate-500 mt-0.5">
            Next {{ birthdayWindow }} days
          </p>
        </header>

        <!-- Today -->
        <div
          v-if="todayBirthdays.length"
          class="bg-amber-50/60 px-6 py-4 border-b border-amber-100/50"
        >
          <p
            class="text-[10px] font-bold uppercase tracking-wider text-amber-600 
                   mb-3 flex items-center gap-1.5"
          >
            <span class="relative flex h-2 w-2">
              <span
                class="animate-ping absolute inline-flex h-full w-full rounded-full 
                       bg-amber-400 opacity-75"
              ></span>
              <span
                class="relative inline-flex rounded-full h-2 w-2 bg-amber-500"
              ></span>
            </span>
            Today
          </p>
          <ul class="space-y-3">
            <li
              v-for="person in todayBirthdays"
              :key="`today-${person.employee_id}`"
              class="flex items-center justify-between"
            >
              <div class="flex items-center gap-3">
                <div
                  class="h-8 w-8 rounded-full bg-white text-amber-600 flex items-center 
                         justify-center text-xs font-bold ring-1 ring-amber-200 shadow-sm"
                >
                  🎂
                </div>
                <span class="text-sm font-bold text-slate-900">
                  {{ person.employee_name }}
                </span>
              </div>
            </li>
          </ul>
        </div>

        <!-- Upcoming -->
        <div v-if="upcomingBirthdays.length" class="divide-y divide-slate-100/80">
          <div
            v-for="person in upcomingBirthdays"
            :key="person.employee_id"
            class="flex items-center gap-4 px-6 py-3.5"
          >
            <div
              class="flex flex-col items-center justify-center w-10 h-10 rounded-lg 
                     bg-slate-50 border border-slate-200 text-slate-900 shrink-0"
            >
              <span
                class="text-[9px] uppercase font-bold leading-none text-slate-500"
              >
                {{ getMonth(person.next_birthday) }}
              </span>
              <span class="text-sm font-bold leading-tight">
                {{ getDay(person.next_birthday) }}
              </span>
            </div>

            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-slate-900 truncate">
                {{ person.employee_name }}
              </p>
              <p class="text-xs text-slate-500 flex items-center gap-1.5">
                <span>In {{ person.days_until }} days</span>
              </p>
            </div>
          </div>
        </div>

        <!-- Empty birthdays -->
        <div
          v-else-if="!todayBirthdays.length"
          class="p-8 text-center flex flex-col items-center justify-center h-48"
        >
          <div
            class="h-10 w-10 rounded-full bg-slate-50 flex items-center justify-center mb-3"
          >
            <svg
              class="h-5 w-5 text-slate-300"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
          <p class="text-sm text-slate-500">No birthdays on the horizon.</p>
        </div>
      </article>
    </div>

    <!-- TEAM OFFBOARDING -->
    <article
      class="rounded-[28px] bg-white/80 border border-[#498528] 
             shadow-[0_24px_60px_rgba(15,23,42,0.12)] overflow-hidden backdrop-blur-xl"
    >
      <header
        class="border-b border-[#498528]/30 px-6 py-4 flex flex-col sm:flex-row 
               sm:items-center sm:justify-between gap-4 
               bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70"
      >
        <div>
          <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
            Transitions
          </p>
          <h2 class="text-base font-bold text-slate-900">Team Offboarding</h2>
          <p class="text-xs text-slate-500 mt-0.5">
            Monitor progress and exit requirements
          </p>
        </div>
      </header>

      <div v-if="teamOffboarding.length" class="divide-y divide-slate-100/80">
        <div
          v-for="member in teamOffboarding"
          :key="member.member_id"
          class="flex flex-col md:flex-row md:items-center justify-between 
                 px-6 py-4 gap-4"
        >
          <div class="flex items-center gap-4">
            <div
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full 
                     bg-slate-100 text-slate-400"
            >
              <svg
                class="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm font-semibold text-slate-900">
                {{ member.name }}
              </p>
              <p class="text-xs text-slate-500">
                {{ member.job_title || 'Team member' }}
              </p>
            </div>
          </div>

          <div
            class="flex items-center justify-between md:justify-end gap-6 
                   w-full md:w-auto pl-14 md:pl-0"
          >
            <div class="flex flex-col items-start md:items-end">
              <span
                class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium 
                       ring-1 ring-inset"
                :class="getStatusColor(member.status)"
              >
                {{ member.stage }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="p-12 text-center">
        <p class="text-sm text-slate-500">
          No active offboarding processes.
        </p>
      </div>
    </article>
  </section>
</template>


<script>
import { parseKolkataISODate } from '@/utils/kolkataTime';

export default {
  name: 'ManagerPeople',
  props: {
    teamMembers: { type: Array, default: () => [] },
    teamEmptyMessage: String,
    birthdayWindow: Number,
    todayBirthdays: { type: Array, default: () => [] },
    upcomingBirthdays: { type: Array, default: () => [] },
    teamOffboarding: { type: Array, default: () => [] },
    teamLabel: { type: String, default: 'Roster' },
    teamManagerId: { type: [String, Number], default: null },
  },
  methods: {
    isManager(member) {
      if (!member) {
        return false;
      }
      if (member.is_manager || member.is_manager_override) {
        return true;
      }
      if (!this.teamManagerId) {
        return false;
      }
      return String(member.id) === String(this.teamManagerId);
    },
    // Generates a consistent 2-letter string from a name
    getInitials(name) {
      if (!name) return '??';
      return name
        .split(' ')
        .map(n => n[0])
        .slice(0, 2)
        .join('')
        .toUpperCase();
    },
    // Extracts short month name
    getMonth(dateVal) {
      const date = this.parseISODate(dateVal);
      return date ? date.toLocaleDateString('en-US', { month: 'short' }) : '';
    },
    // Extracts day number
    getDay(dateVal) {
      const date = this.parseISODate(dateVal);
      return date ? date.getDate() : '';
    },
    parseISODate(value) {
      if (!value) return null;
      if (value instanceof Date) return value;
      return parseKolkataISODate(value) || new Date(value);
    },
    formatRelativeDate(value) {
      if (!value) return '';
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return '';
      const diffMs = Date.now() - date.getTime();
      const minutes = Math.round(diffMs / 60000);
      if (minutes < 60) return `${minutes}m ago`;
      const hours = Math.round(minutes / 60);
      if (hours < 24) return `${hours}h ago`;
      const days = Math.round(hours / 24);
      return `${days}d ago`;
    },
    getStatusColor(status) {
      // Map your backend statuses to visual styles
      const map = {
        'critical': 'bg-rose-50 text-rose-700 ring-rose-600/20',
        'warning': 'bg-amber-50 text-amber-700 ring-amber-600/20',
        'success': 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
        'neutral': 'bg-slate-50 text-slate-600 ring-slate-500/10'
      };
      return map[status] || map['neutral'];
    }
  }
};
</script>
