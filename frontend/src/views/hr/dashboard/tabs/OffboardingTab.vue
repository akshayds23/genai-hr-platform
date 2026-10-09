<template>
  <section class="offboarding-shell min-h-screen p-6 lg:p-10 font-sans text-slate-900 space-y-6">
    
    <header class="offboarding-header mb-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
      <div>
        <div class="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-indigo-600 mb-2">
          <span class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-indigo-600"></span>
          </span>
          Exits & Transitions
        </div>
        <h2 class="text-3xl font-bold tracking-tight text-slate-900">Offboarding Journeys</h2>
        <p class="mt-1 text-slate-500">
          Manage outgoing employee pipelines, tasks, and documentation.
        </p>
      </div>
      
      <div class="flex items-center gap-4">
        <div class="hidden md:block text-right">
          <p class="text-2xl font-bold text-slate-900 leading-none">{{ activeCount }}</p>
          <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Active Exits</p>
        </div>
        <div class="h-10 w-px bg-slate-200 hidden md:block"></div>
        <button
          class="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-bold text-slate-700 shadow-sm ring-1 ring-slate-200 transition hover:bg-slate-50 hover:text-indigo-600"
          type="button"
          @click.stop="$emit('open-letters')"
        >
          <svg class="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
          <span>Manage Templates</span>
        </button>
      </div>
    </header>

    <div class="space-y-6">
      
      <div v-if="offboardingLoading" class="offboarding-card flex flex-col items-center justify-center py-20">
        <svg class="animate-spin h-10 w-10 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <p class="mt-4 font-medium text-slate-500">Syncing workflows...</p>
      </div>

      <div v-else-if="offboardingError" class="offboarding-card text-center text-rose-600">
         <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-100 mb-4">
           <svg class="h-6 w-6 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
         </div>
         <p class="font-bold text-rose-800">System Error</p>
         <p class="text-sm text-rose-600 mt-1">{{ offboardingError }}</p>
        <button @click="refreshOffboardingReport" class="mt-4 text-xs font-bold text-rose-700 underline">Try Again</button>
      </div>

      <div v-else-if="!offboardingReport.length" class="offboarding-card flex flex-col items-center justify-center py-24">
        <div class="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-slate-50 ring-1 ring-slate-100">
          <svg class="h-10 w-10 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
        <h3 class="mt-6 text-lg font-bold text-slate-900">All quiet on the front</h3>
        <p class="text-slate-500">There are no pending offboarding journeys at the moment.</p>
      </div>

      <div v-else class="grid gap-4 offboarding-list">
        <article 
          v-for="row in offboardingReport" 
          :key="row.user.id" 
          class="offboarding-card group relative"
        >
          <div class="flex flex-col gap-6 lg:flex-row lg:items-center">
            
            <div class="flex shrink-0 items-center gap-4 lg:w-72">
              <div 
                class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full text-base font-bold text-white shadow-sm ring-2 ring-white"
                :style="{ backgroundColor: getAvatarColor(row.user.id) }"
              >
                {{ getInitials(row.user) }}
              </div>
              <div class="min-w-0">
                <h3 class="truncate font-bold text-slate-900">{{ displayName(row.user) }}</h3>
                <p class="truncate text-xs text-slate-500">{{ row.user.email }}</p>
                <div class="mt-1 flex gap-2">
                   <span class="inline-flex items-center rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-600">ID: {{ row.user.employee_id || row.user.id }}</span>
                </div>
              </div>
            </div>

            <div class="flex-1 px-2 lg:px-6">
               <div class="mb-2 flex items-end justify-between">
                  <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Exit Pipeline</span>
                  <div class="text-right">
                     <span class="text-sm font-bold text-slate-900">{{ row.percent_complete }}%</span>
                     <span class="ml-1 text-xs text-slate-500">Complete</span>
                  </div>
               </div>
               
               <div class="relative">
                  <div class="absolute top-1/2 left-0 h-1.5 w-full -translate-y-1/2 rounded-full bg-slate-100"></div>
                  <div 
                    class="absolute top-1/2 left-0 h-1.5 -translate-y-1/2 rounded-full bg-indigo-500 transition-all duration-700 ease-out"
                    :style="{ width: row.percent_complete + '%' }"
                  ></div>

                  <div class="relative flex justify-between">
                     <div v-for="(step, index) in journeySteps" :key="step.label" class="group/step flex flex-col items-center">
                        <div 
                           class="relative z-10 h-3 w-3 rounded-full border-2 transition-all duration-300"
                           :class="getStepStatusClasses(index, row.percent_complete)"
                        ></div>
                        <span 
                           class="absolute top-5 text-[10px] font-bold uppercase tracking-tight transition-all"
                           :class="[
                             isStepActive(index, row.percent_complete) ? 'text-indigo-700 opacity-100' : 'text-slate-400 opacity-0 group-hover/step:opacity-100'
                           ]"
                        >
                           {{ step.label }}
                        </span>
                     </div>
                  </div>
               </div>
               <div class="mt-5 text-xs text-slate-400 lg:hidden">
                 {{ row.completed_tasks }} / {{ row.total_tasks }} Tasks Resolved
               </div>
            </div>

            <div class="flex shrink-0 items-center justify-end gap-3 lg:w-auto lg:border-l lg:border-slate-100 lg:pl-6">
              
               <div class="hidden lg:block text-right mr-4">
                  <span class="block text-sm font-bold text-slate-900">{{ row.completed_tasks }} / {{ row.total_tasks }}</span>
                  <span class="text-[10px] font-bold uppercase text-slate-400">Tasks</span>
               </div>

               <button 
                 @click="openTaskDrawer(row.user.id)"
                 class="group inline-flex items-center justify-center rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-bold text-slate-700 transition hover:border-indigo-300 hover:text-indigo-600 hover:shadow-sm"
               >
                 <span class="mr-2 h-2 w-2 rounded-full" :class="row.completed_tasks === row.total_tasks ? 'bg-emerald-500' : 'bg-amber-400'"></span>
                 Review
               </button>
               
               <button 
                 @click="openUnifiedLetterModal(row.user.id)"
                 class="inline-flex items-center justify-center rounded-lg bg-slate-900 px-4 py-2 text-sm font-bold text-white shadow-md shadow-slate-900/10 transition hover:bg-slate-800 hover:translate-y-px"
               >
                 Letter
               </button>
            </div>

          </div>
        </article>
      </div>
    </div>

    <div v-if="showTaskDrawer" class="relative z-[1100]" aria-labelledby="slide-over-title" role="dialog" aria-modal="true">
      <div class="fixed inset-0 bg-slate-900/30 backdrop-blur-sm transition-opacity" @click="closeTaskDrawer"></div>

      <div class="fixed inset-0 overflow-hidden">
        <div class="absolute inset-0 overflow-hidden">
          <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
            <div class="pointer-events-auto w-screen max-w-md transform transition-transform duration-500 ease-in-out sm:duration-700 bg-white shadow-xl">
              
              <div class="flex h-full flex-col divide-y divide-slate-200 bg-white shadow-xl">
                <div class="flex min-h-0 flex-1 flex-col overflow-y-scroll py-6">
                  <div class="px-4 sm:px-6">
                    <div class="flex items-start justify-between">
                      <div>
                        <h2 class="text-lg font-bold text-slate-900" id="slide-over-title">Offboarding Checklist</h2>
                        <p class="text-sm text-slate-500">{{ findUserName(selectedUserId) }}</p>
                      </div>
                      <div class="ml-3 flex h-7 items-center">
                        <button type="button" class="rounded-md bg-white text-slate-400 hover:text-slate-500 focus:outline-none" @click="closeTaskDrawer">
                          <span class="sr-only">Close panel</span>
                          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                        </button>
                      </div>
                    </div>
                  </div>

                  <div class="relative mt-6 flex-1 px-4 sm:px-6">
                    
                    <div v-if="tasksLoading" class="py-12 text-center">
                      <div class="animate-spin h-8 w-8 border-4 border-slate-200 border-t-indigo-600 rounded-full mx-auto mb-3"></div>
                      <p class="text-sm text-slate-500">Loading checklist...</p>
                    </div>

                    <div v-else class="space-y-6">
                      <div class="rounded-xl bg-slate-50 p-4 ring-1 ring-slate-100">
                         <div class="flex justify-between text-xs font-bold uppercase text-slate-500 mb-2">
                           <span>Completion</span>
                           <span>{{ Math.round((tasksList.filter(t => t.status === 'completed').length / (tasksList.length || 1)) * 100) }}%</span>
                         </div>
                         <div class="h-2 w-full rounded-full bg-slate-200 overflow-hidden">
                            <div class="h-full bg-indigo-500 transition-all duration-500" :style="{ width: (tasksList.filter(t => t.status === 'completed').length / (tasksList.length || 1) * 100) + '%' }"></div>
                         </div>
                      </div>

                      <ul class="space-y-3">
                        <li v-for="task in tasksList" :key="task.id" class="group relative rounded-xl border border-slate-200 bg-white p-4 transition hover:border-indigo-300">
                          <div class="flex items-start gap-3">
                            <div class="mt-0.5 shrink-0">
                               <div v-if="task.status === 'completed'" class="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
                                 <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" /></svg>
                               </div>
                               <div v-else class="h-5 w-5 rounded-full border-2 border-slate-300"></div>
                            </div>
                            
                            <div class="flex-1">
                              <p class="text-sm font-bold text-slate-900" :class="{'line-through text-slate-400': task.status === 'completed'}">{{ task.description }}</p>
                              <p class="text-xs text-slate-500 mt-1">Assignee: {{ task.assignee_role || 'HR Admin' }}</p>
                            </div>
                          </div>

                          <div class="mt-3 flex items-center justify-end gap-2 border-t border-slate-50 pt-3">
                             <button 
                               v-if="task.status !== 'completed'"
                               @click="updateTaskStatus(task.id, 'completed')"
                               :disabled="taskUpdateLoading[task.id]"
                               class="rounded px-2 py-1 text-xs font-bold text-indigo-600 hover:bg-indigo-50 disabled:opacity-50"
                             >
                               {{ taskUpdateLoading[task.id] ? 'Saving...' : 'Mark Complete' }}
                             </button>
                             <span
                               v-else
                               class="rounded px-2 py-1 text-xs font-bold text-emerald-600 bg-emerald-50 border border-emerald-100"
                             >
                               Completed
                             </span>
                          </div>
                        </li>
                      </ul>
                      
                      <div v-if="tasksList.length === 0" class="text-center py-8 text-slate-400 italic">
                        No tasks assigned.
                      </div>
                    </div>
                  </div>
                </div>

                <div class="flex flex-shrink-0 justify-between px-4 py-4 border-t border-slate-200 bg-slate-50">
                  <button type="button" class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-bold text-slate-700 shadow-sm hover:bg-slate-50" @click="closeTaskDrawer">Close</button>
                  <button type="button" class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-bold text-white shadow-sm hover:bg-indigo-700" @click="openUnifiedLetterModal(selectedUserId)">Generate Letter</button>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showUnifiedLetterModal" class="fixed inset-0 z-[1200] overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex min-h-screen items-center justify-center p-4 text-center sm:p-0">
        <div class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity" @click="closeUnifiedLetterModal"></div>

        <div class="relative transform overflow-hidden rounded-2xl bg-white text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-5xl border border-slate-200">
            
            <div class="grid grid-cols-1 lg:grid-cols-3 h-[80vh]">
               <div class="bg-slate-50 p-6 lg:border-r lg:border-slate-200 overflow-y-auto">
                  <h3 class="text-xl font-bold text-slate-900 mb-6">Letter Settings</h3>
                  
                  <div class="space-y-6">
                     <div>
                        <label class="block text-sm font-bold text-slate-700 mb-2">Select Template</label>
                        <select 
                           v-model="selectedTemplateId" 
                           class="w-full rounded-lg border-slate-300 text-sm shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                           :disabled="templatesLoading || generatingLetter"
                        >
                           <option v-for="t in templatesList" :key="t.id" :value="t.id">{{ t.name }}</option>
                        </select>
                        <p v-if="templateFetchError" class="mt-1 text-xs text-rose-500">{{ templateFetchError }}</p>
                     </div>

                     <div class="rounded-lg bg-blue-50 p-4 border border-blue-100">
                        <h4 class="text-sm font-bold text-blue-900">Variables</h4>
                        <p class="text-xs text-blue-700 mt-1">This template uses data from the employee profile (Name: {{ findUserName(selectedUserId) }}).</p>
                     </div>

                     <button 
                        @click="generateLetter"
                        :disabled="!selectedTemplateId || generatingLetter"
                        class="w-full flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                     >
                        <span v-if="generatingLetter" class="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white"></span>
                        {{ generatingLetter ? 'Generating...' : 'Generate Preview' }}
                     </button>
                  </div>

                  
               </div>

               <div class="col-span-2 bg-slate-300 p-6 lg:p-10 overflow-y-auto flex flex-col items-center">
                  <div class="w-full max-w-2xl bg-white shadow-xl min-h-[60vh] p-10 text-slate-800 text-sm leading-relaxed whitespace-pre-wrap rounded-sm relative">
                     <div v-if="!letterContent && !generatingLetter" class="absolute inset-0 flex items-center justify-center text-slate-400 italic">
                        Select a template and click generate to preview.
                     </div>
                     <div v-else-if="generatingLetter" class="absolute inset-0 flex items-center justify-center bg-white/80 z-10">
                        <div class="animate-pulse text-indigo-600 font-bold">Drafting document...</div>
                     </div>
                     {{ letterContent }}
                  </div>
               </div>
            </div>

            <div class="bg-white px-4 py-3 border-t border-slate-100 flex justify-between items-center sm:px-6">
               <span class="text-xs text-slate-500" v-if="generatedLetterId">Draft saved automatically.</span>
               <span v-else></span>
               
               <div class="flex gap-3">
                  <button type="button" class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50" @click="closeUnifiedLetterModal">Cancel</button>
                  <button 
                     type="button" 
                     :disabled="!letterContent"
                     class="rounded-lg bg-emerald-600 px-6 py-2 text-sm font-bold text-white shadow-sm hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed" 
                     @click="downloadCurrentLetter"
                  >
                     Download PDF
                  </button>
               </div>
            </div>

        </div>
      </div>
    </div>

  </section>
</template>

<script>
import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || '/api'

export default {
  name: 'HrDashboardOffboardingTab',
  inject: ['hrDashboardContext'], // Assuming global toast/notification context
  emits: ['open-letters'],
  data() {
    return {
      // Configuration
      journeySteps: [
        { label: 'Initiated' },
        { label: 'Logistics' },
        { label: 'Handover' },
        { label: 'Interview' },
        { label: 'Finalize' },
      ],
      
      // Task Drawer State
      showTaskDrawer: false,
      selectedUserId: null,
      tasksList: [],
      tasksLoading: false,
      taskUpdateLoading: {},
      
      // Unified Letter Modal State
      showUnifiedLetterModal: false,
      templatesList: [],
      lettersList: [],
      templatesLoading: false,
      lettersLoading: false,
      selectedTemplateId: null,
      letterContent: '',
      generatedLetterId: null,
      generatingLetter: false,
      templateFetchError: '',
    }
  },
  computed: {
    offboardingReport() {
      return this.hrDashboardContext?.offboardingReport || []
    },
    offboardingLoading() {
      return this.hrDashboardContext?.offboardingLoading || false
    },
    offboardingError() {
      return this.hrDashboardContext?.offboardingError || ''
    },
    activeCount() {
      return this.offboardingReport.length
    },
  },
  mounted() {
    this.refreshOffboardingReport()
  },
  methods: {
    // --- Visual Helpers ---
    getAvatarColor(id) {
       const colors = ['#f43f5e', '#8b5cf6', '#10b981', '#f59e0b', '#3b82f6', '#ec4899'];
       return colors[(id || 0) % colors.length];
    },
    displayName(user) {
       return user.first_name ? `${user.first_name} ${user.last_name || ''}` : (user.full_name || user.username || 'Employee');
    },
    getInitials(user) {
       return this.displayName(user).charAt(0).toUpperCase();
    },
    
    // --- Stepper Logic ---
    isStepActive(index, percent) {
      // Determines if the text label should be highlighted
      const stepThreshold = index * 20; 
      return percent >= stepThreshold;
    },
    getStepStatusClasses(index, percent) {
       const stepThreshold = index * 20;
       
       // Completed Step
       if (percent > stepThreshold + 10) { 
         return 'bg-indigo-500 border-indigo-500'
       }
       // Current Active Step
       if (percent >= stepThreshold) {
         return 'bg-white border-indigo-500 ring-4 ring-indigo-100'
       }
       // Future Step
       return 'bg-white border-slate-200'
    },
    
    findUserName(userId) {
      if (!userId) return '';
      const row = this.offboardingReport.find(r => r.user.id === userId);
      return row ? this.displayName(row.user) : 'Unknown User';
    },

    // --- API: Main Report ---
    async refreshOffboardingReport() {
      const loader = this.hrDashboardContext?.loadOffboardingReport
      if (typeof loader === 'function') {
        await loader()
      }
    },

    // --- Drawer Logic (Tasks) ---
    async openTaskDrawer(userId) {
      this.selectedUserId = userId;
      this.showTaskDrawer = true;
      this.tasksLoading = true;
      
      // Load tasks and report concurrently to ensure data freshness
      try {
        const [tasks] = await Promise.all([
          this._fetchTasksForUser(userId),
          // We silently refresh the report to keep the background updated
          this.refreshOffboardingReport()
        ]);
        this.tasksList = tasks;
      } catch (err) {
        this.hrDashboardContext?.showToast('Failed to load tasks', 'error');
      } finally {
        this.tasksLoading = false;
      }
    },
    
    closeTaskDrawer() {
      this.showTaskDrawer = false;
      this.selectedUserId = null;
      this.tasksList = [];
    },

    async _fetchTasksForUser(userId) {
      const res = await axios.get(`${API_BASE_URL}/offboarding/tasks`, { params: { user_id: userId }, withCredentials: true });
      return res.data?.tasks || [];
    },

    async updateTaskStatus(taskId, targetStatus) {
      this.taskUpdateLoading[taskId] = true;
      
      try {
        if (targetStatus !== 'completed') {
          return
        }

        const currentTask = this.tasksList.find((task) => task.id === taskId)
        if (currentTask && currentTask.status !== 'in_progress') {
          await axios.patch(`${API_BASE_URL}/offboarding/tasks/${taskId}`, { status: 'in_progress' }, {
            withCredentials: true,
            headers: { 'Content-Type': 'application/json' }
          })

          const pendingIndex = this.tasksList.findIndex((task) => task.id === taskId)
          if (pendingIndex !== -1) {
            this.tasksList[pendingIndex].status = 'in_progress'
          }
          await new Promise((resolve) => setTimeout(resolve, 120))
        }

        const payload = { status: 'completed' }
        await axios.patch(`${API_BASE_URL}/offboarding/tasks/${taskId}`, payload, { 
          withCredentials: true,
          headers: { 'Content-Type': 'application/json' }
        })

        const taskIndex = this.tasksList.findIndex(t => t.id === taskId)
        if (taskIndex !== -1) {
          this.tasksList[taskIndex].status = 'completed'
          
          this.hrDashboardContext?.showToast('Task completed successfully', 'success')
          await this.refreshOffboardingReport()
        }
        
      } catch (err) {
        const errorMsg = err.response?.data?.message || err.response?.data?.error || 'Failed to update task'
        this.hrDashboardContext?.showToast(`Failed to update task: ${errorMsg}`, 'error')
      } finally {
        delete this.taskUpdateLoading[taskId]
      }
    },

    // --- Unified Letter Logic ---
    async openUnifiedLetterModal(userId) {
      if (this.showTaskDrawer) this.closeTaskDrawer() // Close drawer if open
      this.selectedUserId = userId

      let tasks = [];
      try {
        tasks = await this._fetchTasksForUser(userId);
        this.tasksList = tasks;
      } catch (err) {
        this.hrDashboardContext?.showToast('Unable to verify task completion before generating the letter.', 'error');
        return;
      }

      const allTasksCompleted =
        Array.isArray(tasks) &&
        tasks.length &&
        tasks.every((task) => task.status === 'completed')

      if (!allTasksCompleted) {
        this.hrDashboardContext?.showToast(
          'Complete every offboarding task before generating the final letter.',
          'warning',
          4500,
        )
        return
      }

      this.showUnifiedLetterModal = true
      this.letterContent = ''
      this.generatedLetterId = null
      this.templatesLoading = true
      this.lettersLoading = true
      this.templateFetchError = ''

      try {
        const [tplRes, lettersRes] = await Promise.allSettled([
          axios.get(`${API_BASE_URL}/letters/templates`, { withCredentials: true }),
          axios.get(`${API_BASE_URL}/offboarding/letters`, { params: { user_id: userId }, withCredentials: true })
        ]);

        // Handle Templates
        if(tplRes.status === 'fulfilled') {
            this.templatesList = tplRes.value.data?.templates || [];
            if(this.templatesList.length > 0) this.selectedTemplateId = this.templatesList[0].id;
            else this.templateFetchError = 'No templates available.';
        } else {
            this.templateFetchError = 'Failed to load templates.';
        }

        // Handle History
        if(lettersRes.status === 'fulfilled') {
            this.lettersList = lettersRes.value.data?.letters || [];
        }

      } finally {
        this.templatesLoading = false;
        this.lettersLoading = false;
      }
    },

    closeUnifiedLetterModal() {
      this.showUnifiedLetterModal = false;
      this.selectedUserId = null;
      this.letterContent = '';
    },

    async generateLetter() {
      if (!this.selectedTemplateId || !this.selectedUserId) return

      const allTasksCompleted =
        Array.isArray(this.tasksList) &&
        this.tasksList.length &&
        this.tasksList.every((task) => task.status === 'completed')

      if (!allTasksCompleted) {
        this.hrDashboardContext?.showToast(
          'You can only generate the final letter after every task is completed.',
          'warning',
          4500,
        )
        return
      }
      
      this.generatingLetter = true;
      this.letterContent = ''; 
      
      try {
        const payload = { template_id: this.selectedTemplateId, user_id: this.selectedUserId };
        const res = await axios.post(`${API_BASE_URL}/letters/generate`, payload, { withCredentials: true });
        
        this.letterContent = res.data?.letter?.content || '';
        this.generatedLetterId = res.data?.letter?.id;
        
        // Refresh history list
        this.lettersLoading = true;
        const historyRes = await axios.get(`${API_BASE_URL}/offboarding/letters`, { params: { user_id: this.selectedUserId }, withCredentials: true });
        this.lettersList = historyRes.data?.letters || [];
        this.lettersLoading = false;

      } catch (err) {
        this.hrDashboardContext?.showToast('Generation failed: ' + (err.response?.data?.error || err.message), 'error');
      } finally {
        this.generatingLetter = false;
      }
    },
    
    async viewLetter(letterId) {
        this.generatingLetter = true;
        try {
            const res = await axios.get(`${API_BASE_URL}/offboarding/letters/${letterId}`, { withCredentials: true });
            this.letterContent = res.data?.content || '';
            this.generatedLetterId = letterId;
        } catch(err) {
            this.hrDashboardContext?.showToast('Could not fetch letter content', 'error');
        } finally {
            this.generatingLetter = false;
        }
    },

    async downloadCurrentLetter() {
        if(!this.generatedLetterId && !this.letterContent) return;

        // Visual feedback
        this.hrDashboardContext?.showToast('Downloading...', 'info');

        try {
            // Attempt server download if ID exists
            if (this.generatedLetterId) {
                const res = await axios.get(`${API_BASE_URL}/offboarding/letters/${this.generatedLetterId}/download`, { withCredentials: true, responseType: 'blob' });
                this.triggerBrowserDownload(res.data, `letter_${this.generatedLetterId}.txt`); // Assuming text/pdf
                return;
            } 
            
            // Fallback: Client side blob
            const blob = new Blob([this.letterContent], { type: 'text/plain' });
            this.triggerBrowserDownload(blob, `generated_letter_${Date.now()}.txt`);
            
        } catch(err) {
            console.error("Download failed", err);
            // Fallback if server download fails
            const blob = new Blob([this.letterContent], { type: 'text/plain' });
            this.triggerBrowserDownload(blob, 'fallback_letter.txt');
        }
    },

    triggerBrowserDownload(blobData, fileName) {
        const url = window.URL.createObjectURL(blobData);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 100);
    }
  }
}
</script>

<style scoped>
.offboarding-shell {
  background: #f5faf5;
  border-radius: 2rem;
  border: 1px solid rgba(73, 133, 40, 0.25);
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.08);
}
.offboarding-card {
  border-radius: 1.5rem;
  border: 1px solid rgba(73, 133, 40, 0.25);
  background: #ffffff;
  padding: 1.5rem;
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
}
.offboarding-header {
  border-bottom: 1px solid rgba(73, 133, 40, 0.2);
  padding-bottom: 1rem;
}
.offboarding-list {
  padding-bottom: 1rem;
}
.offboarding-card:nth-child(odd) {
  background: #ffffff;
}
.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s ease;
}
.slide-enter, .slide-leave-to {
  transform: translateX(100%);
}
</style>
