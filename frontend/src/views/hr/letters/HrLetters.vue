<template>
  <section class="min-h-screen bg-slate-50/50 p-6 lg:p-10">
    
    <header class="mb-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
      <div>
        <div class="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-violet-600 mb-2">
          <span class="h-2 w-2 rounded-full bg-violet-500"></span>
          Configuration
        </div>
        <h2 class="text-3xl font-bold tracking-tight text-slate-900">Letter Templates</h2>
        <p class="mt-2 text-slate-500 max-w-2xl">
          Define standard formats for offers, relieving letters, and experience certificates.
        </p>
      </div>
      <button 
        class="inline-flex items-center justify-center gap-2 rounded-xl bg-violet-600 px-5 py-3 text-sm font-bold text-white shadow-lg shadow-violet-200 transition-all hover:bg-violet-700 hover:-translate-y-0.5 active:translate-y-0" 
        @click="openNewTemplate"
      >
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
        <span>Create Template</span>
      </button>
    </header>

    <div v-if="loading && !showForm" class="flex flex-col items-center justify-center py-20">
      <div class="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-violet-600"></div>
      <p class="mt-4 font-medium text-slate-500">Syncing templates...</p>
    </div>

    <div v-else-if="error" class="rounded-2xl border border-rose-100 bg-rose-50 p-6 text-center">
       <p class="font-bold text-rose-700">Unable to load templates</p>
       <p class="text-sm text-rose-600">{{ error }}</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      
      <div v-if="!templates.length" class="col-span-full rounded-[2rem] border border-slate-200 bg-white p-16 text-center shadow-sm">
        <div class="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-slate-50 ring-1 ring-slate-100">
          <svg class="h-10 w-10 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
        </div>
        <h3 class="mt-6 text-lg font-bold text-slate-900">No templates yet</h3>
        <p class="text-slate-500">Create your first letter template to get started.</p>
        <button @click="openNewTemplate" class="mt-4 text-sm font-bold text-violet-600 hover:text-violet-800 hover:underline">Create Now &rarr;</button>
      </div>

      <div 
        v-for="tpl in templates" 
        :key="tpl.id" 
        class="group relative flex flex-col justify-between overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:border-violet-200 hover:shadow-md"
      >
        <div>
          <div class="flex items-start justify-between mb-4">
            <div class="h-10 w-10 rounded-lg bg-violet-50 flex items-center justify-center text-violet-600 font-bold text-lg">
              {{ tpl.name.charAt(0).toUpperCase() }}
            </div>
            <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
               <button @click="editTemplate(tpl)" class="p-2 text-slate-400 hover:text-violet-600 bg-slate-50 hover:bg-violet-50 rounded-lg transition" title="Edit">
                 <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
               </button>
               <button @click="deleteTemplate(tpl)" class="p-2 text-slate-400 hover:text-rose-600 bg-slate-50 hover:bg-rose-50 rounded-lg transition" title="Delete">
                 <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
               </button>
            </div>
          </div>
          
          <h3 class="text-lg font-bold text-slate-900 mb-2 line-clamp-1">{{ tpl.name }}</h3>
          <p class="text-sm text-slate-500 line-clamp-2 min-h-[2.5em]">{{ tpl.description || 'No description provided.' }}</p>
        </div>

        <div class="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400 font-medium font-mono">
           <span>ID: {{ tpl.id }}</span>
           <span>TXT Format</span>
        </div>
      </div>
    </div>

    <div v-if="showForm" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity" @click="cancelForm"></div>
      
      <div class="relative w-full max-w-2xl transform overflow-hidden rounded-3xl bg-white shadow-2xl transition-all max-h-[90vh] flex flex-col">
        
        <div class="px-8 py-6 border-b border-slate-100 bg-slate-50/50">
          <h3 class="text-xl font-bold text-slate-900">{{ isEditing ? 'Edit Template' : 'New Letter Template' }}</h3>
          <p class="text-sm text-slate-500 mt-1">Configure the content and dynamic variables.</p>
        </div>

        <div class="p-8 overflow-y-auto">
          <div class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Template Name</label>
                <input 
                  v-model="form.name" 
                  type="text" 
                  class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium outline-none focus:border-violet-500 focus:ring-4 focus:ring-violet-500/10 transition" 
                  placeholder="e.g. Relieving Letter" 
                />
              </div>
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Short Description</label>
                <input 
                  v-model="form.description" 
                  type="text" 
                  class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium outline-none focus:border-violet-500 focus:ring-4 focus:ring-violet-500/10 transition" 
                  placeholder="e.g. Standard exit document" 
                />
              </div>
            </div>

            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="block text-xs font-bold uppercase tracking-wider text-slate-500">Content Body</label>
                <span class="text-[10px] text-slate-400 bg-slate-100 px-2 py-1 rounded">Markdown Supported</span>
              </div>
              <textarea 
                v-model="form.content" 
                rows="10" 
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-mono text-slate-700 leading-relaxed outline-none focus:border-violet-500 focus:ring-4 focus:ring-violet-500/10 transition resize-none" 
                placeholder="Dear {first_name}, ..."
              ></textarea>
            </div>

            <div class="rounded-xl border border-blue-100 bg-blue-50/50 p-4">
              <p class="text-xs font-bold text-blue-800 mb-3 flex items-center gap-2">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                Click variables to copy
              </p>
              <div class="flex flex-wrap gap-2">
                <button 
                  v-for="ph in placeholders" 
                  :key="ph"
                  @click="copyToContent(ph)"
                  type="button"
                  class="group relative rounded-lg border border-blue-200 bg-white px-2 py-1 text-xs font-mono text-slate-600 hover:border-blue-400 hover:text-blue-600 transition"
                >
                  {{ ph }}
                  <span class="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[10px] px-2 py-1 rounded opacity-0 group-active:opacity-100 transition-opacity whitespace-nowrap">Copied!</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="px-8 py-5 bg-slate-50 border-t border-slate-100 flex items-center justify-end gap-3">
          <button 
            @click="cancelForm"
            class="px-5 py-2.5 rounded-xl border border-slate-200 bg-white text-sm font-bold text-slate-600 hover:bg-slate-50 hover:text-slate-800 transition"
          >
            Cancel
          </button>
          <button 
            @click="saveTemplate"
            :disabled="loading"
            class="px-6 py-2.5 rounded-xl bg-violet-600 text-sm font-bold text-white shadow-md hover:bg-violet-700 hover:shadow-lg disabled:opacity-70 disabled:cursor-not-allowed transition"
          >
            {{ loading ? 'Saving...' : (isEditing ? 'Update Template' : 'Create Template') }}
          </button>
        </div>

      </div>
    </div>

  </section>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HrLetters',
  props: {
    context: {
      type: Object,
      required: false,
    },
  },
  data() {
    return {
      loading: false,
      error: null,
      templates: [],
      showForm: false,
      isEditing: false,
      form: {
        id: null,
        name: '',
        description: '',
        content: '',
      },
      placeholders: [
        '{first_name}', '{last_name}', '{full_name}', 
        '{job_title}', '{department}', 
        '{hire_date}', '{exit_date}', 
        '{manager_name}', '{company_name}'
      ]
    }
  },
  mounted() {
    this.fetchTemplates()
  },
  methods: {
    getAuthHeaders() {
      const token = localStorage.getItem('authToken')
      return token ? { 'Authentication-Token': token } : {}
    },
    
    copyToContent(text) {
      // Logic to insert text into cursor position or just copy to clipboard
      navigator.clipboard.writeText(text);
      
      // Simple Append fallback if clipboard fails or for ease
      this.form.content += ` ${text} `;
    },

    async fetchTemplates() {
      this.loading = true
      this.error = null
      try {
        const res = await axios.get(`${process.env.VUE_APP_API_BASE_URL || '/api'}/letters/templates`, {
          headers: this.getAuthHeaders(),
        })
        this.templates = res.data.templates || []
      } catch (err) {
        this.error = err?.response?.data?.error || err.message || 'Failed to load templates'
      } finally {
        this.loading = false
      }
    },

    openNewTemplate() {
      this.isEditing = false
      this.form = { id: null, name: '', description: '', content: '' }
      this.showForm = true
    },

    editTemplate(tpl) {
      this.isEditing = true
      this.form = { id: tpl.id, name: tpl.name, description: tpl.description || '', content: tpl.content }
      this.showForm = true
    },

    cancelForm() {
      this.showForm = false
      this.isEditing = false
    },

    async saveTemplate() {
      const { id, name, description, content } = this.form
      if (!name || !content) {
        // Fallback alert if context toast isn't available
        if(this.context?.showToast) this.context.showToast('Name and content are required', 'error')
        else alert('Name and content are required')
        return
      }
      
      this.loading = true
      this.error = null
      
      try {
        const url = `${process.env.VUE_APP_API_BASE_URL || '/api'}/letters/templates`
        const config = { headers: this.getAuthHeaders() }
        const payload = { name, description, content }

        if (this.isEditing) {
          await axios.patch(`${url}/${id}`, payload, config)
          if(this.context?.showToast) this.context.showToast('Template updated successfully', 'success')
        } else {
          await axios.post(url, payload, config)
          if(this.context?.showToast) this.context.showToast('Template created successfully', 'success')
        }
        
        this.showForm = false
        await this.fetchTemplates()
      } catch (err) {
        const msg = err?.response?.data?.error || err.message || 'Failed to save template'
        if(this.context?.showToast) this.context.showToast(msg, 'error')
        else alert(msg)
      } finally {
        this.loading = false
      }
    },

    async deleteTemplate(tpl) {
      if (!confirm(`Are you sure you want to delete "${tpl.name}"? This cannot be undone.`)) {
        return
      }
      this.loading = true
      try {
        await axios.delete(
          `${process.env.VUE_APP_API_BASE_URL || '/api'}/letters/templates/${tpl.id}`,
          { headers: this.getAuthHeaders() },
        )
        if(this.context?.showToast) this.context.showToast('Template deleted', 'success')
        await this.fetchTemplates()
      } catch (err) {
        const msg = err?.response?.data?.error || err.message || 'Failed to delete template'
        if(this.context?.showToast) this.context.showToast(msg, 'error')
        else alert(msg)
      } finally {
        this.loading = false
      }
    },
  },
}
</script>