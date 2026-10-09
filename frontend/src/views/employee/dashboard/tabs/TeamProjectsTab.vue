<template>
  <section class="space-y-10">
    <div class="grid grid-cols-1 items-start gap-8 xl:grid-cols-3">
      <!-- TEAM ROSTER -->
      <article
        class="xl:col-span-2 flex h-full flex-col overflow-hidden rounded-[28px] border border-[#498528] 
               bg-white/80 shadow-[0_24px_60px_rgba(15,23,42,0.12)] backdrop-blur-xl"
      >
        <header
          class="flex items-center justify-between border-b border-[#498528]/30 
                 bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70 px-6 py-4"
        >
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
              Team overview
            </p>
            <h2 class="text-base font-bold text-slate-900 mt-1">Team {{ teamLabel }}</h2>
            <p class="mt-0.5 text-xs font-medium text-slate-500">Your immediate collaborators</p>
          </div>
          <span
            class="rounded-full border border-[#498528]/30 bg-[#DDEED1] px-3 py-1 text-[10px] font-semibold 
                   uppercase tracking-[0.25em] text-[#2F4C1C]"
          >
            {{ teamMembers.length }} Members
          </span>
        </header>

        <div v-if="teamMembers.length" class="divide-y divide-slate-100/70">
          <div
            v-for="member in teamMembers"
            :key="member.id || member.email || member.name"
            :class="[
              'group flex items-center justify-between px-6 py-3.5 transition-all',
              isManager(member)
                ? 'bg-[#DDEED1] border-l-4 border-[#498528] hover:bg-[#d2e6c4]'
                : 'hover:bg-slate-50/80'
            ]"
          >
            <div class="flex items-center gap-4">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold 
                       ring-1 ring-inset"
                :class="isManager(member)
                  ? 'bg-[#DDEED1] text-[#2F4C1C] ring-[#498528]/50'
                  : 'bg-emerald-50 text-emerald-700 ring-emerald-100'"
              >
                {{ getInitials(member.name) }}
              </div>
              <div class="flex flex-col">
                <p class="flex items-center gap-2 text-sm font-semibold text-slate-900">
                  {{ member.name || 'Teammate' }}
                  <span
                    v-if="member.is_self"
                    class="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600"
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
                <!-- <p class="text-xs font-medium text-slate-500">
                  {{ member.job_title || member.employment_role || 'Member' }}
                </p> -->
              </div>
            </div>

            <!-- <a
              v-if="member.email"
              :href="'mailto:' + member.email"
              class="invisible rounded-full p-2 text-slate-400 transition-all 
                     hover:bg-[#DDEED1]/70 hover:text-[#2F4C1C] 
                     group-hover:visible focus:visible focus:outline-none 
                     focus:ring-2 focus:ring-[#498528]/60"
              :title="`Email ${member.name || 'teammate'}`"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            </a> -->
          </div>
        </div>

        <div v-else class="p-8 text-center">
          <p class="text-sm text-slate-500">{{ teamEmptyMessage }}</p>
        </div>
      </article>

      <!-- UPCOMING BIRTHDAYS -->
      <article
        class="flex h-full flex-col overflow-hidden rounded-[28px] border border-[#498528] 
               bg-white/80 shadow-[0_24px_60px_rgba(15,23,42,0.1)] backdrop-blur-xl"
      >
        <header
          class="border-b border-[#498528]/30 bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70 
                 px-6 py-4"
        >
          <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
            Celebrations
          </p>
          <h2 class="text-base font-bold text-slate-900 mt-1">Upcoming birthdays</h2>
          <p class="mt-0.5 text-xs text-slate-500 text-left">
            Next {{ birthdayWindow }} days
          </p>
        </header>

        <!-- Today birthdays -->
        <div
          v-if="todayBirthdays.length"
          class="border-b border-amber-200/60 bg-amber-50/70 px-6 py-4"
        >
          <p class="mb-3 flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-[0.25em] text-amber-700">
            <span class="relative flex h-2 w-2">
              <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-amber-400 opacity-75"></span>
              <span class="relative inline-flex h-2 w-2 rounded-full bg-amber-500"></span>
            </span>
            Today
          </p>
          <ul class="space-y-3">
            <li
              v-for="person in todayBirthdays"
              :key="`today-${person.employee_id || person.employee_name || person.name}`"
              class="flex items-center justify-between"
            >
              <div class="flex items-center gap-3">
                <div
                  class="flex h-8 w-8 items-center justify-center rounded-full bg-white text-xs font-bold 
                         text-amber-600 ring-1 ring-amber-200 shadow-sm"
                >
                  🎂
                </div>
                <span class="text-sm font-bold text-slate-900">
                  {{ person.employee_name || person.name }}
                </span>
              </div>
            </li>
          </ul>
        </div>

        <!-- Upcoming birthdays -->
        <div v-if="upcomingBirthdays.length" class="divide-y divide-slate-100/70">
          <div
            v-for="person in upcomingBirthdays"
            :key="person.employee_id || person.employee_name || person.name"
            class="flex items-center gap-4 px-6 py-3.5"
          >
            <div
              class="flex h-10 w-10 shrink-0 flex-col items-center justify-center rounded-[14px] 
                     border border-[#498528]/30 bg-[#DDEED1] text-[#2F4C1C]"
            >
              <span class="text-[9px] font-bold uppercase leading-none text-[#2F4C1C]/70">
                {{ getMonth(person.next_birthday || person.date) }}
              </span>
              <span class="text-sm font-bold leading-tight">
                {{ getDay(person.next_birthday || person.date) }}
              </span>
            </div>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-semibold text-slate-900">
                {{ person.employee_name || person.name }}
              </p>
              <p class="text-xs text-slate-500">
                In {{ person.days_until || calculateDaysUntil(person.next_birthday || person.date) }} days
              </p>
            </div>
          </div>
        </div>

        <!-- No birthdays -->
        <div
          v-else-if="!todayBirthdays.length"
          class="flex h-48 flex-col items-center justify-center p-8 text-center"
        >
          <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-slate-50">
            <svg class="h-5 w-5 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
      class="flex flex-col overflow-hidden rounded-[28px] border border-[#498528] 
             bg-white/80 shadow-[0_24px_60px_rgba(15,23,42,0.12)] backdrop-blur-xl"
    >
      <header
        class="border-b border-[#498528]/30 bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70 
               px-6 py-4"
      >
        <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
          Lifecycle
        </p>
        <h2 class="text-base font-bold text-slate-900 mt-1">Team offboarding</h2>
        <p class="mt-0.5 text-xs text-slate-500">Monitor progress and exit requirements</p>
      </header>

      <div v-if="teamOffboarding.length" class="divide-y divide-slate-100/70">
        <div
          v-for="member in teamOffboarding"
          :key="member.member_id || member.id || member.email || member.name"
          class="flex flex-col gap-4 px-6 py-4 md:flex-row md:items-center md:justify-between"
        >
          <div class="flex items-center gap-4">
            <div
              class="flex h-10 w-10 items-center justify-center rounded-full bg-slate-50 text-slate-400 
                     ring-1 ring-slate-200"
            >
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
                {{ member.name || 'Team member' }}
              </p>
              <p class="text-xs text-slate-500">
                {{ member.job_title || member.role || 'Team member' }}
              </p>
            </div>
          </div>

          <div class="flex w-full items-center justify-between gap-6 pl-10 md:w-auto md:justify-end md:pl-0">
            <div class="flex flex-col items-start md:items-end">
              <span
                class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset"
                :class="getStatusColor(member.status)"
              >
                {{ member.stage || member.status_label || 'In progress' }}
              </span>
            </div>
            <button
              class="text-slate-400 transition-colors hover:text-[#2F4C1C]"
              type="button"
            >
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div v-else class="p-12 text-center text-sm text-slate-500">
        No active offboarding processes.
      </div>
    </article>

    <!-- PROJECT ASSIGNMENTS -->
    <article
      class="space-y-0 overflow-hidden rounded-[28px] border border-[#498528] 
             bg-white/80 shadow-[0_24px_60px_rgba(15,23,42,0.12)] backdrop-blur-xl"
    >
      <header
        class="flex flex-col gap-1 border-b border-[#498528]/30 
               bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70 px-6 py-4 
               sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
            Workload
          </p>
          <h2 class="text-base font-bold text-slate-900 mt-1">Project assignments</h2>
          <p class="text-xs text-slate-500">
            Latest manager updates and active work
          </p>
        </div>
        <p
          v-if="projectSummaryText"
          class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400 mt-2 sm:mt-0"
        >
          {{ projectSummaryText }}
        </p>
      </header>

      <div class="space-y-6 px-6 py-6">
        <!-- Manager announcement -->
        <div
          v-if="projectAnnouncement"
          class="rounded-[20px] border border-[#498528]/30 bg-[#DDEED1]/70 px-5 py-4"
        >
          <p class="text-[11px] font-bold uppercase tracking-[0.35em] text-[#2F4C1C]/70">
            Manager update
          </p>
          <h3 class="mt-1 text-base font-semibold text-slate-900">
            {{ projectAnnouncement.title }}
          </h3>
          <p class="mt-2 text-sm text-slate-700 whitespace-pre-line">
            {{ projectAnnouncement.description }}
          </p>
        </div>

        <div
          v-else
          class="rounded-[20px] border border-dashed border-slate-200 bg-white px-5 py-6 text-sm text-slate-500"
        >
          Your manager's project updates will appear here when shared.
        </div>

        <!-- Assignment list -->
        <div
          v-if="projectAssignments.length"
          class="overflow-hidden rounded-[20px] border border-slate-100/80 bg-white/80"
        >
          <ul class="divide-y divide-slate-100/80">
            <li
              v-for="assignment in projectAssignments"
              :key="assignment.name + (assignment.start_date || '')"
              class="flex flex-col gap-3 px-5 py-4 md:flex-row md:items-center md:justify-between"
            >
              <div class="space-y-1">
                <div class="flex flex-wrap items-center gap-2">
                  <h3 class="text-sm font-semibold text-slate-900">
                    {{ assignment.name || 'Project' }}
                  </h3>
                  <span
                    v-if="assignment.is_active"
                    class="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700"
                  >
                    Active
                  </span>
                </div>
                <p v-if="assignment.role" class="text-xs text-slate-500">
                  {{ assignment.role }}
                </p>
                <p v-if="assignment.client" class="text-xs text-slate-500">
                  Client · {{ assignment.client }}
                </p>
                <p v-if="assignment.summary" class="text-xs text-slate-500">
                  {{ assignment.summary }}
                </p>
              </div>
              <div class="text-xs text-slate-400">
                {{ formatAssignmentRange(assignment.start_date, assignment.end_date) }}
              </div>
            </li>
          </ul>
        </div>
      </div>
    </article>
  </section>
</template>

<script>
import { parseKolkataISODate, startOfKolkataDay } from '@/utils/kolkataTime';

export default {
  name: 'TeamProjectsTab',
  inject: ['employeeDashboardContext'],
  computed: {
    ctx() {
      return this.employeeDashboardContext;
    },
    teamMembers() {
      const overviewMembers =
        this.ctx.teamOverview && Array.isArray(this.ctx.teamOverview.members)
          ? [...this.ctx.teamOverview.members]
          : [...(this.ctx.teamMembers || [])];
      const manager = this.teamManager;
      if (manager) {
        const exists = overviewMembers.some((member) =>
          this.isSamePerson(member, manager)
        );
        if (!exists) {
          overviewMembers.unshift({ ...manager, is_self: manager.id === this.ctx.profile?.id });
        } else {
          overviewMembers.forEach((member, index) => {
            if (this.isSamePerson(member, manager)) {
              overviewMembers[index] = { ...member, is_manager_override: true };
            }
          });
        }
      }
      return overviewMembers.filter((member) => this.isActiveMember(member));
    },
    teamEmptyMessage() {
      if (this.ctx.teamOverview && this.ctx.teamOverview.empty_message) {
        return this.ctx.teamOverview.empty_message;
      }
      return this.ctx.teamEmptyMessage || 'No teammates recorded yet.';
    },
    teamManager() {
      return (this.ctx.teamOverview && this.ctx.teamOverview.manager) || null;
    },
    teamLabel() {
      const overview = this.ctx.teamOverview || {};
      return overview.team_name || overview.team_number || 'Team Roster';
    },
    birthdayWindow() {
      const overview = this.ctx.teamOverview || {};
      return overview.birthday_window || overview.birthdayWindow || 30;
    },
    todayBirthdays() {
      const birthdays = (this.ctx.teamOverview && this.ctx.teamOverview.birthdays) || {};
      return Array.isArray(birthdays.today) ? birthdays.today : [];
    },
    upcomingBirthdays() {
      const birthdays = (this.ctx.teamOverview && this.ctx.teamOverview.birthdays) || {};
      const list = Array.isArray(birthdays.upcoming) ? birthdays.upcoming : [];
      return list.slice(0, 6);
    },
    teamOffboarding() {
      const overview = this.ctx.teamOverview || {};
      const entries = Array.isArray(overview.offboarding) ? overview.offboarding : [];
      if (entries.length) {
        return entries.map((entry) => ({
          member_id: entry.member_id || entry.id,
          name: entry.name || entry.employee_name,
          job_title: entry.job_title || entry.role,
          status: entry.status || entry.statusClass || 'neutral',
          stage: entry.stage || entry.status_label,
          last_updated: entry.last_updated || entry.updated_at || entry.updatedAt,
        }));
      }
      if (this.ctx.offboardingCard) {
        const card = this.ctx.offboardingCard;
        return [
          {
            member_id: this.ctx.profile?.id || 'self',
            name: this.ctx.displayName,
            job_title: this.ctx.displayJobTitle || 'Employee',
            status: 'warning',
            stage: card.status_label,
            last_updated: card.last_day,
          },
        ];
      }
      return [];
    },
    projectAssignments() {
      return this.ctx.projectList || [];
    },
    projectAnnouncement() {
      return this.ctx.projectAnnouncement;
    },
    projectSummaryText() {
      return this.ctx.projectSummaryText;
    },
  },
  methods: {
    getInitials(name) {
      if (!name) {
        return '??';
      }
      return name
        .split(' ')
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0].toUpperCase())
        .join('');
    },
    getMonth(value) {
      const date = this.parseDate(value);
      return date
        ? date.toLocaleDateString('en-IN', { month: 'short', timeZone: 'Asia/Kolkata' })
        : '';
    },
    getDay(value) {
      const date = this.parseDate(value);
      return date ? date.getDate() : '';
    },
    parseDate(value) {
      if (!value) {
        return null;
      }
      if (value instanceof Date) {
        return value;
      }
      const parsed = parseKolkataISODate(value);
      if (parsed) {
        return parsed;
      }
      const fallback = new Date(value);
      return Number.isNaN(fallback.getTime()) ? null : fallback;
    },
    calculateDaysUntil(date) {
      const parsed = this.parseDate(date);
      if (!parsed) {
        return '-';
      }
      const today = startOfKolkataDay(new Date());
      const target = startOfKolkataDay(parsed);
      if (!today || !target) {
        return '-';
      }
      const diff = target.getTime() - today.getTime();
      return Math.max(0, Math.round(diff / 86400000));
    },
    isActiveMember(member) {
      if (!member) {
        return false;
      }
      if (member.active === false || member.is_active === false) {
        return false;
      }
      const blockedStatuses = new Set(['inactive', 'offboarded', 'terminated', 'archived']);
      const statusValues = [
        member.status,
        member.state,
        member.status_label,
        member.stage,
        member.employment_status,
      ];
      const normalizedStatus = statusValues
        .filter(Boolean)
        .map((value) => String(value).trim().toLowerCase());
      return !normalizedStatus.some((value) => blockedStatuses.has(value));
    },
    isManager(member) {
      if (!member) {
        return false;
      }
      if (member.is_manager_override || member.is_manager) {
        return true;
      }
      const teamManager = this.teamManager;
      if (!teamManager) {
        return false;
      }
      return this.isSamePerson(member, teamManager);
    },
    isSamePerson(member, other) {
      if (!member || !other) {
        return false;
      }
      const normalize = (value) => (value == null ? '' : String(value).trim().toLowerCase());
      const aIds = [member.id, member.employee_id, member.email].map(normalize).filter(Boolean);
      const bIds = [other.id, other.employee_id, other.email].map(normalize).filter(Boolean);
      return aIds.some((a) => bIds.includes(a));
    },
    getStatusColor(status) {
      const map = {
        critical: 'bg-rose-50 text-rose-700 ring-rose-600/20',
        warning: 'bg-amber-50 text-amber-700 ring-amber-600/20',
        success: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
        neutral: 'bg-slate-50 text-slate-600 ring-slate-500/10',
      };
      return map[status] || map.neutral;
    },
    formatRelative(value) {
      if (typeof this.ctx.formatRelativeDate === 'function') {
        return this.ctx.formatRelativeDate(value);
      }
      return this.defaultRelativeFormatter(value);
    },
    defaultRelativeFormatter(value) {
      if (!value) {
        return '';
      }
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) {
        return '';
      }
      const diffMs = Date.now() - date.getTime();
      const minutes = Math.round(diffMs / 60000);
      if (minutes < 1) {
        return 'Just now';
      }
      if (minutes < 60) {
        return `${minutes}m ago`;
      }
      const hours = Math.round(minutes / 60);
      if (hours < 24) {
        return `${hours}h ago`;
      }
      const days = Math.round(hours / 24);
      return `${days}d ago`;
    },
    formatAssignmentRange(start, end) {
      if (typeof this.ctx.formatAbsoluteDate === 'function') {
        const from = this.ctx.formatAbsoluteDate(start);
        const to = this.ctx.formatAbsoluteDate(end);
        return `${from} - ${to}`;
      }
      return `${start || '-'} - ${end || '-'}`;
    },
  },
};
</script>
