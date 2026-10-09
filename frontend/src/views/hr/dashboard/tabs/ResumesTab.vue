<template>
  <section class="resumes-shell space-y-6 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
      <article class="resumes-hero space-y-6">
        <header class="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-slate-100 pb-8">
          <div>
            <div class="flex items-center gap-2 mb-2">
              <span class="relative flex h-2.5 w-2.5">
                <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-indigo-500"></span>
              </span>
              <span class="text-xs font-bold uppercase tracking-widest text-indigo-600">Talent Pipeline</span>
            </div>
            <h2 class="text-3xl font-bold tracking-tight text-slate-900">Resume Database</h2>
            <p class="text-slate-500 mt-2 text-sm leading-relaxed max-w-2xl">
              Centralized repository for candidate profiles, parsing status, and AI-driven role matching.
            </p>
          </div>

          <div class="flex gap-4">
            <div class="hidden md:flex flex-col items-end">
              <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Candidates</span>
              <span class="text-2xl font-black text-slate-900 leading-none">{{ ctx.resumesTotal || 0 }}</span>
            </div>
          </div>
        </header>
      </article>

      <article class="resumes-panel space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-0">
          <div class="resumes-subpanel h-full">
            <div class="p-5 border-b border-slate-50">
              <div class="flex items-center gap-3 mb-1">
                <div class="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                </div>
                <h3 class="font-bold text-slate-900">Bulk Ingestion</h3>
              </div>
              <p class="text-xs text-slate-500 ml-12">Import PDF, DOCX, or TXT files to parse.</p>
            </div>

            <form class="p-6 flex-1 flex flex-col gap-5" @submit.prevent>
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Select Files</label>
                <input
                  :key="ctx.bulkInputKey"
                  type="file"
                  accept=".pdf,.doc,.docx,.txt"
                  multiple
                  @change="ctx.handleBulkFiles"
                  class="block w-full text-sm text-slate-500
                    file:mr-4 file:py-2.5 file:px-4
                    file:rounded-lg file:border-0
                    file:text-sm file:font-bold
                    file:bg-emerald-50 file:text-emerald-700
                    hover:file:bg-emerald-100
                    cursor-pointer border border-slate-200 rounded-xl bg-white
                  "
                />
                <p class="mt-2 text-[10px] text-slate-400">Supported formats: .pdf, .docx, .txt</p>
              </div>

              <div class="grid grid-cols-3 gap-3">
                <div class="col-span-2">
                  <input
                    v-model="ctx.resumeUploadSource"
                    class="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition"
                    type="text"
                    placeholder="Source (e.g., LinkedIn)"
                  />
                </div>
                <button
                  class="col-span-1 w-full bg-blue-600 text-white font-semibold px-4 py-2 rounded-xl hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
                  type="button"
                  :disabled="ctx.bulkUploading"
                  @click.prevent="ctx.triggerBulkUpload"
                >
                  {{ ctx.bulkUploading ? '...' : 'Upload' }}
                </button>
              </div>

              <p v-if="ctx.bulkUploadError" class="text-xs font-medium text-rose-600 bg-rose-50 p-2 rounded">{{ ctx.bulkUploadError }}</p>

              <div v-if="ctx.bulkUploadProgress.show" class="mt-auto pt-4 border-t border-slate-50">
                <div class="flex justify-between text-xs font-bold text-slate-600 mb-2">
                  <span>Processing...</span>
                  <span>{{ ctx.bulkUploadProgress.percentage }}%</span>
                </div>
                <div class="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden mb-2">
                  <div class="h-full bg-emerald-500 transition-all duration-300" :style="{ width: ctx.bulkUploadProgress.percentage + '%' }"></div>
                </div>
                <div class="flex gap-3 text-[10px] uppercase font-bold text-slate-400">
                  <span>Done: {{ ctx.bulkUploadProgress.processed }}/{{ ctx.bulkUploadProgress.total }}</span>
                  <span class="text-emerald-600">+ {{ ctx.bulkUploadProgress.successful }}</span>
                  <span class="text-rose-500">- {{ ctx.bulkUploadProgress.failed }}</span>
                </div>
              </div>
            </form>
          </div>

          <div class="resumes-subpanel h-full">
            <div class="p-5 border-b border-slate-50">
              <div class="flex items-center gap-3 mb-1">
                <div class="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                </div>
                <h3 class="font-bold text-slate-900">AI Role Match</h3>
              </div>
              <p class="text-xs text-slate-500 ml-12">Score candidates against specific JDs.</p>
            </div>

            <div class="p-6 flex-1 flex flex-col gap-5">
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Target Job Description</label>
                <select
                  v-model.number="ctx.selectedJobDescriptionId"
                  class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 text-sm outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition"
                >
                  <option value="">Select a role to match...</option>
                  <option v-for="jd in ctx.jobDescriptions" :key="jd.id" :value="jd.id">
                    {{ jd.title }}{{ jd.department ? ' (' + jd.department + ')' : '' }}
                  </option>
                </select>
              </div>

              <div class="flex items-end gap-3">
                <div class="w-1/3">
                  <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Limit Results</label>
                  <input
                    v-model.number="ctx.matchTopN"
                    class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 text-sm text-center font-semibold outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition"
                    type="number"
                    min="1"
                    max="50"
                  />
                </div>
                <button
                  class="col-span-1 w-full bg-blue-600 text-white font-semibold px-4 py-2 rounded-xl hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
                  type="button"
                  :disabled="ctx.matching || !ctx.jobDescriptions.length"
                  @click="ctx.runMatching"
                >
                  <span v-if="ctx.matching" class="flex items-center justify-center gap-2">
                    <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    Analyzing...
                  </span>
                  <span v-else>Run Match Analysis</span>
                </button>
              </div>

              <p v-if="!ctx.jobDescriptions.length" class="text-xs text-slate-400 text-center bg-slate-50 rounded p-2">
                No JDs found. Create one in the JD Maker tab first.
              </p>
              <p v-if="ctx.matchError" class="text-xs text-rose-600 font-medium">{{ ctx.matchError }}</p>
            </div>
          </div>
        </div>
      </article>

      <article class="resumes-panel space-y-6">
        <transition enter-active-class="transition ease-out duration-300" enter-from-class="opacity-0 translate-y-4" enter-to-class="opacity-100 translate-y-0" leave-active-class="transition ease-in duration-200" leave-from-class="opacity-100" leave-to-class="opacity-0">
          <div v-if="ctx.matchResults.length" class="mb-10 rounded-2xl border border-indigo-100 bg-white shadow-xl shadow-indigo-100/50 overflow-hidden">
            <div class="px-6 py-4 bg-gradient-to-r from-indigo-50 to-white border-b border-indigo-100 flex justify-between items-center">
              <div>
                <h3 class="text-lg font-bold text-indigo-900">Analysis Results</h3>
                <p class="text-xs text-indigo-600/80 font-medium">Target: {{ ctx.matchedJob?.title }}</p>
              </div>
              <button @click="ctx.clearMatchResults" class="text-xs font-bold text-indigo-400 hover:text-indigo-600">Close Results</button>
            </div>

            <div class="overflow-x-auto">
              <table class="min-w-full text-left">
                <thead class="bg-indigo-50/50 text-indigo-900/60 text-[10px] uppercase tracking-wider">
                  <tr>
                    <th class="px-6 py-3 font-bold">Candidate</th>
                    <th class="px-6 py-3 font-bold">Current Role</th>
                    <th class="px-6 py-3 font-bold">Match Score</th>
                    <th class="px-6 py-3 font-bold">AI Reasoning</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-indigo-50 text-sm">
                  <tr v-for="item in ctx.matchResults" :key="item.candidate.id" class="hover:bg-indigo-50/30 transition-colors">
                    <td class="px-6 py-4">
                      <div class="font-bold text-slate-900">{{ item.candidate.full_name || item.candidate.name }}</div>
                      <div class="text-xs text-slate-500">{{ item.candidate.email }}</div>
                    </td>
                    <td class="px-6 py-4 text-slate-600">{{ item.candidate.current_role || 'Not specified' }}</td>
                    <td class="px-6 py-4">
                      <div class="flex items-center gap-2">
                        <div class="w-12 bg-slate-200 rounded-full h-1.5 overflow-hidden">
                          <div class="bg-indigo-500 h-full" :style="{ width: Math.min(item.match_score * 10, 100) + '%' }"></div>
                        </div>
                        <span class="font-bold text-indigo-700">{{ ctx.formatMatchScore(item.match_score) }}</span>
                      </div>
                    </td>
                    <td class="px-6 py-4 text-slate-500 text-xs leading-relaxed max-w-md">{{ ctx.formatReasoning(item.reasoning) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </transition>
      </article>

      <article class="resumes-panel space-y-0 resumes-table-panel">
        <div class="resumes-table-shell">
          <div class="px-6 py-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
            <h3 class="font-bold text-slate-800">All Profiles</h3>
            <div class="relative">
              <input type="text" placeholder="Search resumes..." class="pl-8 pr-3 py-1.5 text-xs rounded-lg border border-slate-200 bg-white focus:outline-none focus:border-indigo-300 w-48 transition" />
              <svg class="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
            </div>
          </div>

          <div v-if="ctx.resumesLoading" class="p-20 text-center">
            <div class="animate-spin w-8 h-8 border-4 border-slate-100 border-t-slate-600 rounded-full mx-auto mb-4"></div>
            <p class="text-xs font-bold uppercase tracking-wide text-slate-400">Fetching Database...</p>
          </div>

          <div v-else-if="!ctx.resumesList.length" class="p-20 text-center">
            <div class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4 ring-8 ring-slate-50/50">
              <svg class="w-8 h-8 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            </div>
            <p class="font-bold text-slate-900">Database Empty</p>
            <p class="text-sm text-slate-500 mt-1">Upload resumes above to populate the list.</p>
          </div>

          <div v-else class="overflow-x-auto">
            <table class="min-w-full text-left">
              <thead class="bg-white border-b border-slate-100 text-slate-500 text-[10px] uppercase tracking-wider">
                <tr>
                  <th class="px-6 py-3 font-bold">Candidate Details</th>
                  <th class="px-6 py-3 font-bold">Experience</th>
                  <th class="px-6 py-3 font-bold">Latest Role</th>
                  <th class="px-6 py-3 font-bold">Profile Summary</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 text-sm">
                <tr v-for="r in ctx.resumesList" :key="r.id" class="hover:bg-slate-50 transition-colors group">
                  <td class="px-6 py-4">
                    <div class="flex items-center gap-3">
                      <div class="h-10 w-10 rounded-full bg-slate-100 text-slate-500 font-bold flex items-center justify-center text-xs group-hover:bg-indigo-100 group-hover:text-indigo-600 transition-colors">
                        {{ (r.name || '?').charAt(0).toUpperCase() }}
                      </div>
                      <div>
                        <div class="font-bold text-slate-900">{{ r.name || 'Unknown' }}</div>
                        <div class="text-xs text-slate-500">{{ r.email }}</div>
                        <div class="text-[10px] text-slate-400 mt-0.5">{{ r.phone }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-md bg-slate-100 text-slate-700 text-xs font-medium">
                      {{ r.total_experience != null ? r.total_experience + ' Yrs' : 'N/A' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-slate-600 font-medium">
                    {{ r.current_role || r.current_company || '-' }}
                  </td>
                  <td class="px-6 py-4 max-w-xs">
                    <p class="line-clamp-2 text-xs text-slate-500 leading-relaxed">{{ (r.summary || '').replace(/\s+/g, ' ').trim() || 'No summary available.' }}</p>
                  </td>
                </tr>
              </tbody>
            </table>

            <div class="px-6 py-4 border-t border-slate-100 flex items-center justify-between bg-slate-50/50">
              <span class="text-xs text-slate-500 font-medium">Page {{ ctx.resumesPage }} ({{ ctx.resumesList.length }} items)</span>
              <div class="flex gap-2">
                <button
                  class="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-600 text-xs font-bold hover:bg-slate-50 hover:border-slate-300 transition disabled:opacity-50"
                  :disabled="ctx.resumesPage === 1"
                  @click="ctx.loadResumes(ctx.resumesPage - 1)"
                >
                  Previous
                </button>
                <button
                  class="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-600 text-xs font-bold hover:bg-slate-50 hover:border-slate-300 transition disabled:opacity-50"
                  :disabled="ctx.resumesList.length < ctx.resumesPerPage"
                  @click="ctx.loadResumes(ctx.resumesPage + 1)"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script>
export default {
  name: 'HrDashboardResumesTab',
  inject: ['hrDashboardContext'],
  computed: {
    ctx() {
      return this.hrDashboardContext
    },
  },
}
</script>

<style scoped>
.resumes-shell {
  background: #f6faf6;
}
.resumes-hero {
  border-radius: 2rem;
  border: 1px solid #498528;
  background: #ffffff;
  padding: 2rem;
  box-shadow: 0 32px 80px rgba(15, 23, 42, 0.15);
}
.resumes-panel {
  border-radius: 1.75rem;
  border: 1px solid rgba(73, 133, 40, 0.3);
  background: #ffffff;
  padding: 1.5rem;
  box-shadow: 0 25px 45px rgba(15, 23, 42, 0.08);
}
.resumes-subpanel {
  border-radius: 1.5rem;
  border: 1px solid rgba(73, 133, 40, 0.2);
  background: #ffffff;
  padding: 1rem;
  box-shadow: inset 0 0 0 1px rgba(73, 133, 40, 0.08);
}
.resumes-hero header h2 {
  color: #0f172a;
}
.resumes-table-panel {
  background: #ffffff;
}
.resumes-table-shell {
  background: #ffffff;
  border-radius: 1.5rem;
  border: 1px solid rgba(73, 133, 40, 0.25);
  box-shadow: 0 20px 35px rgba(15, 23, 42, 0.08);
}
.resumes-shell .primary-btn {
  min-height: 3rem;
}
</style>
