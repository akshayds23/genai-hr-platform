<template>
<section class="jd-shell p-6 lg:p-10 max-w-7xl mx-auto h-full flex flex-col space-y-6">
    
    <header class="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div>
        <div class="flex items-center gap-2 mb-2">
          <span class="relative flex h-2.5 w-2.5">
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-violet-500"></span>
          </span>
          <span class="text-xs font-bold uppercase tracking-widest text-violet-600">AI Recruiter</span>
        </div>
        <h2 class="text-3xl font-bold tracking-tight text-slate-900">JD Maker Studio</h2>
        <p class="text-slate-500 mt-2 text-sm leading-relaxed max-w-2xl">
          Generate comprehensive job descriptions instantly using AI and manage your role library.
        </p>
      </div>
    </header>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
      
      <div class="xl:col-span-1">
        <div class="jd-panel sticky top-6">
          <div class="flex items-center gap-3 mb-6 border-b border-slate-50 pb-4">
            <div class="p-2 bg-violet-50 text-violet-600 rounded-lg">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            </div>
            <div>
              <h3 class="font-bold text-slate-900">New Role</h3>
              <p class="text-xs text-slate-500">Enter details to generate JD</p>
            </div>
          </div>

          <form @submit.prevent="generateJD" class="space-y-4">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Job Title <span class="text-rose-500">*</span></label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                </div>
                <input
                  v-model.trim="form.title"
                  class="w-full pl-10 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500 transition font-medium text-slate-900"
                  type="text"
                  placeholder="e.g. Senior Product Designer"
                  required
                />
              </div>
            </div>

            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Department</label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                   <svg class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
                </div>
                <input
                  v-model.trim="form.department"
                  class="w-full pl-10 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500 transition"
                  type="text"
                  placeholder="e.g. Engineering"
                />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Exp. (Yrs)</label>
                <div class="relative">
                  <input
                    v-model.number="form.experience_required"
                    class="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500 transition"
                    type="number"
                    placeholder="e.g. 3"
                    min="0"
                    step="0.5"
                  />
                </div>
              </div>
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Salary Range</label>
                <div class="relative">
                   <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                     <span class="text-slate-400 font-bold">₹ </span>
                   </div>
                  <input
                    v-model.trim="form.salary_range"
                    class="w-full pl-7 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500 transition"
                    type="text"
                    placeholder="100k-120k"
                  />
                </div>
              </div>
            </div>

            <div v-if="generatingError" class="flex items-center gap-2 text-xs text-rose-600 bg-rose-50 border border-rose-100 rounded-lg p-3">
               <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
               {{ generatingError }}
            </div>
            <div v-if="generatingSuccess" class="flex items-center gap-2 text-xs text-emerald-600 bg-emerald-50 border border-emerald-100 rounded-lg p-3">
               <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
               {{ generatingSuccess }}
            </div>

            <button
              class="w-full group relative overflow-hidden rounded-xl bg-slate-900 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-slate-900/20 transition hover:bg-slate-800 hover:shadow-xl disabled:opacity-70 disabled:cursor-not-allowed mt-2"
              type="submit"
              :disabled="generating"
            >
              <span v-if="!generating" class="flex items-center justify-center gap-2">
                <svg class="w-4 h-4 text-violet-400 group-hover:text-violet-300 transition" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
                Generate with AI
              </span>
              <span v-else class="flex items-center justify-center gap-2">
                <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                Drafting Content...
              </span>
            </button>
          </form>
        </div>
      </div>

      <div class="xl:col-span-2">
        <div class="jd-panel overflow-hidden flex flex-col h-full min-h-[400px]">
          <div class="px-6 py-5 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
            <h3 class="font-bold text-slate-800">Job Library</h3>
            <span class="text-xs font-semibold text-slate-500 bg-white border border-slate-200 px-2 py-1 rounded-md">{{ jobDescriptions.length }} Roles</span>
          </div>

          <div v-if="loading" class="flex-1 flex flex-col items-center justify-center p-12">
             <div class="animate-spin w-8 h-8 border-4 border-slate-100 border-t-violet-600 rounded-full mb-4"></div>
             <p class="text-xs font-bold uppercase tracking-wide text-slate-400">Loading Library...</p>
          </div>

          <div v-else-if="!jobDescriptions.length" class="flex-1 flex flex-col items-center justify-center p-12 text-center">
            <div class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4 ring-8 ring-slate-50/50">
              <span class="text-2xl">📋</span>
            </div>
            <p class="text-lg font-bold text-slate-900">No Jobs Created</p>
            <p class="text-sm text-slate-500 mt-1 max-w-xs mx-auto">Use the form on the left to generate your first job description.</p>
          </div>

          <div v-else class="overflow-x-auto">
            <table class="min-w-full text-left">
              <thead class="bg-white border-b border-slate-100 text-slate-500 text-[10px] uppercase tracking-wider">
                <tr>
                  <th class="px-6 py-3 font-bold">Role Details</th>
                  <th class="px-6 py-3 font-bold">Requirements</th>
                  <th class="px-6 py-3 font-bold">Created</th>
                  <th class="px-6 py-3 font-bold text-right">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 text-sm">
                <tr v-for="jd in jobDescriptions" :key="jd.id" class="hover:bg-slate-50/50 transition-colors group">
                  <td class="px-6 py-4">
                    <div class="font-bold text-slate-900">{{ jd.title }}</div>
                    <div class="text-xs text-slate-500 mt-0.5">{{ jd.department || 'General' }}</div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex flex-wrap gap-2">
                      <span v-if="jd.experience_required" class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-blue-50 text-blue-700 border border-blue-100">
                        {{ jd.experience_required }} Yrs
                      </span>
                      <span v-if="jd.salary_range" class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-100">
                        {{ jd.salary_range }}
                      </span>
                      <span v-if="!jd.experience_required && !jd.salary_range" class="text-slate-400 text-xs">-</span>
                    </div>
                  </td>
                  <td class="px-6 py-4 text-xs text-slate-500">
                    {{ formatDate(jd.uploaded_at) }}
                  </td>
                  <td class="px-6 py-4 text-right">
                    <div class="flex items-center justify-end gap-2">
                      <button
                        @click="viewJD(jd)"
                        class="p-2 text-slate-400 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition"
                        title="View Details"
                      >
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                      </button>
                      <button
                        @click="downloadJD(jd)"
                        :disabled="downloadingId === jd.id"
                        class="p-2 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition disabled:opacity-50"
                        title="Download PDF"
                      >
                         <svg v-if="downloadingId !== jd.id" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                         <svg v-else class="animate-spin w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <transition
      enter-active-class="transform transition ease-in-out duration-300 sm:duration-500"
      enter-from-class="translate-x-full"
      enter-to-class="translate-x-0"
      leave-active-class="transform transition ease-in-out duration-300 sm:duration-500"
      leave-from-class="translate-x-0"
      leave-to-class="translate-x-full"
    >
      <div v-if="showViewModal" class="fixed inset-0 z-[100] overflow-hidden" aria-labelledby="slide-over-title" role="dialog" aria-modal="true">
        <div class="absolute inset-0 overflow-hidden">
          <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" @click="closeViewModal"></div>

          <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
            <div class="pointer-events-auto w-screen max-w-xl">
              <div class="flex h-full flex-col overflow-y-scroll bg-white shadow-2xl">
                
                <div class="px-6 py-6 border-b border-slate-100 bg-slate-50/50">
                  <div class="flex items-start justify-between">
                    <div>
                      <h2 class="text-xl font-bold text-slate-900 leading-6" id="slide-over-title">{{ selectedJD?.title }}</h2>
                      <p class="text-sm text-slate-500 mt-1">{{ selectedJD?.department || 'General Department' }}</p>
                    </div>
                    <div class="ml-3 flex h-7 items-center">
                      <button @click="closeViewModal" type="button" class="rounded-md bg-transparent text-slate-400 hover:text-slate-500 focus:outline-none">
                        <span class="sr-only">Close panel</span>
                        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                      </button>
                    </div>
                  </div>
                </div>

                <div class="relative flex-1 px-6 py-6 space-y-8">
                  
                  <div class="grid grid-cols-2 gap-4 p-4 bg-slate-50 rounded-xl border border-slate-100">
                    <div>
                      <p class="text-[10px] font-bold uppercase text-slate-400 tracking-wider">Experience</p>
                      <p class="text-sm font-semibold text-slate-900 mt-0.5">{{ selectedJD?.experience_required || 'Not specified' }} Years</p>
                    </div>
                    <div>
                      <p class="text-[10px] font-bold uppercase text-slate-400 tracking-wider">Salary</p>
                      <p class="text-sm font-semibold text-slate-900 mt-0.5">{{ selectedJD?.salary_range || 'Not specified' }}</p>
                    </div>
                    <div>
                      <p class="text-[10px] font-bold uppercase text-slate-400 tracking-wider">Created</p>
                      <p class="text-sm font-semibold text-slate-900 mt-0.5">{{ formatDate(selectedJD?.uploaded_at) }}</p>
                    </div>
                  </div>

                  <div>
                    <h3 class="text-sm font-bold text-slate-900 uppercase tracking-wide border-b border-slate-100 pb-2 mb-3">Job Description</h3>
                    <div class="text-sm text-slate-600 leading-relaxed space-y-2 text-left" v-html="renderMarkdown(selectedJD?.description)"></div>
                  </div>

                  <div v-if="selectedJD?.requirements">
                    <h3 class="text-sm font-bold text-slate-900 uppercase tracking-wide border-b border-slate-100 pb-2 mb-3">Requirements</h3>
                    <ul class="space-y-2 text-left">
                      <li v-for="(req, index) in parseRequirements(selectedJD.requirements)" :key="index" class="flex items-start gap-2 text-sm text-slate-600 leading-relaxed">
                         <span class="mt-1.5 h-1.5 w-1.5 rounded-full bg-violet-500 shrink-0"></span>
                         <span>{{ req }}</span>
                      </li>
                    </ul>
                  </div>
                  
                  <div v-if="selectedJD?.skills_required">
                    <h3 class="text-sm font-bold text-slate-900 uppercase tracking-wide border-b border-slate-100 pb-2 mb-3">Key Skills</h3>
                    <div class="flex flex-wrap gap-2 text-left">
                       <span v-for="(skill, idx) in parseSkills(selectedJD.skills_required)" :key="idx" class="px-2.5 py-1 bg-white border border-slate-200 rounded-md text-xs font-medium text-slate-600 shadow-sm">
                         {{ skill.trim() }}
                       </span>
                    </div>
                  </div>

                </div>

                <div class="flex flex-shrink-0 justify-end px-6 py-4 border-t border-slate-100 bg-slate-50">
                  <button
                    @click="closeViewModal"
                    class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-bold text-slate-700 shadow-sm hover:bg-slate-50 mr-3"
                  >
                    Close
                  </button>
                  <button
                    @click="downloadJD(selectedJD)"
                    :disabled="downloadingId === selectedJD?.id"
                    class="inline-flex justify-center items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-bold text-white shadow-sm hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-70"
                  >
                    <svg v-if="downloadingId === selectedJD?.id" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    {{ downloadingId === selectedJD?.id ? 'Downloading...' : 'Download PDF' }}
                  </button>
                </div>

              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

  </section>
</template>

<script>
import { ref, onMounted } from 'vue'
import apiClient from '@/api'

export default {
  name: 'JdMakerTab',
  inject: ['hrDashboardContext'],
  setup() {
    const form = ref({
      title: '',
      experience_required: null,
      salary_range: '',
      department: ''
    })

    const generating = ref(false)
    const loading = ref(false)
    const generatingError = ref('')
    const generatingSuccess = ref('')
    const jobDescriptions = ref([])
    const showViewModal = ref(false)
    const selectedJD = ref(null)
    const downloadingId = ref(null)
    const authToken = localStorage.getItem('authToken') || localStorage.getItem('token')

    // Debug function to check user auth status
    const checkUserAuth = async () => {
      try {
        const response = await apiClient.get('/me')
        return response.data.user
      } catch (error) {
        console.error('Failed to get user info:', error)
        return null
      }
    }

    // --- HELPER 1: Safe Skills Parser ---
    const parseSkills = (skills) => {
      if (!skills) return []
      if (Array.isArray(skills)) return skills
      if (typeof skills === 'string') {
        const clean = skills.replace(/[[\]"]/g, '')
        return clean.split(',').map(s => s.trim()).filter(s => s)
      }
      return []
    }

    // --- HELPER 2: Requirements JSON Parser ---
    const parseRequirements = (reqs) => {
      if (!reqs) return []
      if (Array.isArray(reqs)) return reqs
      if (typeof reqs === 'string') {
        reqs = reqs.trim()
        if (reqs.startsWith('[') && reqs.endsWith(']')) {
          try {
            return JSON.parse(reqs)
          } catch (e) {
            console.warn('Failed to parse requirements JSON', e)
          }
        }
        if (reqs.includes(',')) return reqs.split(',').map(s => s.trim())
        return [reqs]
      }
      return []
    }

    // --- HELPER 3: Markdown Renderer ---
    const renderMarkdown = (text) => {
      if (!text) return ''
      let html = text
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
        .replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-900">$1</strong>')
        .replace(/^\s*\*\s+(.*)$/gm, '<li class="ml-4 list-outside list-disc">$1</li>')
        .replace(/\n/g, '<br>')
      return html
    }

    const fetchJobDescriptions = async () => {
      loading.value = true
      try {
        const response = await apiClient.get('/hr/jd')
        jobDescriptions.value = response.data.job_descriptions || []
      } catch (error) {
        console.error('Error fetching job descriptions:', error)
        
        if (error.response) {
          const status = error.response.status
          if (status === 403) {
            console.warn('Access denied: User may not have super_admin role')
            generatingError.value = 'Access denied: Insufficient permissions to view job descriptions'
          } else if (status === 401) {
            console.warn('Authentication failed: Token may be invalid')
            generatingError.value = 'Authentication failed: Please login again'
          } else {
            console.error('HTTP error:', status, error.response.data)
            generatingError.value = 'Unable to load job descriptions: Server error'
          }
        } else {
          console.error('Network or other error:', error.message)
          generatingError.value = 'Unable to connect to server'
        }
        
        jobDescriptions.value = []
        setTimeout(() => { generatingError.value = '' }, 5000)
      } finally {
        loading.value = false
      }
    }

    const generateJD = async () => {
      if (!form.value.title.trim()) {
        generatingError.value = 'Job title is required'
        return
      }

      generatingError.value = ''
      generatingSuccess.value = ''
      generating.value = true

      try {
        const payload = {
          title: form.value.title,
          department: form.value.department || '',
          experience_level: form.value.experience_required ? `${form.value.experience_required}+ years` : '',
          salary_range: form.value.salary_range || '',
          employment_type: 'Full-time',
          location: 'Remote',
          company_info: '',
          key_skills: [],
          responsibilities: '',
          qualifications: '',
          additional_notes: ''
        }

        const generateResponse = await apiClient.post('/genai/jd/generate', payload)
        const generatedDescription = generateResponse.data.description

        const savePayload = {
          title: form.value.title,
          department: form.value.department,
          description: generatedDescription,
          experience_required: form.value.experience_required,
          salary_range: form.value.salary_range,
          requirements: generateResponse.data.requirements,
          skills_required: generateResponse.data.skills_required
        }

        await apiClient.post('/genai/jd/save', savePayload)

        generatingSuccess.value = 'Success! Job description generated and saved.'
        
        form.value = {
          title: '',
          experience_required: null,
          salary_range: '',
          department: ''
        }

        await fetchJobDescriptions()
        
        setTimeout(() => { generatingSuccess.value = '' }, 4000)
      } catch (error) {
        console.error('JD generation failed:', error)
        
        let errorMsg = 'Failed to generate job description'
        if (error.response) {
          const status = error.response.status
          if (status === 403) {
            errorMsg = 'Access denied: You do not have permission to generate job descriptions'
          } else if (status === 401) {
            errorMsg = 'Authentication failed: Please login again'
          } else if (error.response.data?.error) {
            errorMsg = error.response.data.error
          } else {
            errorMsg = `Server error (${status}): Unable to generate job description`
          }
        } else if (error.message) {
          errorMsg = error.message
        }
        
        generatingError.value = errorMsg
      } finally {
        generating.value = false
      }
    }

    const viewJD = (jd) => {
      selectedJD.value = jd
      showViewModal.value = true
    }

    const closeViewModal = () => {
      showViewModal.value = false
      setTimeout(() => { selectedJD.value = null }, 300)
    }

    // --- ENHANCED DOWNLOAD FUNCTION WITH PROPER ERROR HANDLING ---
    const downloadJD = async (jd) => {
      downloadingId.value = jd.id
      
      try {
        // 1. Validate required data
        if (!jd.title || !jd.description) {
          throw new Error('Incomplete job description data - missing title or description')
        }

        // 2. Prepare payload for PDF generation
        const payload = {
          title: jd.title,
          description: jd.description,
          requirements: jd.requirements || [],
          skills_required: jd.skills_required || [],
          department: jd.department || '',
          salary_range: jd.salary_range || '',
          experience_required: jd.experience_required || null
        }


        // 3. Make API call with proper error handling
        let response
        try {
          response = await apiClient.post('/genai/jd/pdf', payload, { 
            responseType: 'blob',
            timeout: 30000 // 30 second timeout
          })
        } catch (firstError) {
          // If the full payload fails, try with minimal required data
          const minimalPayload = {
            title: jd.title,
            description: jd.description
          }
          response = await apiClient.post('/genai/jd/pdf', minimalPayload, { 
            responseType: 'blob',
            timeout: 30000
          })
        }

        // 4. Verify response is valid
        if (!response.data || response.data.size === 0) {
          throw new Error('Empty response received from server')
        }

        // 5. Check if response is actually a PDF (and not an error JSON)
        const contentType = response.headers['content-type']
        if (contentType && !contentType.includes('application/pdf')) {
          // Response might be JSON error disguised as blob
          const text = await response.data.text()
          let errorMsg = 'Invalid PDF response from server'
          try {
            const jsonError = JSON.parse(text)
            errorMsg = jsonError.error || errorMsg
          } catch {
            // Not JSON, use default error
          }
          throw new Error(errorMsg)
        }

        // 6. Successfully download PDF
        const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${jd.title.replace(/[^a-zA-Z0-9_-]/g, '_')}.pdf`)
        document.body.appendChild(link)
        link.click()
        link.parentNode.removeChild(link)
        window.URL.revokeObjectURL(url)
        
      
      } catch (error) {
        console.error('PDF download failed:', error)
        
        // 7. Determine error type and show appropriate message
        let errorMessage = 'PDF download failed'
        let shouldFallback = true
        
        if (error.response) {
          const status = error.response.status
          console.error('HTTP Status:', status, 'Response:', error.response.data)
          
          if (status === 403) {
            errorMessage = 'Access denied: You do not have permission to download PDFs'
            shouldFallback = false
          } else if (status === 401) {
            errorMessage = 'Authentication required: Please login again'
            shouldFallback = false
          } else if (status === 500) {
            errorMessage = 'Server error: PDF generation service is temporarily unavailable'
          } else if (status === 404) {
            errorMessage = 'PDF service not found: Feature may not be available'
            shouldFallback = false
          } else {
            try {
              const errorData = error.response.data
              if (errorData && typeof errorData === 'object' && errorData.error) {
                errorMessage = `Server error: ${errorData.error}`
              }
            } catch {
              errorMessage = `HTTP ${status}: Unable to generate PDF`
            }
          }
        } else if (error.code === 'ECONNABORTED') {
          errorMessage = 'Request timeout: PDF generation took too long'
        } else if (error.message) {
          errorMessage = error.message
        }

        // 8. Show error and decide on fallback
        if (shouldFallback) {
          const userConfirmed = confirm(`${errorMessage}\n\nWould you like to download a text version instead?`)
          
          if (userConfirmed) {
            // Generate fallback text file
            const reqList = parseRequirements(jd.requirements).map(r => `• ${r}`).join('\n')
            const skillList = parseSkills(jd.skills_required).join(', ')

            const textContent = `
JOB DESCRIPTION
================================================
Title:       ${jd.title}
Department:  ${jd.department || 'Not specified'}
Experience:  ${jd.experience_required || 'Not specified'} Years
Salary:      ${jd.salary_range || 'Not specified'}
Created:     ${formatDate(jd.uploaded_at)}
================================================

DESCRIPTION:
${jd.description.replace(/<br\s*\/?>/g, '\n').replace(/\*\*(.*?)\*\*/g, '$1').replace(/<li[^>]*>/g, '• ').replace(/<\/li>/g, '').replace(/<[^>]*>/g, '')}

================================================
REQUIREMENTS:
${reqList || '• No specific requirements listed'}

================================================
KEY SKILLS:
${skillList || 'No specific skills listed'}

================================================
Generated by JD Maker Studio
Downloaded: ${new Date().toLocaleString()}
            `.trim()

            const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' })
            const url = window.URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `${jd.title.replace(/[^a-zA-Z0-9_-]/g, '_')}_JobDescription.txt`)
            document.body.appendChild(link)
            link.click()
            link.parentNode.removeChild(link)
            window.URL.revokeObjectURL(url)
            
          }
        } else {
          alert(errorMessage)
        }

      } finally {
        downloadingId.value = null
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      try { return new Date(dateString).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) } 
      catch { return dateString }
    }

    onMounted(async () => {
      // Debug: Check authentication status
      
      if (authToken) {
        const userInfo = await checkUserAuth()
        if (userInfo) {
          
          if (!userInfo.roles?.includes('hr')) {
            console.warn('User does NOT have hr role - JD functions may not work')
            generatingError.value = 'Warning: Your account may not have sufficient permissions for all JD Maker features'
            setTimeout(() => { generatingError.value = '' }, 8000)
          }
        }
      } else {
        console.warn('No authentication token found')
        generatingError.value = 'Authentication token missing - please login again'
      }
      
      fetchJobDescriptions()
    })

    return {
      form,
      generating,
      loading,
      generatingError,
      generatingSuccess,
      jobDescriptions,
      showViewModal,
      selectedJD,
      generateJD,
      viewJD,
      closeViewModal,
      downloadJD,
      downloadingId,
      formatDate,
      parseSkills,
      parseRequirements,
      renderMarkdown,
      checkUserAuth
    }
  }
}
</script>

<style scoped>
.jd-shell {
  background: #f6faf6;
}
.jd-panel {
  background: #ffffff;
  border-radius: 1.75rem;
  border: 1px solid rgba(73, 133, 40, 0.3);
  padding: 1.5rem;
  box-shadow: 0 25px 45px rgba(15, 23, 42, 0.08);
}
.jd-panel + .jd-panel {
  margin-top: 1.5rem;
}
.jd-panel h3 {
  color: #0f172a;
}
.jd-panel form label {
  color: #1f4c1c;
}
</style>
