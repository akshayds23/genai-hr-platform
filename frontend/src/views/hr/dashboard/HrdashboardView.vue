<template>
  <div class="min-h-screen bg-[#f9f9f9] text-slate-900 flex font-sans">
    <!-- Sidebar -->
    <aside
      :class="[
        'hidden lg:flex bg-white/95 text-slate-700 flex-col fixed inset-y-0 border-r border-slate-200 shadow-[0_25px_60px_rgba(15,23,42,0.12)] z-40 transition-all duration-300',
        sidebarCollapsed ? 'w-20' : 'w-72'
      ]"
    >
      <div class="relative border-b border-slate-200/80 p-6 bg-white/90">
        <button
          class="absolute -right-3 top-6 rounded-full bg-slate-100 border border-slate-300 text-slate-500 p-1.5 transition hover:bg-slate-200 hover:shadow"
          type="button"
          aria-label="Toggle sidebar"
          @click.stop="toggleSidebar"
        >
          <span class="text-xs font-bold">{{sidebarCollapsed ? '»' : '«' }}</span>
        </button>
        <router-link
          :class="[
            'inline-flex items-center transition-all duration-200',
            sidebarCollapsed ? 'w-full justify-center' : 'mb-4'
          ]"
          to="/"
          aria-label="Alveon home"
        >
          <BrandLogo size="sm" :hide-text="sidebarCollapsed" />
        </router-link>
        <div v-if="!sidebarCollapsed">
          <p class="text-xs uppercase tracking-[0.35em] text-slate-500">HR Workspace</p>
          <h1 class="mt-1 text-xl font-bold text-slate-900">Operations Center</h1>
          <p class="mt-1 text-sm text-slate-500">Super admin control for company-wide insights.</p>
        </div>
      </div>

      <nav class="flex-1 overflow-y-auto p- space-y-2 bg-white/90">
        <button
          v-for="item in navItems"
          :key="item.value"
          type="button"
          @click.stop="setActiveTab(item.value)"
          :title="sidebarCollapsed ? item.label : ''"
          :class="[
            'group relative w-full flex items-center text-left transition-all duration-200 rounded-none',
            sidebarCollapsed ? 'justify-center px-2 py-3 border-l-0' : 'justify-between px-4 py-3 border-l-4',
            activeTab === item.value
              ? 'bg-white text-slate-900 border-slate-300 font-semibold'
              : 'bg-white text-slate-600 border-transparent hover:border-slate-300 hover:text-slate-900'
          ]"
        >
          <div :class="['flex items-center gap-3', sidebarCollapsed ? '' : 'flex-1']">
            <!-- ICON COLOR SYSTEM IDENTICAL TO MANAGER UI -->
            <span
              :class="[
                'flex h-9 w-9 items-center justify-center border transition-all duration-200 rounded-lg',

                // --- OVERVIEW (BLUE) ---
                item.value === 'overview'
                  ? activeTab === 'overview'
                    ? 'border-blue-500 bg-blue-600 text-white'
                    : 'border-transparent bg-blue-500 text-white group-hover:bg-blue-600'

                // --- USER MANAGEMENT / TEAM MANAGEMENT (SKY BLUE) ---
                : item.value === 'userManagement' || item.value === 'teamManagement'
                  ? activeTab === item.value
                    ? 'border-sky-500 bg-sky-600 text-white'
                    : 'border-transparent bg-sky-500 text-white group-hover:bg-sky-600'

                // --- APPROVALS (AMBER) ---
                : item.value === 'approvals'
                  ? activeTab === 'approvals'
                    ? 'border-amber-500 bg-amber-600 text-white'
                    : 'border-transparent bg-amber-500 text-white group-hover:bg-amber-600'

                // --- QUESTIONS (INDIGO) ---
                : item.value === 'questions'
                  ? activeTab === 'questions'
                    ? 'border-indigo-500 bg-indigo-600 text-white'
                    : 'border-transparent bg-indigo-500 text-white group-hover:bg-indigo-600'

                // --- NOTIFICATIONS (ROSE) ---
                : item.value === 'notifications'
                  ? activeTab === 'notifications'
                    ? 'border-rose-500 bg-rose-600 text-white'
                    : 'border-transparent bg-rose-500 text-white group-hover:bg-rose-600'

                // --- RESUMES (PURPLE) ---
                : item.value === 'resumes'
                  ? activeTab === 'resumes'
                    ? 'border-purple-500 bg-purple-600 text-white'
                    : 'border-transparent bg-purple-500 text-white group-hover:bg-purple-600'

                // --- JD MAKER (PINK) ---
                : item.value === 'jdMaker'
                  ? activeTab === 'jdMaker'
                    ? 'border-pink-500 bg-pink-600 text-white'
                    : 'border-transparent bg-pink-500 text-white group-hover:bg-pink-600'

                // --- LETTERS (BLUE) ---
                : item.value === 'letters'
                  ? activeTab === 'letters'
                    ? 'border-blue-500 bg-blue-600 text-white'
                    : 'border-transparent bg-blue-500 text-white group-hover:bg-blue-600'

                // --- BIRTHDAYS (GREEN) ---
                : item.value === 'birthdays'
                  ? activeTab === 'birthdays'
                    ? 'border-green-500 bg-green-600 text-white'
                    : 'border-transparent bg-green-500 text-white group-hover:bg-green-600'

                // --- OFFBOARDING (ROSE) ---
                : item.value === 'offboarding'
                  ? activeTab === 'offboarding'
                    ? 'border-rose-500 bg-rose-600 text-white'
                    : 'border-transparent bg-rose-500 text-white group-hover:bg-rose-600'

                // --- FEEDBACK (AMBER) ---
                : item.value === 'feedback'
                  ? activeTab === 'feedback'
                    ? 'border-amber-500 bg-amber-600 text-white'
                    : 'border-transparent bg-amber-500 text-white group-hover:bg-amber-600'

                // --- FAQs (INDIGO) ---
                : item.value === 'faqs'
                  ? activeTab === 'faqs'
                    ? 'border-indigo-500 bg-indigo-600 text-white'
                    : 'border-transparent bg-indigo-500 text-white group-hover:bg-indigo-600'

                // --- DEFAULT ---
                : 'border-slate-200 bg-slate-100 text-slate-600 group-hover:bg-slate-200'
              ]"
            >
              <SidebarIcon :name="item.icon || item.value" />
            </span>
            <span v-if="!sidebarCollapsed" class="font-semibold tracking-tight text-slate-800">{{ item.label }}</span>
          </div>
          <span
            v-if="!sidebarCollapsed && item.badge && item.badge()"
            class="bg-slate-200 text-slate-700 text-xs px-2 py-0.5 rounded-full font-semibold min-w-[20px] text-center"
          >
            {{ item.badge() }}
          </span>
        </button>
      </nav>

      <div class="p-4 border-t border-slate-200/80 space-y-3 bg-white">
        <div
          :class="[
            'flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3 shadow-sm',
            sidebarCollapsed ? 'justify-center' : ''
          ]"
        >
          <button
            :class="[
              'flex items-center gap-2 rounded-xl bg-transparent text-sm font-semibold text-slate-700 transition hover:bg-slate-50 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-200',
              sidebarCollapsed ? 'h-12 w-12 justify-center p-0' : 'w-full px-4 py-2'
            ]"
            type="button"
            :title="sidebarCollapsed ? 'Logout' : ''"
            @click="logout"
          >
            <ArrowRightOnRectangleIcon class="h-5 w-5 text-slate-500" aria-hidden="true" />
            <span v-if="!sidebarCollapsed">Logout</span>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <div :class="['flex-1 w-full flex flex-col min-h-screen transition-all duration-300', sidebarCollapsed ? 'lg:ml-20' : 'lg:ml-72']">
      <header class="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div class="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 md:px-8">
          <div class="flex w-full flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div class="mx-auto flex flex-col items-center text-center lg:flex-1">
              <p class="text-xs uppercase tracking-[0.35em] text-slate-500 font-semibold">Super Admin Console</p>
              <h1 class="text-2xl font-semibold text-slate-900">HR Operations Center</h1>
              <p class="text-sm text-slate-500">Lead company-wide people initiatives, insights, and support.</p>
            </div>
            <div class="flex flex-wrap items-center justify-center gap-3 lg:justify-end">
              <div class="relative">
                <button
                  class="relative flex h-11 w-11 items-center justify-center rounded-full border border-slate-200 bg-white text-xl text-slate-600 shadow-sm transition hover:bg-slate-50"
                  type="button"
                  aria-label="Notifications"
                  @click.stop="toggleNotifications"
                >
                  🔔
                  <span
                    v-if="unreadNotificationCount"
                    class="absolute -right-1 -top-1 inline-flex min-h-[20px] min-w-[20px] items-center justify-center rounded-full bg-slate-700 px-1 text-xs font-semibold text-white"
                  >
                    {{ unreadNotificationCount > 99 ? '99+' : unreadNotificationCount }}
                  </span>
                </button>
                <div
                  v-if="showNotifications"
                  class="absolute right-0 z-50 mt-3 w-[320px] origin-top-right rounded-2xl border border-slate-200 bg-white text-slate-900 shadow-xl"
                  @click.self="closeNotifications"
                >
                  <div class="flex items-center justify-between border-b border-slate-100 px-4 py-3">
                    <h3 class="text-sm font-semibold text-slate-800">Notifications</h3>
                    <button class="text-lg leading-none text-slate-400 transition hover:text-slate-600" type="button" @click="closeNotifications">&times;</button>
                  </div>
                  <div class="max-h-80 overflow-y-auto p-4">
                    <div v-if="notificationsLoading" class="py-6 text-center text-sm text-slate-500">Loading alerts...</div>
                    <div v-else-if="notificationsError" class="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-600">
                      {{ notificationsError }}
                    </div>
                    <ul v-else-if="notificationBellItems.length" class="space-y-3">
                      <li v-for="item in notificationBellItems" :key="item.id">
                        <div
                          class="relative flex gap-3 rounded-lg border border-slate-100 px-3 py-2 transition hover:border-slate-200 hover:bg-slate-50"
                          :class="{ 'border-slate-200 bg-slate-50': !item.isRead }"
                        >
                          <button
                            class="absolute -right-1 -top-1 h-5 w-5 rounded-full bg-slate-200 text-xs font-semibold text-slate-600 transition hover:bg-slate-300"
                            type="button"
                            @click.stop="dismissNotification(item)"
                          >
                            -
                          </button>
                          <div class="flex-1" @click.stop="markNotificationRead(item)">
                            <p class="text-sm font-semibold text-slate-800">{{ item.title }}</p>
                            <p v-if="item.message" class="mt-1 text-xs text-slate-500">{{ item.message }}</p>
                            <time v-if="item.createdAtLabel" class="mt-2 block text-xs text-slate-400">
                              {{ item.createdAtLabel }}
                            </time>
                          </div>
                        </div>
                      </li>
                    </ul>
                    <p v-else class="py-6 text-center text-sm text-slate-500">You're all caught up.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main class="px-6 py-8 max-w-7xl mx-auto w-full">
        <div class="bg-white rounded-3xl shadow-[0_25px_60px_rgba(15,23,42,0.12)] border border-slate-200 backdrop-blur-sm overflow-hidden">
          <OverviewTab v-if="activeTab === 'overview'" />
          <div v-else-if="activeTab === 'userManagement'" class="p-8">
            <UserManagementTab />
          </div>
          <div v-else-if="activeTab === 'teamManagement'" class="p-8">
            <TeamManagementTab />
          </div>
          <div v-else-if="activeTab === 'approvals'" class="p-8">
            <ApprovalsTab />
          </div>
          <div v-else-if="activeTab === 'questions'" class="p-8">
            <QuestionsTab />
          </div>
          <div v-else-if="activeTab === 'notifications'" class="p-8">
            <HrNotifications
              :notifications="normalizedNotifications"
              :loading="notificationsLoading"
              :error="notificationsError"
              @refresh="loadNotifications(true)"
              @mark-read="markNotificationRead"
              @dismiss="dismissNotification"
            />
          </div>
          <div v-else-if="activeTab === 'resumes'" class="p-8">
            <ResumesTab />
          </div>
          <div v-else-if="activeTab === 'jdMaker'" class="p-8">
            <JdMakerTab />
          </div>
          <div v-else-if="activeTab === 'letters'" class="p-8">
            <LettersTab />
          </div>
          <div v-else-if="activeTab === 'birthdays'" class="p-8">
            <BirthdaysTab />
          </div>
          <div v-else-if="activeTab === 'offboarding'" class="p-8">
            <OffboardingTab @open-letters="setActiveTab('letters')" />
          </div>
          <div v-else-if="activeTab === 'feedback'" class="p-8">
            <FeedbackTab />
          </div>
          <div v-else-if="activeTab === 'faqs'" class="p-8">
            <FaqsTab />
          </div>
        </div>
      </main>
    </div>

    <transition name="fade">
      <aside
        v-if="toast"
        :class="[
          'fixed bottom-8 right-8 z-50 flex items-center gap-4 rounded-2xl px-6 py-4 shadow-2xl backdrop-blur-sm border border-slate-200 bg-white/95 text-slate-900',
        ]"
      >
        <span class="text-base font-semibold">{{ toast.message }}</span>
        <button class="text-slate-500 hover:text-slate-900 transition-colors p-1 rounded-full hover:bg-slate-100" type="button" @click="dismissToast">✕</button>
      </aside>
    </transition>

    <div v-if="showAnswerModal" class="fixed inset-0 bg-gradient-to-br from-slate-900/70 via-slate-800/60 to-slate-900/70 backdrop-blur-sm flex items-center justify-center p-6 z-[1200]" @click.self="closeAnswerModal">
      <div class="w-full max-w-2xl rounded-3xl bg-white/95 backdrop-blur-xl p-8 shadow-2xl space-y-6 border border-white/20">
        <div class="space-y-2">
          <h3 class="text-2xl font-bold text-slate-900">Answer Question</h3>
          <div class="w-16 h-1 bg-gradient-to-r from-slate-300 to-slate-400 rounded-full"></div>
        </div>
        <div class="bg-gradient-to-r from-white to-white rounded-2xl p-6 border border-slate-200">
          <p class="text-lg font-bold text-slate-900 mb-2">{{ activeQuestion?.subject || 'Question' }}</p>
          <p class="text-base text-slate-700 leading-relaxed">{{ activeQuestion?.body || activeQuestion?.question }}</p>
        </div>
        <textarea
          v-model="answerDraft"
          class="w-full rounded-2xl border border-slate-200 px-4 py-4 focus:ring-4 focus:ring-slate-200 focus:border-slate-300 transition-all min-h-[140px] text-base"
          rows="6"
          placeholder="Type your detailed answer here..."
        ></textarea>
        <p v-if="answerError" class="text-sm text-rose-600 bg-rose-50 rounded-xl p-3 border border-rose-200">{{ answerError }}</p>
        <div class="flex items-center justify-end gap-4 pt-4">
          <button class="px-6 py-3 rounded-xl border border-slate-200 bg-white/80 text-slate-700 font-semibold hover:bg-white hover:shadow-lg transition-all" type="button" @click="closeAnswerModal">Cancel</button>
          <button
            class="px-6 py-3 rounded-xl border border-slate-300 bg-white text-slate-900 font-bold shadow-sm transition hover:bg-slate-50 disabled:opacity-60 disabled:cursor-not-allowed"
            type="button"
            :disabled="answerSubmitting"
            @click="submitAnswer"
          >
            {{ answerSubmitting ? 'Sending...' : 'Send Answer' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import axios from 'axios'
import { ArrowRightOnRectangleIcon } from '@heroicons/vue/24/outline'
import BrandLogo from '@/components/BrandLogo.vue'
import SidebarIcon from '@/components/SidebarIcon.vue'
import OverviewTab from './tabs/OverviewTab.vue'
import ApprovalsTab from './tabs/ApprovalsTab.vue'
import QuestionsTab from './tabs/QuestionsTab.vue'
import ResumesTab from './tabs/ResumesTab.vue'
import JdMakerTab from './tabs/JdMakerTab.vue'
import LettersTab from './tabs/LettersTab.vue'
import BirthdaysTab from './tabs/BirthdaysTab.vue'
import OffboardingTab from './tabs/OffboardingTab.vue'
import FeedbackTab from './tabs/FeedbackTab.vue'
import FaqsTab from './tabs/FaqsTab.vue'
import HrNotifications from './tabs/HrNotifications.vue'
import UserManagementTab from './tabs/UserManagementTab.vue'
import TeamManagementTab from './tabs/TeamManagementTab.vue'

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || '/api'
const AUTH_HEADER = 'Authentication-Token'

export default {
  name: 'HrdashboardView',
  components: {
    BrandLogo,
    SidebarIcon,
    ArrowRightOnRectangleIcon,
    OverviewTab,
    ApprovalsTab,
    QuestionsTab,
    ResumesTab,
    JdMakerTab,
    LettersTab,
    BirthdaysTab,
    OffboardingTab,
    FeedbackTab,
    FaqsTab,
    UserManagementTab,
    TeamManagementTab,
    HrNotifications,
  },
  provide() {
    return {
      hrDashboardContext: this,
    }
  },
  data() {
    return {
      activeTab: 'overview',
      userManagementIntent: null,
      sidebarCollapsed: false,
      filters: {
        query: '',
        employee_id: '',
        department: '',
        role: '',
        status: '',
      },
      departments: [],
      results: [],
      total: 0,
      page: 1,
      pageSize: 5,
      loadingResults: false,
      resultsError: '',
      managerLeaves: [],
      employeeLeaves: [],
      processingLeaves: {},
      managerLoading: false,
      employeeLoading: false,
      questions: [],
      questionsLoading: false,
      showAnswerModal: false,
      activeQuestion: null,
      answerDraft: '',
      answerError: '',
      answerSubmitting: false,
      resumeSummary: {
        pending: 0,
        shortlisted: 0,
        rejected: 0,
        total: 0,
      },
      analyticsOverview: {
        total_candidates: 0,
        average_experience: 0,
      },
      // Resumes table
      resumesList: [],
      resumesLoading: false,
      resumesError: '',
      resumesPage: 1,
      resumesPerPage: 20,
      resumesTotal: 0,
      recentResumes: [],
      resumeUploadFile: null,
      resumeUploadSource: '',
      resumeUploading: false,
      resumeUploadError: '',
      resumeInputKey: 0,
      bulkFiles: [],
      bulkInputKey: 0,
      bulkUploading: false,
      bulkUploadError: '',
      bulkUploadProgress: {
        show: false,
        total: 0,
        processed: 0,
        successful: 0,
        failed: 0,
        failedFiles: [],
        percentage: 0,
      },
      jdFile: null,
      jdInputKey: 0,
      jdForm: {
        title: '',
        department: '',
        description: '',
        skills: '',
        requirements: '',
        experience_required: '',
      },
      jdUploading: false,
      jdUploadError: '',
      jobDescriptions: [],
      selectedJobDescriptionId: null,
      matchTopN: 5,
      matching: false,
      matchResults: [],
      profileName: 'Super Admin',
      profileRole: 'Super Admin',
      toast: null,
      toastTimer: null,
      notifications: [],
      notificationsLoading: false,
      notificationsError: '',
      showNotifications: false,
      offboardingReport: [],
      offboardingLoading: false,
      offboardingError: '',
      // Birthday tracker data
      birthdayTracker: {
        today: [],
        upcoming: [],
        summary: {
          birthdays_today: 0,
        },
      },
      birthdayLoading: false,
      birthdayError: '',
      birthdayLoaded: false,
    }
  },
  computed: {
    navItems() {
      return [
        { value: 'overview', label: 'Overview', icon: 'overview' },
        { value: 'userManagement', label: 'Users', icon: 'userManagement' },
        { value: 'teamManagement', label: 'Teams', icon: 'userManagement' },
        {
          value: 'approvals',
          label: 'Approve Leaves',
          icon: 'approvals',
          badge: () => (this.employeeLeaves?.length || 0) || null,
        },
          {
            value: 'questions',
            label: 'Answer Questions',
            icon: 'questions',
            badge: () => (this.questions.length ? this.questions.length : null),
          },
          {
            value: 'notifications',
            label: 'Notifications',
            icon: 'notifications',
            badge: () => (this.unreadNotificationCount ? Math.min(this.unreadNotificationCount, 99) : null),
          },
          { value: 'resumes', label: 'Resumes', icon: 'resumes' },
        { value: 'jdMaker', label: 'JD Maker', icon: 'jdMaker' },
        { value: 'letters', label: 'Letter Templates', icon: 'letters' },
        {
          value: 'birthdays',
          label: 'Birthdays',
          icon: 'birthdays',
          badge: () =>
            this.birthdayTracker &&
            this.birthdayTracker.summary &&
            this.birthdayTracker.summary.birthdays_today
              ? this.birthdayTracker.summary.birthdays_today
              : null,
        },
        { value: 'offboarding', label: 'Offboarding', icon: 'offboarding' },
        { value: 'feedback', label: 'Feedback', icon: 'feedback' },
        { value: 'faqs', label: 'FAQs', icon: 'faqs' },
      ]
    },
    displayName() {
      return this.profileName
    },
    initials() {
      const parts = (this.displayName || '').trim().split(/\s+/)
      return parts.slice(0, 2).map((p) => p.charAt(0).toUpperCase()).join('') || 'SA'
    },
    totalPages() {
      return Math.max(Math.ceil(this.total / this.pageSize), 1)
    },
    showingLabel() {
      if (!this.total) return 'No results'
      const start = (this.page - 1) * this.pageSize + 1
      const end = Math.min(this.total, this.page * this.pageSize)
      return `${start}-${end} of ${this.total}`
    },
    statusCounts() {
      return this.results.reduce((acc, person) => {
        const status = person.status || 'unknown'
        acc[status] = (acc[status] || 0) + 1
        return acc
      }, {})
    },
    managerCount() {
      return this.results.filter((person) => (person.employment_role || person.role) === 'manager').length
    },
    recentResumeUploads() {
      return this.recentResumes.length
    },
    matchScoreLabel() {
      if (!this.resumeSummary.total) return 'Awaiting data'
      const ratio = this.resumeSummary.shortlisted / this.resumeSummary.total
      if (ratio >= 0.6) return 'Excellent'
      if (ratio >= 0.3) return 'Healthy'
      return 'Needs attention'
    },
    funnelHealthLabel() {
      if (!this.resumeSummary.total) return 'Building pipeline'
      const rejectionRatio = this.resumeSummary.rejected / this.resumeSummary.total
      if (rejectionRatio <= 0.4) return 'Balanced'
      if (rejectionRatio <= 0.7) return 'Watch list'
      return 'High drop-off'
    },
    overviewContext() {
      const resumeCount = this.resumesList.length
      const experienceSum = resumeCount
        ? this.resumesList.reduce((sum, r) => sum + (Number(r.total_experience) || 0), 0)
        : 0
      const derivedAverage = resumeCount ? experienceSum / resumeCount : 0
      const fallbackAverage = Number(derivedAverage.toFixed(1))
      const analyticsAverage = Number.isFinite(this.analyticsOverview.average_experience)
        ? this.analyticsOverview.average_experience
        : fallbackAverage
      const analyticsTotal = Number.isFinite(this.analyticsOverview.total_candidates)
        ? this.analyticsOverview.total_candidates
        : this.resumeSummary.total || 0
      const matchedCount = this.matchResults.length || this.resumeSummary.shortlisted || 0

      return {
        analytics: {
          total_candidates: analyticsTotal,
          average_experience: analyticsAverage,
        },
        jobDescriptions: this.jobDescriptions,
        matchedCandidates: this.matchResults,
        matchedCandidatesCount: matchedCount,
      }
    },
    timeToHireLabel() {
      if (this.resumeSummary.shortlisted >= 5) return 'Improving'
      if (this.resumeSummary.shortlisted) return 'Stable'
      return 'Collecting data'
    },
    unreadNotificationCount() {
      if (!Array.isArray(this.notifications)) {
        return 0
      }
      return this.notifications.filter((item) => item && (item.is_read === false || item.read === false)).length
    },
    normalizedNotifications() {
      if (!Array.isArray(this.notifications)) {
        return []
      }
      const normalized = this.notifications.map((item) => {
        const createdAt = item?.created_at || item?.createdAt || null
        let createdAtLabel = ''
        if (createdAt) {
          const date = new Date(createdAt)
          if (!Number.isNaN(date.getTime())) {
            createdAtLabel = date.toLocaleString('en-IN', {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
              timeZone: 'Asia/Kolkata',
            })
          }
        }
        return {
          id: item?.id,
          title: item?.title || 'Notification',
          message: item?.message || '',
          createdAt,
          createdAtLabel,
          isRead: item?.is_read === undefined ? Boolean(item?.isRead) : item.is_read === true,
          status: item?.status,
          metadata: item?.metadata,
        }
      })
      return normalized.sort((a, b) => {
        const aTime = a.createdAt ? new Date(a.createdAt).getTime() : 0
        const bTime = b.createdAt ? new Date(b.createdAt).getTime() : 0
        return bTime - aTime
      })
    },
    notificationBellItems() {
      return this.normalizedNotifications.filter((item) => !item.isRead)
    },
    topSourceLabel() {
      if (!this.recentResumes.length) return 'No recent uploads'
      const sources = this.recentResumes
        .map((item) => (item.source || '').trim())
        .filter(Boolean)
      if (!sources.length) return 'Mixed channels'
      const tally = sources.reduce((acc, source) => {
        acc[source] = (acc[source] || 0) + 1
        return acc
      }, {})
      return Object.entries(tally).sort((a, b) => b[1] - a[1])[0][0]
    },
    ctx() {
      return this
    },
  },
    watch: {
      activeTab(newValue) {
        try {
          localStorage.setItem('hrDashboardActiveTab', newValue)
        } catch (error) {
          console.warn('Unable to persist active tab selection', error)
        }
        if (newValue === 'notifications') {
          this.loadNotifications(true)
        }
      },
    },
  created() {
    this.loadUserFromStorage()
    const restoredTab = this.restoreActiveTab()
    if (restoredTab && restoredTab !== 'overview') {
      this.setActiveTab(restoredTab)
    }
    this.bootstrap()
  },
  beforeUnmount() {
    if (this.toastTimer) {
      clearTimeout(this.toastTimer)
    }
  },
  methods: {
    async bootstrap() {
        await Promise.allSettled([
          this.submitSearch(),
      this.loadManagerLeaves(),
      this.loadEmployeeLeaves(),
      this.loadQuestions(),
      this.loadNotifications(true),
      this.loadDepartments(),
      this.loadResumeSummary(),
      this.loadAnalyticsOverview(),
      this.loadJobDescriptions(),
      this.loadOffboardingReport(),
      this.loadBirthdayTracker(),
        ])
      },
    restoreActiveTab() {
      try {
        const savedTab = localStorage.getItem('hrDashboardActiveTab')
        const validTabs = new Set(this.navItems.map((item) => item.value))
        if (savedTab && validTabs.has(savedTab)) {
          this.activeTab = savedTab
          return savedTab
        }
        if (savedTab && !validTabs.has(savedTab)) {
          localStorage.removeItem('hrDashboardActiveTab')
        } else {
          localStorage.setItem('hrDashboardActiveTab', this.activeTab)
        }
      } catch (error) {
        console.warn('Unable to restore active tab selection', error)
      }
      return this.activeTab
    },
    setActiveTab(tab) {
      this.activeTab = tab
      if (tab === 'overview' && !this.results.length && !this.loadingResults) {
        this.submitSearch()
      }
      if (tab === 'approvals' && !this.employeeLeaves.length && !this.employeeLoading) {
        this.loadEmployeeLeaves()
      }
        if (tab === 'questions' && !this.questions.length && !this.questionsLoading) {
          this.loadQuestions()
        }
        if (tab === 'notifications') {
          this.loadNotifications(true)
        }
      if (tab === 'jdMaker' && !this.jobDescriptions.length && !this.jdUploading) {
        this.loadJobDescriptions()
      }
      if (tab === 'resumes' && !this.resumesList.length && !this.resumesLoading) {
        this.loadResumes()
      }
      if (tab === 'birthdays' && !this.birthdayLoaded && !this.birthdayLoading) {
        this.loadBirthdayTracker()
      }
      if (tab === 'offboarding' && !this.offboardingLoading) {
        this.loadOffboardingReport()
      }
    },
    launchUserDirectory(action = null) {
      if (action) {
        this.userManagementIntent = { type: action, timestamp: Date.now() }
      } else {
        this.userManagementIntent = null
      }
      this.setActiveTab('userManagement')
    },
    acknowledgeUserManagementIntent() {
      this.userManagementIntent = null
    },
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
    loadUserFromStorage() {
      const raw = localStorage.getItem('currentUser')
      if (raw) {
        try {
          const parsed = JSON.parse(raw)
          const nameParts = [parsed.first_name, parsed.last_name].filter(Boolean)
          const fallback = parsed.full_name || parsed.username || parsed.email || this.profileName
          this.profileName = nameParts.length ? nameParts.join(' ') : fallback
          const roles = Array.isArray(parsed.roles) ? parsed.roles : []
          if (roles.includes('hr')) {
            this.profileRole = 'HR'
          } else if (roles.includes('manager')) {
            this.profileRole = 'Manager'
          } else {
            const roleValue = (parsed.employment_role || 'User').replace(/_/g, ' ')
            this.profileRole = roleValue.charAt(0).toUpperCase() + roleValue.slice(1)
          }
        } catch (error) {
          console.warn('Unable to parse cached user profile', error)
        }
      }
      const savedToken = localStorage.getItem('authToken')
      if (savedToken) {
        axios.defaults.headers.common[AUTH_HEADER] = savedToken
      } else {
        delete axios.defaults.headers.common[AUTH_HEADER]
      }
    },
    async loadDepartments() {
      try {
        const res = await axios.get(`${API_BASE_URL}/admin/departments`, { withCredentials: true })
        const items = Array.isArray(res.data?.departments) ? res.data.departments : []
        this.departments = items
      } catch (error) {
        this.departments = []
      }
    },
    async submitSearch() {
      this.loadingResults = true
      this.resultsError = ''
      try {
        const params = {
          ...this.filters,
          page: this.page,
          page_size: this.pageSize,
        }
        const res = await axios.get(`${API_BASE_URL}/admin/employees/search`, { params, withCredentials: true })
        this.results = Array.isArray(res.data?.results) ? res.data.results : []
        this.total = typeof res.data?.total === 'number' ? res.data.total : this.results.length
      } catch (error) {
        console.error('Employee search failed', error)
        this.resultsError = error?.response?.data?.error || error.message || 'Unable to search right now.'
        this.results = []
        this.total = 0
      } finally {
        this.loadingResults = false
      }
    },
    resetSearch() {
      this.filters = {
        query: '',
        employee_id: '',
        department: '',
        role: '',
        status: '',
      }
      this.page = 1
      this.submitSearch()
    },
    onSearchSubmit() {
      this.page = 1
      this.submitSearch()
    },
    prevPage() {
      if (this.page <= 1) return
      this.page -= 1
      this.submitSearch()
    },
    nextPage() {
      if (this.page >= this.totalPages) return
      this.page += 1
      this.submitSearch()
    },
    async loadManagerLeaves() {
      this.managerLoading = true
      try {
        const res = await axios.get(`${API_BASE_URL}/admin/leaves`, {
          params: { submitted_by: 'manager', status: 'pending' },
          withCredentials: true,
        })
        const items = Array.isArray(res.data?.leaves) ? res.data.leaves : []
        this.managerLeaves = items.map((leave) => ({
          ...leave,
          manager_name: leave.manager_name || leave.manager || leave.requested_by || 'Manager',
          date_range: leave.date_range || `${leave.start_date || 'N/A'} -> ${leave.end_date || 'N/A'}`,
        }))
      } catch (error) {
        console.error('Failed to load manager leaves', error)
        this.showToast('Unable to load manager approvals right now.', 'error')
        this.managerLeaves = []
      } finally {
        this.managerLoading = false
      }
    },
    async loadEmployeeLeaves() {
      this.employeeLoading = true
      try {
        const res = await axios.get(`${API_BASE_URL}/admin/leaves`, {
          params: { submitted_by: 'employee', status: 'pending' },
          withCredentials: true,
        })
        const items = Array.isArray(res.data?.leaves) ? res.data.leaves : []
        this.employeeLeaves = items.map((leave) => ({
          ...leave,
          employee_name:
            leave.manager_name ||
            leave.employee_name ||
            leave.requested_by ||
            'Employee',
          date_range: leave.date_range || `${leave.start_date || 'N/A'} -> ${leave.end_date || 'N/A'}`,
        }))
      } catch (error) {
        console.error('Failed to load employee leaves', error)
        this.showToast('Unable to load employee approvals right now.', 'error')
        this.employeeLeaves = []
      } finally {
        this.employeeLoading = false
      }
    },
    async actOnManagerLeave(leave, action) {
      if (!leave || !leave.id) return
      const question = action === 'approve' ? `Approve ${leave.manager_name}'s leave?` : `Reject ${leave.manager_name}'s leave?`
      if (!window.confirm(question)) return
      this.processingLeaves = { ...this.processingLeaves, [leave.id]: action }
      try {
        const endpoint =
          action === 'approve'
            ? `${API_BASE_URL}/admin/leaves/${leave.id}/approve`
            : `${API_BASE_URL}/admin/leaves/${leave.id}/reject`
        const payload = action === 'reject' ? { reason: 'Rejected by HR' } : {}
        await axios.post(endpoint, payload, { withCredentials: true })
        this.showToast(`Leave ${action === 'approve' ? 'approved' : 'rejected'} successfully.`, 'success')
        await Promise.all([this.loadManagerLeaves(), this.loadEmployeeLeaves()])
      } catch (error) {
        console.error('Failed to update leave status', error)
        this.showToast('Unable to update leave status.', 'error')
      } finally {
        const nextState = { ...this.processingLeaves }
        delete nextState[leave.id]
        this.processingLeaves = nextState
      }
    },
      async loadQuestions() {
        this.questionsLoading = true
        try {
          const res = await axios.get(`${API_BASE_URL}/admin/hr/questions`, {
            params: { status: 'pending' },
            withCredentials: true,
          })
        this.questions = Array.isArray(res.data?.questions) ? res.data.questions : []
        } catch (error) {
          console.error('Failed to load escalated questions', error)
          this.showToast('Unable to load HR questions right now.', 'error')
          this.questions = []
        } finally {
          this.questionsLoading = false
        }
      },
      async loadNotifications(force = false) {
        if (this.notificationsLoading) {
          return
        }
        if (!force && this.notifications.length) {
          return
        }
        this.notificationsLoading = true
        this.notificationsError = ''
        try {
          const res = await axios.get(`${API_BASE_URL}/notifications`, {
            params: { limit: 50 },
            withCredentials: true,
          })
          const items = Array.isArray(res.data?.notifications) ? res.data.notifications : []
          this.notifications = items
        } catch (error) {
          console.error('Failed to load notifications', error)
          this.notificationsError =
            error?.response?.data?.error || error.message || 'Unable to load notifications.'
          if (force) {
            this.notifications = []
          }
        } finally {
          this.notificationsLoading = false
        }
      },
      async markNotificationRead(notification, { remove = false } = {}) {
        if (!notification || !notification.id) {
          return
        }
        if (!notification.isRead && notification.is_read !== true) {
          try {
            await axios.post(
              `${API_BASE_URL}/notifications/${notification.id}/read`,
              {},
              { withCredentials: true },
            )
          } catch (error) {
            console.error('Failed to mark notification as read', error)
          }
        }
        let updated = this.notifications.map((item) =>
          item && item.id === notification.id
            ? { ...item, is_read: true, read: true, isRead: true }
            : item,
        )
        if (remove) {
          updated = updated.filter((item) => item && item.id !== notification.id)
        }
        this.notifications = updated
      },
      async dismissNotification(notification) {
        await this.markNotificationRead(notification, { remove: true })
      },
      async toggleNotifications() {
        if (this.showNotifications) {
          this.showNotifications = false
          return
        }
        this.showNotifications = true
        await this.loadNotifications(true)
      },
      closeNotifications() {
        this.showNotifications = false
      },
    openAnswerModal(question) {
      this.activeQuestion = question
      this.answerDraft = ''
      this.answerError = ''
      this.showAnswerModal = true
    },
    closeAnswerModal() {
      this.showAnswerModal = false
      this.activeQuestion = null
      this.answerDraft = ''
      this.answerError = ''
    },
    async submitAnswer() {
      if (!this.answerDraft.trim()) {
        this.answerError = 'Please add an answer before sending.'
        return
      }
      if (!this.activeQuestion || !this.activeQuestion.id) {
        this.answerError = 'Question information missing.'
        return
      }
      this.answerSubmitting = true
      this.answerError = ''
      try {
        await axios.post(
          `${API_BASE_URL}/admin/hr/questions/${this.activeQuestion.id}/answer`,
          { answer: this.answerDraft.trim() },
          { withCredentials: true },
        )
        this.showToast('Answer sent to the employee.', 'success')
        this.closeAnswerModal()
        await this.loadQuestions()
      } catch (error) {
        console.error('Failed to submit answer', error)
        this.answerError = error?.response?.data?.error || error.message || 'Unable to send answer right now.'
      } finally {
        this.answerSubmitting = false
      }
    },
    async loadResumeSummary() {
      try {
        const res = await axios.get(`${API_BASE_URL}/admin/resumes/summary`, { withCredentials: true })
        const payload = res.data || {}
        const summary = payload.summary || {}
        this.resumeSummary = {
          pending: summary.pending ?? 0,
          shortlisted: summary.shortlisted ?? 0,
          rejected: summary.rejected ?? 0,
          total: payload.total ?? (summary.pending ?? 0) + (summary.shortlisted ?? 0) + (summary.rejected ?? 0),
        }
        this.recentResumes = Array.isArray(payload.recent_uploads) ? payload.recent_uploads : []
      } catch (error) {
        this.resumeSummary = { pending: 0, shortlisted: 0, rejected: 0, total: 0 }
        this.recentResumes = []
      }
    },
    async loadAnalyticsOverview() {
      try {
        const res = await axios.get(`${API_BASE_URL}/hr/analytics/overview`, { withCredentials: true })
        const payload = res.data || {}
        this.analyticsOverview = {
          total_candidates: Number.isFinite(payload.total_candidates) ? payload.total_candidates : 0,
          average_experience: Number.isFinite(payload.average_experience) ? payload.average_experience : 0,
        }
      } catch (error) {
        console.error('Failed to load analytics overview', error)
        this.analyticsOverview = {
          total_candidates: 0,
          average_experience: 0,
        }
      }
    },
    async loadJobDescriptions() {
      try {
        const res = await axios.get(`${API_BASE_URL}/hr/jd`, { withCredentials: true })
        const items = Array.isArray(res.data?.job_descriptions) ? res.data.job_descriptions : []
        this.jobDescriptions = items.map((item) => ({
          ...item,
          requirements: Array.isArray(item.requirements)
            ? item.requirements
            : typeof item.requirements === 'string' && item.requirements
            ? item.requirements.split(',').map((value) => value.trim()).filter(Boolean)
            : [],
          skills_required: Array.isArray(item.skills_required)
            ? item.skills_required
            : typeof item.skills_required === 'string' && item.skills_required
            ? item.skills_required.split(',').map((value) => value.trim()).filter(Boolean)
            : [],
        }))
        if (!this.selectedJobDescriptionId && this.jobDescriptions.length) {
          this.selectedJobDescriptionId = this.jobDescriptions[0].id
        } else if (!this.jobDescriptions.length) {
          this.selectedJobDescriptionId = null
        }
    } catch (error) {
      console.error('Failed to load job descriptions', error)
      this.jobDescriptions = []
      this.selectedJobDescriptionId = null
    }
  },
  async loadOffboardingReport() {
    this.offboardingLoading = true
    this.offboardingError = ''
    try {
      const res = await axios.get(`${API_BASE_URL}/offboarding/report`, { withCredentials: true })
      this.offboardingReport = Array.isArray(res.data?.report) ? res.data.report : []
      return this.offboardingReport
    } catch (error) {
      console.error('Failed to load offboarding report', error)
      this.offboardingError = 'Connection failed. Please check your network.'
      return []
    } finally {
      this.offboardingLoading = false
    }
  },
  handleResumeFile(event) {
      const [file] = event.target.files || []
      this.resumeUploadFile = file || null
      this.resumeUploadError = ''
    },
    handleBulkFiles(event) {
      const files = Array.from(event.target.files || [])
      this.bulkFiles = files
      this.bulkUploadError = ''
      this.bulkUploadProgress = {
        show: false,
        total: files.length,
        processed: 0,
        successful: 0,
        failed: 0,
        failedFiles: [],
        percentage: 0,
      }
    },
    async triggerBulkUpload() {
      if (!this.bulkFiles || !this.bulkFiles.length) {
        this.bulkUploadError = 'Please select one or more files to upload.'
        return
      }
      this.bulkUploading = true
      this.bulkUploadError = ''
      this.bulkUploadProgress.show = true
      this.bulkUploadProgress.total = this.bulkFiles.length
      try {
        const formData = new FormData()
        for (let i = 0; i < this.bulkFiles.length; i++) {
          formData.append('files', this.bulkFiles[i])
        }
        if (this.resumeUploadSource) formData.append('source', this.resumeUploadSource)
        formData.append('max_workers', String(Math.min(10, this.bulkFiles.length)))

        const res = await axios.post(`${API_BASE_URL}/hr/resume/bulk-upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          withCredentials: true,
        })

        const results = res.data?.results || {}
        this.bulkUploadProgress.processed = results.processed || this.bulkUploadProgress.total
        this.bulkUploadProgress.successful = Array.isArray(results.successful) ? results.successful.length : 0
        this.bulkUploadProgress.failed = Array.isArray(results.failed) ? results.failed.length : 0
        this.bulkUploadProgress.failedFiles = results.failed || []
        this.bulkUploadProgress.percentage = Math.round((this.bulkUploadProgress.processed / this.bulkUploadProgress.total) * 100)

  this.showToast(res.data?.message || 'Bulk upload completed', 'success')
  await Promise.allSettled([this.loadResumeSummary(), this.loadJobDescriptions(), this.loadResumes()])
      } catch (err) {
        console.error('Bulk upload failed', err)
        this.bulkUploadError = err?.response?.data?.error || err.message || 'Bulk upload failed'
        this.bulkUploadProgress.failed = this.bulkUploadProgress.total
        this.bulkUploadProgress.failedFiles = [{ filename: 'bulk_upload', error: this.bulkUploadError }]
      } finally {
        this.bulkUploading = false
        this.bulkInputKey += 1
        this.bulkFiles = []
      }
    },
    handleJdFile(event) {
      const [file] = event.target.files || []
      this.jdFile = file || null
      this.jdUploadError = ''
    },
    async uploadResume() {
      if (!this.resumeUploadFile) {
        this.resumeUploadError = 'Please choose a resume file.'
        return
      }
      this.resumeUploading = true
      this.resumeUploadError = ''
      try {
        const formData = new FormData()
        formData.append('file', this.resumeUploadFile)
        if (this.resumeUploadSource) {
          formData.append('source', this.resumeUploadSource)
        }
        await axios.post(`${API_BASE_URL}/hr/resume/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          withCredentials: true,
        })
        this.showToast('Resume processed successfully.', 'success')
        this.resumeUploadFile = null
        this.resumeUploadSource = ''
        this.resumeInputKey += 1
        await Promise.allSettled([this.loadResumeSummary(), this.loadJobDescriptions()])
      } catch (error) {
        console.error('Resume upload failed', error)
        this.resumeUploadError =
          error?.response?.data?.error || error.message || 'Unable to process resume right now.'
      } finally {
        this.resumeUploading = false
      }
    },
    parseCommaList(value) {
      return value
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean)
    },
    async uploadJobDescription() {
      const title = this.jdForm.title.trim()
      const descriptionText = this.jdForm.description.trim()
      if (!title) {
        this.jdUploadError = 'Title is required.'
        return
      }
      if (!descriptionText && !this.jdFile) {
        this.jdUploadError = 'Add description text or upload a JD file.'
        return
      }
      this.jdUploading = true
      this.jdUploadError = ''
      try {
        const department = this.jdForm.department.trim()
        const skills = this.jdForm.skills.trim()
        const requirements = this.jdForm.requirements.trim()
        const experienceRaw = this.jdForm.experience_required
        const experience =
          typeof experienceRaw === 'string'
            ? experienceRaw.trim()
            : experienceRaw !== null && experienceRaw !== undefined
            ? String(experienceRaw).trim()
            : ''
        const skillsList = skills ? this.parseCommaList(skills) : []
        const requirementsList = requirements ? this.parseCommaList(requirements) : []

        if (this.jdFile) {
          const formData = new FormData()
          formData.append('file', this.jdFile)
          formData.append('title', title)
          if (department) formData.append('department', department)
          if (descriptionText) formData.append('description', descriptionText)
          if (skillsList.length) formData.append('skills_required', JSON.stringify(skillsList))
          if (requirementsList.length) formData.append('requirements', JSON.stringify(requirementsList))
          if (experience) {
            const parsed = Number.parseFloat(experience)
            if (!Number.isNaN(parsed)) {
              formData.append('experience_required', String(parsed))
            }
          }
          await axios.post(`${API_BASE_URL}/hr/jd/upload`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            withCredentials: true,
          })
        } else {
          const payload = {
            title,
            department: department || undefined,
            description: descriptionText,
          }
          if (skillsList.length) payload.skills_required = skillsList
          if (requirementsList.length) payload.requirements = requirementsList
          if (experience) {
            const parsed = Number.parseFloat(experience)
            if (!Number.isNaN(parsed)) {
              payload.experience_required = parsed
            }
          }
          await axios.post(`${API_BASE_URL}/hr/jd/upload`, payload, { withCredentials: true })
        }

        this.showToast('Job description saved.', 'success')
        this.jdForm = {
          title: '',
          department: '',
          description: '',
          skills: '',
          requirements: '',
          experience_required: '',
        }
        this.jdFile = null
        this.jdInputKey += 1
        await this.loadJobDescriptions()
      } catch (error) {
        console.error('JD upload failed', error)
        this.jdUploadError = error?.response?.data?.error || error.message || 'Unable to save JD right now.'
      } finally {
        this.jdUploading = false
      }
    },
    async loadResumes(page = 1) {
      this.resumesLoading = true
      this.resumesError = ''
      try {
        const res = await axios.get(`${API_BASE_URL}/hr/resumes`, {
          params: { page: page, per_page: this.resumesPerPage },
          withCredentials: true,
        })
        const payload = res.data || {}
        this.resumesList = Array.isArray(payload.resumes) ? payload.resumes : []
        if (payload.pagination) {
          this.resumesPage = payload.pagination.page || page
          this.resumesPerPage = payload.pagination.per_page || this.resumesPerPage
          this.resumesTotal = payload.pagination.total || this.resumesList.length
        } else {
          this.resumesPage = page
          this.resumesTotal = this.resumesList.length
        }
      } catch (err) {
        console.error('Failed to load resumes', err)
        this.resumesError = err?.response?.data?.error || err.message || 'Unable to load resumes'
        this.resumesList = []
        this.resumesTotal = 0
      } finally {
        this.resumesLoading = false
      }
    },
    formatReasoning(text) {
      if (!text) return '-'
      try {
        const s = String(text).replace(/\s+/g, ' ').trim()
        const sentences = s.match(/[^.!?]+[.!?]?/g) || [s]
        let first = (sentences[0] || '').trim()
        if (!first) return s.slice(0, 140) + (s.length > 140 ? '...' : '')
        // limit length
        if (first.length > 140) first = first.slice(0, 137) + '...'
        return first.replace(/[.?!]$/, '')
      } catch (e) {
        return (String(text) || '').slice(0, 140)
      }
    },
    formatSummary(text) {
      if (!text) return '-'
      try {
        const s = String(text).replace(/\s+/g, ' ').trim()
        const sentences = s.match(/[^.!?]+[.!?]?/g) || [s]
        const parts = sentences.map(ss => ss.trim().replace(/[.?!]$/, '')).filter(Boolean).slice(0, 2)
        // if parts are short, join with bullet; otherwise, use first truncated sentence
        if (parts.length === 0) return s.slice(0, 120)
        if (parts.join(' • ').length <= 140) return parts.join(' • ')
        // fallback to single truncated first sentence
        const first = parts[0]
        return first.length <= 140 ? first : first.slice(0, 137) + '...'
      } catch (e) {
        return (String(text) || '').slice(0, 140)
      }
    },
    async runMatching() {
      if (!this.selectedJobDescriptionId) {
        this.matchError = 'Select a job description first.'
        return
      }
      this.matchError = ''
      this.matching = true
      this.matchResults = []
      this.matchedJob = null
      try {
        const res = await axios.post(
          `${API_BASE_URL}/hr/jd/match`,
          {
            job_description_id: this.selectedJobDescriptionId,
            top_n: this.matchTopN || 5,
          },
          { withCredentials: true },
        )
        this.matchResults = Array.isArray(res.data?.matches) ? res.data.matches : []
        this.matchedJob = res.data?.job_description || null
        if (!this.matchResults.length) {
          this.matchError = 'No candidates matched this job description.'
        }
      } catch (error) {
        console.error('Matching failed', error)
        this.matchError = error?.response?.data?.error || error.message || 'Unable to run matching right now.'
      } finally {
        this.matching = false
      }
    },
    clearMatchResults() {
      this.matchResults = []
      this.matchedJob = null
      this.matchError = ''
    },
    formatMatchScore(score) {
      const numeric = typeof score === 'number' ? score : Number(score)
      if (Number.isNaN(numeric)) return '-'
      const percent = numeric <= 1 ? numeric * 100 : numeric
      return `${percent.toFixed(1)}%`
    },
    formatRequirementList(value) {
      if (Array.isArray(value)) {
        const cleaned = value.map((item) => (typeof item === 'string' ? item.trim() : '')).filter(Boolean)
        return cleaned.length ? cleaned.join(', ') : '-'
      }
      if (typeof value === 'string') {
        const cleaned = value
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean)
        return cleaned.length ? cleaned.join(', ') : '-'
      }
      return '-'
    },
    formatBirthdayEntry(entry) {
      const days = Number(entry?.days_until)
      const date = entry?.next_birthday ? new Date(entry.next_birthday) : null
      const dateLabel = date && !Number.isNaN(date.getTime())
        ? date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
        : ''
      if (days === 0) return dateLabel ? `Today - ${dateLabel}` : 'Today'
      if (Number.isNaN(days)) return dateLabel || '-'
      const unit = days === 1 ? 'day' : 'days'
      return `${days} ${unit} - ${dateLabel || 'Soon'}`
    },
    async loadBirthdayTracker() {
      this.birthdayLoading = true
      this.birthdayError = ''
      try {
        const res = await axios.get(`${API_BASE_URL}/birthday-tracker`, { 
          params: { days: 90 },
          withCredentials: true 
        })
        const today = Array.isArray(res.data?.today) ? res.data.today : []
        const upcomingAll = Array.isArray(res.data?.upcoming) ? res.data.upcoming : []
        const upcoming = upcomingAll.filter((entry) => Number(entry?.days_until) > 0)
        const summary = res.data?.summary || {}
        this.birthdayTracker = { today, upcoming, summary }
        this.birthdayLoaded = true
      } catch (error) {
        console.error('Failed to load birthday tracker', error)
        this.birthdayError = error?.response?.data?.error || error.message || 'Unable to load birthday tracker.'
      } finally {
        this.birthdayLoading = false
      }
    },

    showToast(message, type = 'info', duration = 4000) {
      this.toast = { message, type }
      if (this.toastTimer) {
        clearTimeout(this.toastTimer)
      }
      this.toastTimer = setTimeout(() => {
        this.toast = null
        this.toastTimer = null
      }, duration)
    },
    dismissToast() {
      if (this.toastTimer) {
        clearTimeout(this.toastTimer)
        this.toastTimer = null
      }
      this.toast = null
    },
    formatDate(value) {
      if (!value) {
        return '-'
      }
      try {
        const date = new Date(value)
        if (Number.isNaN(date.getTime())) {
          return '-'
        }
        return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
      } catch (error) {
        return '-'
      }
    },
    findUserName(userId) {
      if (!userId) {
        return 'Unknown User'
      }
      // Try to find in results array
      const user = this.results.find((person) => person.id === userId || person.employee_id === userId)
      if (user) {
        const nameParts = [user.first_name, user.last_name].filter(Boolean)
        if (nameParts.length) {
          return nameParts.join(' ')
        }
        return user.full_name || user.username || user.email || `User ${userId}`
      }
      return `User ${userId}`
    },
    async logout() {
      try {
        await axios.post(`${API_BASE_URL}/logout`, {}, { withCredentials: true })
      } catch (error) {
        console.error('Failed to logout', error)
        this.showToast('Unable to log out right now. Clearing local session.', 'error')
      } finally {
        try {
          localStorage.removeItem('currentUser')
          localStorage.removeItem('authToken')
          localStorage.removeItem('activeUserRole')
        } catch (storageError) {
          console.warn('Unable to clear cached session', storageError)
        }
        delete axios.defaults.headers.common[AUTH_HEADER]
        this.$router.push({ name: 'HomePage' })
      }
    },
  },
}
</script>
