<template>
  <div class="profile-container" style="max-width:700px; margin:40px auto;">
    <h2>My Profile & Resume</h2>

    <div style="margin-top:1rem;">
      <label style="display:block; margin-bottom:0.5rem;">Upload Resume</label>
      <input type="file" ref="fileInput" @change="onFileChange" />
      <div style="margin-top:0.75rem; display:flex; gap:10px;">
        <button @click="upload" :disabled="!file || uploading" style="padding:0.5rem 1rem; background:#4f46e5; color:white; border:none; border-radius:6px;">{{ uploading ? 'Uploading...' : 'Upload' }}</button>
        <button @click="downloadMyResume" style="padding:0.5rem 1rem; background:#10b981; color:white; border:none; border-radius:6px;">Download My Resume</button>
      </div>
      <p v-if="message" :style="{ color: messageType === 'error' ? 'red' : 'green', marginTop: '0.75rem' }">{{ message }}</p>
    </div>

    <hr style="margin:24px 0;" />

    <div>
      <h3>Admin: Download user resume</h3>
      <div style="display:flex; gap:8px; align-items:center;">
        <input v-model="adminUserId" type="number" placeholder="User ID" style="padding:0.4rem; width:120px;" />
        <button @click="adminDownloadResume" style="padding:0.4rem 0.8rem; background:#ef4444; color:white; border:none; border-radius:6px;">Download</button>
      </div>
      <p v-if="adminMessage" style="color:#ef4444; margin-top:0.5rem;">{{ adminMessage }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || '/api'

const file = ref(null)
const uploading = ref(false)
const message = ref('')
const messageType = ref('')
const adminUserId = ref('')
const adminMessage = ref('')

function onFileChange(e) {
  message.value = ''
  const f = e.target.files[0]
  if (f) file.value = f
}

async function upload() {
  if (!file.value) {
    messageType.value = 'error'
    message.value = 'Please choose a file first.'
    return
  }

  uploading.value = true
  const form = new FormData()
  form.append('file', file.value)

  try {
    const res = await axios.post(`${API_BASE_URL}/me/resume`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      withCredentials: true
    })
    messageType.value = 'success'
    message.value = res.data?.message || 'Uploaded'
  } catch (err) {
    messageType.value = 'error'
    message.value = err.response?.data?.error || 'Upload failed'
  } finally {
    uploading.value = false
  }
}

async function downloadMyResume() {
  try {
    const res = await axios.get(`${API_BASE_URL}/me/resume`, { responseType: 'blob', withCredentials: true })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = 'resume.bin'
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    messageType.value = 'error'
    message.value = err.response?.data?.error || 'Download failed'
  }
}

async function adminDownloadResume() {
  adminMessage.value = ''
  if (!adminUserId.value) {
    adminMessage.value = 'Provide a user id.'
    return
  }

  try {
    const res = await axios.get(`${API_BASE_URL}/admin/users/${adminUserId.value}/resume`, { responseType: 'blob', withCredentials: true })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `user_${adminUserId.value}_resume.bin`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    adminMessage.value = err.response?.data?.error || 'Admin download failed'
  }
}
</script>

<style scoped>
.profile-container { background: #fff; padding: 24px; border-radius: 8px; box-shadow: 0 6px 20px rgba(16,24,40,0.06); }
</style>
