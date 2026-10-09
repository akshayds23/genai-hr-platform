<template>
  <section class="faqs-shell min-h-screen">
    <div class="mx-auto w-full max-w-7xl px-6 py-10 space-y-10">
      <!-- Header -->
      <header class="faqs-header rounded-3xl border border-indigo-100 bg-white/80 p-8 shadow-sm backdrop-blur">
        <div class="flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
          <div class="space-y-3">
            <div class="inline-flex items-center gap-2 rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-indigo-700">
              <span class="relative flex h-2 w-2">
                <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-indigo-400 opacity-75"></span>
                <span class="relative inline-flex h-2 w-2 rounded-full bg-indigo-600"></span>
              </span>
              Knowledge Studio
            </div>
            <div>
              <h2 class="text-3xl font-bold tracking-tight text-slate-900">FAQs & Knowledge Base</h2>
              <p class="mt-2 text-sm leading-relaxed text-slate-600">
                Keep every HR answer one click away. Browse the knowledge base on the left and capture new entries without leaving the page.
              </p>
            </div>
          </div>

          <div class="flex flex-wrap gap-3">
            <button
              type="button"
              @click="showUploadModal = true"
              class="inline-flex items-center gap-2 rounded-2xl border border-emerald-100 bg-emerald-50 px-5 py-3 text-sm font-semibold text-emerald-700 transition hover:border-emerald-200 hover:bg-emerald-100"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Upload File
            </button>
            <button
              type="button"
              @click="startCreate"
              class="inline-flex items-center gap-2 rounded-2xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Quick Add
            </button>
          </div>
        </div>

        <div class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <article class="rounded-2xl border border-slate-100 bg-white p-4">
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Articles</p>
            <p class="mt-2 text-3xl font-bold text-slate-900">{{ totalFaqs }}</p>
            <p class="text-xs text-slate-500">Total active FAQs</p>
          </article>
          <article class="rounded-2xl border border-slate-100 bg-white p-4">
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Selected</p>
            <p class="mt-2 text-3xl font-bold text-slate-900">{{ selectedFaqs.length }}</p>
            <p class="text-xs text-slate-500">Ready for bulk actions</p>
          </article>
          <article class="rounded-2xl border border-slate-100 bg-white p-4">
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Per page</p>
            <p class="mt-2 text-3xl font-bold text-slate-900">{{ perPage }}</p>
            <p class="text-xs text-slate-500">Visible at a glance</p>
          </article>
        </div>
      </header>

      <div class="grid gap-8 xl:grid-cols-[minmax(0,1fr)_360px]">
        <!-- Left column -->
        <div class="space-y-6">
          <div class="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
            <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div class="relative w-full lg:max-w-md">
                <input
                  v-model="searchQuery"
                  @input="debouncedSearch"
                  type="text"
                  placeholder="Search questions or keywords"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 pl-11 pr-4 py-3 text-sm focus:border-indigo-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-100"
                />
                <svg class="absolute left-4 top-3.5 h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>

              <div class="flex flex-wrap items-center gap-3 text-sm text-slate-600">
                <span class="rounded-full bg-slate-100 px-3 py-1 font-medium">
                  Page {{ currentPage }} / {{ totalPages || 1 }}
                </span>
                <button
                  v-if="selectedFaqs.length"
                  type="button"
                  @click="bulkDeleteFaqs"
                  class="inline-flex items-center gap-2 rounded-full bg-red-50 px-3 py-1.5 font-semibold text-red-600 transition hover:bg-red-100"
                >
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Delete {{ selectedFaqs.length }}
                </button>
              </div>
            </div>
          </div>

          <div class="space-y-4">
            <div v-if="loading" class="flex h-60 items-center justify-center rounded-2xl border border-slate-100 bg-white">
              <div class="h-8 w-8 animate-spin rounded-full border-4 border-indigo-200 border-t-indigo-600"></div>
            </div>

            <div v-else-if="faqs.length === 0" class="rounded-2xl border border-dashed border-slate-200 bg-white p-12 text-center shadow-sm">
              <svg class="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 class="mt-4 text-lg font-semibold text-slate-900">No FAQs yet</h3>
              <p class="mt-2 text-sm text-slate-500">Start by creating your first entry. The form on the right is always ready.</p>
              <button
                type="button"
                @click="startCreate"
                class="mt-6 inline-flex items-center gap-2 rounded-2xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
              >
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Add FAQ
              </button>
            </div>

            <div
              v-else
              class="space-y-4"
            >
              <article
                v-for="faq in faqs"
                :key="faq.id"
                class="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-100 hover:shadow-md"
              >
                <div class="flex items-start justify-between gap-4">
                  <div class="flex flex-1 items-start gap-4">
                    <input
                      type="checkbox"
                      :checked="selectedFaqs.includes(faq.id)"
                      @change="toggleFaqSelection(faq.id)"
                      class="mt-1 h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                    />
                    <div class="flex-1 space-y-3">
                      <h3 class="text-lg font-semibold text-slate-900">{{ faq.question }}</h3>
                      <p class="text-sm leading-relaxed text-slate-600">
                        {{ faq.answer }}
                      </p>
                      <div class="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-500">
                        <span class="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-1 font-medium text-slate-600">
                          <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                          </svg>
                          {{ faq.source || 'Manual Entry' }}
                        </span>
                        <span v-if="faq.created_at">Added {{ formatDate(faq.created_at) }}</span>
                        <span v-if="faq.updated_at && faq.updated_at !== faq.created_at">Updated {{ formatDate(faq.updated_at) }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <button
                      type="button"
                      @click="editFaq(faq)"
                      class="rounded-xl p-2 text-slate-400 transition hover:bg-indigo-50 hover:text-indigo-600"
                      title="Edit FAQ"
                    >
                      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      type="button"
                      @click="deleteFaq(faq.id)"
                      class="rounded-xl p-2 text-slate-400 transition hover:bg-red-50 hover:text-red-600"
                      title="Delete FAQ"
                    >
                      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </article>
            </div>
          </div>

          <div v-if="totalPages > 1" class="rounded-2xl border border-slate-100 bg-white px-5 py-4 shadow-sm">
            <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <p class="text-sm text-slate-500">
                Showing {{ ((currentPage - 1) * perPage) + 1 }} - {{ Math.min(currentPage * perPage, totalFaqs) }} of {{ totalFaqs }} FAQs
              </p>
              <div class="flex flex-wrap gap-2">
                <button
                  type="button"
                  @click="goToPage(currentPage - 1)"
                  :disabled="currentPage === 1"
                  class="rounded-xl border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Previous
                </button>
                <button
                  v-for="page in visiblePages"
                  :key="page"
                  type="button"
                  @click="goToPage(page)"
                  :class="[
                    'rounded-xl border px-3 py-2 text-sm font-semibold transition',
                    page === currentPage
                      ? 'border-indigo-600 bg-indigo-600 text-white'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                  ]"
                >
                  {{ page }}
                </button>
                <button
                  type="button"
                  @click="goToPage(currentPage + 1)"
                  :disabled="currentPage === totalPages"
                  class="rounded-xl border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Right column: Always-on form -->
        <aside ref="formPanel" class="space-y-4 xl:sticky xl:top-8">
          <div class="rounded-3xl border border-indigo-100 bg-white p-6 shadow-lg">
            <div class="mb-6 flex items-center justify-between">
              <div>
                <p class="text-xs font-semibold uppercase tracking-wide text-indigo-500">{{ isEditing ? 'Editing entry' : 'New entry' }}</p>
                <h3 class="text-xl font-bold text-slate-900">{{ isEditing ? 'Update FAQ' : 'Add FAQ' }}</h3>
              </div>
              <button
                v-if="isEditing"
                type="button"
                @click="startCreate"
                class="text-sm font-semibold text-indigo-600 underline-offset-4 hover:underline"
              >
                New
              </button>
            </div>

            <form @submit.prevent="saveFaq" class="space-y-5">
              <div class="space-y-2">
                <label class="text-sm font-semibold text-slate-700">Question <span class="text-red-500">*</span></label>
                <textarea
                  ref="questionInput"
                  v-model="faqForm.question"
                  rows="3"
                  placeholder="What can we help employees with?"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm focus:border-indigo-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-100"
                  required
                ></textarea>
              </div>

              <div class="space-y-2">
                <label class="text-sm font-semibold text-slate-700">Answer <span class="text-red-500">*</span></label>
                <textarea
                  v-model="faqForm.answer"
                  rows="6"
                  placeholder="Provide the clearest answer, links, or policy snippets."
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm focus:border-indigo-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-100"
                  required
                ></textarea>
              </div>

              <div class="flex flex-wrap items-center gap-3 pt-2">
                <button
                  type="submit"
                  :disabled="saving"
                  class="inline-flex flex-1 items-center justify-center gap-2 rounded-2xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:opacity-50"
                >
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  {{ saving ? 'Saving...' : isEditing ? 'Update FAQ' : 'Add FAQ' }}
                </button>
                <button
                  type="button"
                  @click="resetForm"
                  class="rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-600 transition hover:bg-slate-50"
                >
                  Clear
                </button>
              </div>
            </form>
          </div>

          <div class="rounded-3xl border border-slate-100 bg-slate-900/90 p-6 text-white shadow-lg">
            <p class="text-sm font-semibold uppercase tracking-wide text-emerald-300">Tips</p>
            <p class="mt-3 text-base text-slate-100">Short answers perform best. Include policy tags and links so the chatbot references the latest source.</p>
          </div>
        </aside>
      </div>
    </div>

    <!-- Upload modal -->
    <div v-if="showUploadModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div class="w-full max-w-lg rounded-3xl bg-white shadow-2xl">
        <div class="border-b border-slate-100 px-6 py-5">
          <h3 class="text-lg font-semibold text-slate-900">Upload Knowledge Base</h3>
          <p class="mt-1 text-sm text-slate-500">PDF or TXT with Q/A pairs. Each pair should start with "Q:" followed by "A:".</p>
        </div>
        <form @submit.prevent="uploadFile" class="space-y-6 px-6 py-6">
          <div class="cursor-pointer rounded-2xl border-2 border-dashed border-slate-300 p-6 text-center transition hover:border-indigo-300">
            <input
              ref="fileInput"
              type="file"
              accept=".pdf,.txt"
              @change="handleFileSelect"
              class="hidden"
            />
            <div v-if="!selectedFile" @click="$refs.fileInput.click()">
              <svg class="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p class="mt-4 text-sm font-semibold text-slate-900">Drop file here or click to browse</p>
              <p class="text-xs text-slate-500">Max 10MB • PDF or TXT</p>
            </div>
            <div v-else class="space-y-3 text-sm">
              <p class="flex items-center justify-center gap-2 text-indigo-600">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {{ selectedFile.name }}
              </p>
              <button type="button" class="text-xs text-slate-500 hover:text-red-600" @click="selectedFile = null">Remove file</button>
            </div>
          </div>
          <div class="flex items-center justify-end gap-3">
            <button
              type="button"
              @click="closeUploadModal"
              class="rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="!selectedFile || uploading"
              class="rounded-2xl bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-50"
            >
              {{ uploading ? 'Uploading…' : 'Upload & Process' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>

<script>
import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || '/api'

export default {
  name: 'FaqsTab',
  data() {
    return {
      faqs: [],
      totalFaqs: 0,
      currentPage: 1,
      perPage: 3,
      totalPages: 1,
      loading: false,
      searchQuery: '',
      selectedFaqs: [],

      // Form state
      isEditing: false,
      faqForm: {
        id: null,
        question: '',
        answer: ''
      },

      // Upload
      showUploadModal: false,
      selectedFile: null,
      uploading: false,
      saving: false,

      // Debounce timer
      searchTimer: null
    }
  },

  computed: {
    visiblePages() {
      const pages = []
      const start = Math.max(1, this.currentPage - 2)
      const end = Math.min(this.totalPages, this.currentPage + 2)

      for (let i = start; i <= end; i++) {
        pages.push(i)
      }

      return pages
    },

    debouncedSearch() {
      return () => {
        clearTimeout(this.searchTimer)
        this.searchTimer = setTimeout(() => {
          this.currentPage = 1
          this.loadFaqs()
        }, 500)
      }
    }
  },

  mounted() {
    this.loadFaqs()
  },

  methods: {
    async loadFaqs() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          per_page: this.perPage,
          search: this.searchQuery || undefined
        }

        const response = await axios.get(`${API_BASE_URL}/admin/faqs`, {
          params,
          withCredentials: true
        })

        this.faqs = response.data.faqs
        this.totalFaqs = response.data.total
        this.totalPages = Math.ceil(this.totalFaqs / this.perPage) || 1
      } catch (error) {
        console.error('Failed to load FAQs:', error)
        this.showToast('Failed to load FAQs', 'error')
      } finally {
        this.loading = false
      }
    },

    async saveFaq() {
      this.saving = true
      try {
        const url = this.isEditing
          ? `${API_BASE_URL}/admin/faqs/${this.faqForm.id}`
          : `${API_BASE_URL}/admin/faqs`

        const method = this.isEditing ? 'PUT' : 'POST'

        await axios({
          method,
          url,
          data: {
            question: this.faqForm.question.trim(),
            answer: this.faqForm.answer.trim()
          },
          withCredentials: true
        })

        this.showToast(`FAQ ${this.isEditing ? 'updated' : 'created'} successfully`, 'success')
        this.resetForm()
        this.loadFaqs()
      } catch (error) {
        console.error('Failed to save FAQ:', error)
        const message = error.response?.data?.error || 'Failed to save FAQ'
        this.showToast(message, 'error')
      } finally {
        this.saving = false
      }
    },

    async deleteFaq(faqId) {
      if (!confirm('Are you sure you want to delete this FAQ?')) return

      try {
        await axios.delete(`${API_BASE_URL}/admin/faqs/${faqId}`, {
          withCredentials: true
        })

        this.showToast('FAQ deleted successfully', 'success')
        this.loadFaqs()
      } catch (error) {
        console.error('Failed to delete FAQ:', error)
        this.showToast('Failed to delete FAQ', 'error')
      }
    },

    async bulkDeleteFaqs() {
      if (!confirm(`Are you sure you want to delete ${this.selectedFaqs.length} FAQs?`)) return

      try {
        await axios.post(`${API_BASE_URL}/admin/faqs/bulk-delete`, {
          ids: this.selectedFaqs
        }, {
          withCredentials: true
        })

        this.showToast(`Deleted ${this.selectedFaqs.length} FAQs successfully`, 'success')
        this.selectedFaqs = []
        this.loadFaqs()
      } catch (error) {
        console.error('Failed to bulk delete FAQs:', error)
        this.showToast('Failed to delete FAQs', 'error')
      }
    },

    async uploadFile() {
      if (!this.selectedFile) return

      this.uploading = true
      try {
        const formData = new FormData()
        formData.append('file', this.selectedFile)

        const response = await axios.post(`${API_BASE_URL}/admin/faqs/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          withCredentials: true
        })

        this.showToast(response.data.message, 'success')
        this.closeUploadModal()
        this.loadFaqs()
      } catch (error) {
        console.error('Failed to upload file:', error)
        const message = error.response?.data?.error || 'Failed to upload file'
        this.showToast(message, 'error')
      } finally {
        this.uploading = false
      }
    },

    startCreate() {
      this.isEditing = false
      this.faqForm = { id: null, question: '', answer: '' }
      this.focusFormPanel()
      this.focusQuestionInput()
    },

    editFaq(faq) {
      this.faqForm = {
        id: faq.id,
        question: faq.question,
        answer: faq.answer
      }
      this.isEditing = true
      this.focusFormPanel()
      this.focusQuestionInput()
    },

    resetForm() {
      this.startCreate()
    },

    focusFormPanel() {
      this.$nextTick(() => {
        if (this.$refs.formPanel) {
          this.$refs.formPanel.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      })
    },

    focusQuestionInput() {
      this.$nextTick(() => {
        this.$refs.questionInput?.focus()
      })
    },

    toggleFaqSelection(faqId) {
      const index = this.selectedFaqs.indexOf(faqId)
      if (index > -1) {
        this.selectedFaqs.splice(index, 1)
      } else {
        this.selectedFaqs.push(faqId)
      }
    },

    handleFileSelect(event) {
      this.selectedFile = event.target.files[0] || null
    },

    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        this.loadFaqs()
      }
    },

    closeUploadModal() {
      this.showUploadModal = false
      this.selectedFile = null
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },

    showToast(message, type = 'info') {
      const toast = document.createElement('div')
      toast.className = `fixed top-4 right-4 z-50 rounded-xl px-4 py-3 text-sm font-medium text-white ${
        type === 'success' ? 'bg-emerald-600' :
        type === 'error' ? 'bg-red-600' : 'bg-indigo-600'
      }`
      toast.textContent = message
      document.body.appendChild(toast)

      setTimeout(() => {
        toast.remove()
      }, 4000)
    }
  }
}
</script>

<style scoped>
.faqs-shell {
  background: #f6faf6;
  padding-bottom: 3rem;
}
.faqs-header {
  border-color: rgba(73, 133, 40, 0.2);
  background: #ffffff;
}
.faqs-shell .rounded-2xl {
  border-color: rgba(73, 133, 40, 0.2);
}
.faqs-panel {
  border-radius: 1.75rem;
  border: 1px solid rgba(73, 133, 40, 0.3);
  background: #ffffff;
  box-shadow: 0 25px 45px rgba(15, 23, 42, 0.08);
}
.faqs-shell .bg-white {
  background: #ffffff;
}
</style>
