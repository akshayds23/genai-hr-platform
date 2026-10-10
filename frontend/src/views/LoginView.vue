<template>
  <div class="page-shell" role="main" aria-label="Login page">
    <!-- animated background -->
    <div class="bg-layer" aria-hidden="true">
      <span class="bubble b1"></span>
      <span class="bubble b2"></span>
      <span class="bubble b3"></span>
      <span class="bubble b4"></span>
    </div>

    <!-- central card -->
    <div class="card-frame">
      <!-- LEFT: wavy white panel with illustration -->
      <div class="left-panel">
        <!-- the wavy partition is drawn with SVG; it's part of the panel so it always looks organic -->
        <svg class="left-wave" viewBox="0 0 1400 1000" preserveAspectRatio="none" aria-hidden="true">
          <defs>
            <linearGradient id="LGrad" x1="0" x2="1">
              <stop offset="0%" stop-color="#ffffff" />
              <stop offset="100%" stop-color="#f3fbf9" />
            </linearGradient>
            <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="8" stdDeviation="30" flood-color="#0a2e27" flood-opacity="0.07"/>
            </filter>
          </defs>
          <!-- big organic path - tweak points to adjust curvature -->
          <path d="M0 0 H820 C980 0 1100 160 1240 300 C1300 360 1400 470 1400 600 V1000 H0 Z"
                fill="url(#LGrad)" filter="url(#softShadow)"/>
        </svg>

        <!-- small top-left logo -->
        <div class="brand-top">
          <BrandLogo size="sm" />
        </div>

        <!-- illustration container (image centered) -->
        <div
          class="illustration-wrap"
          @mousemove="onMouseMove"
          @mouseleave="onLeave"
          :style="`transform: perspective(900px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) translateY(${bob}px)`"
        >
          <div class="illustration-card" :style="{ boxShadow: illShadow }">
            <img
              :src="employeeSrc"
              alt="Illustration of person working on laptop"
              class="employee-img"
              @load="imgLoaded = true"
            />
            <!-- subtle accent shapes overlaid -->
            <svg class="accent-dots" viewBox="0 0 200 200" aria-hidden="true">
              <circle cx="18" cy="20" r="10" fill="#e6faf4" opacity="0.9"/>
              <circle cx="160" cy="40" r="6" fill="#dff6ef" opacity="0.85"/>
              <circle cx="110" cy="150" r="8" fill="#dff6ef" opacity="0.7"/>
            </svg>
          </div>

          <div class="illustration-caption">
            <div class="title">Human Resource Management</div>
            <div class="sub">Smart & delightful experience for your team</div>
          </div>
        </div>
      </div>

      <!-- RIGHT: dark green form area -->
      <div class="right-panel" role="form" aria-labelledby="loginHeading">
        <div class="form-inner">
          <h1 id="loginHeading" class="heading">Welcome back</h1>
          <p class="subheading">Sign in to access the HR dashboard</p>

          <form class="form" @submit.prevent="handleLogin" novalidate>
            <label class="field">
              <span class="field-label">Role</span>
              <select v-model="selectedRole" class="input" required aria-label="Role">
                <option v-for="opt in roleOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </label>

            <label class="field">
              <span class="field-label">Email</span>
              <input v-model="email" type="email" placeholder="you@company.com" class="input" required aria-label="Email" />
            </label>

            <label class="field">
              <span class="field-label">Password</span>
              <input v-model="password" type="password" placeholder="Enter your password" class="input" required aria-label="Password" />
            </label>

            <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>

            <button
              type="submit"
              class="cta"
              :disabled="isLoading"
              :aria-busy="isLoading ? 'true' : 'false'"
            >
              <span v-if="isLoading" class="spinner" aria-hidden="true"></span>
              {{ isLoading ? 'Signing in…' : 'Login to App' }}
            </button>

            <div v-if="isDemoMode" class="demo-section">
              <div class="demo-divider">
                <span>Or try a demo account</span>
              </div>
              <div class="demo-buttons">
                <button
                  type="button"
                  class="demo-btn"
                  :disabled="isLoading"
                  @click="loginAsDemo('hr')"
                >
                  Try as HR
                </button>
                <button
                  type="button"
                  class="demo-btn"
                  :disabled="isLoading"
                  @click="loginAsDemo('manager')"
                >
                  Try as Manager
                </button>
                <button
                  type="button"
                  class="demo-btn"
                  :disabled="isLoading"
                  @click="loginAsDemo('employee')"
                >
                  Try as Employee
                </button>
              </div>
            </div>

            <div class="helper-row">
              <router-link to="/" class="link-minor">Back to Home</router-link>
            </div>
          </form>
          <div v-if="isWakingUp" class="wake-banner" role="status">
            <span class="spinner-small" aria-hidden="true"></span>
            <span>Waking up the demo server, this can take up to a minute...</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import BrandLogo from '@/components/BrandLogo.vue'

// --- State & inputs (keeps your original logic) ---
const router = useRouter()
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)
const roleOptions = [
  { label: 'Employee', value: 'employee' },
  { label: 'Manager', value: 'manager' },
  { label: 'HR', value: 'hr' },
]
const selectedRole = ref(roleOptions[0].value)

const isDemoMode = computed(() => {
  return process.env.VUE_APP_DEMO_MODE === 'true'
})

const isWakingUp = ref(false)

const API_BASE_URL = (process.env.VUE_APP_API_BASE_URL || '/api').replace(/\/$/, '')
const API_URL = `${API_BASE_URL}/login`
const ROLE_STORAGE_KEY = 'activeUserRole'

// --- Illustration & tilt state for interactivity ---
const employeeSrc = new URL('@/assets/Login.svg', import.meta.url).href
const bob = ref(0)
const tiltX = ref(0)
const tiltY = ref(0)
const imgLoaded = ref(false)
const illShadow = ref('0 18px 42px rgba(5,44,36,0.12)')

// subtle bob animation
let bobInterval = null
onMounted(() => {
  let t = 0
  bobInterval = setInterval(() => {
    t += 0.04
    bob.value = Math.sin(t) * 6 // vertical bob amplitude
  }, 16)

  // Wake-up check for cold start
  const timer = setTimeout(() => {
    isWakingUp.value = true
  }, 3000)
  axios.get(`${API_BASE_URL}/health`).catch(() => {}).finally(() => {
    clearTimeout(timer)
    isWakingUp.value = false
  })
})
onBeforeUnmount(() => {
  clearInterval(bobInterval)
})

// tilt calculation when user moves mouse over illustration
const onMouseMove = (e) => {
  const el = e.currentTarget
  const rect = el.getBoundingClientRect()
  const cx = rect.left + rect.width / 2
  const cy = rect.top + rect.height / 2
  const dx = e.clientX - cx
  const dy = e.clientY - cy
  tiltY.value = (dx / rect.width) * 8 // rotateY
  tiltX.value = -(dy / rect.height) * 6 // rotateX
}
const onLeave = () => {
  tiltX.value = 0
  tiltY.value = 0
}

// --- Login logic (unchanged, integrated) ---
const handleLogin = async () => {
  errorMessage.value = ''
  if (!email.value || !password.value || !selectedRole.value) {
    errorMessage.value = 'Please fill in email, password, and role.'
    return
  }
  isLoading.value = true
  try {
    const response = await axios.post(
      API_URL,
      { email: email.value, password: password.value, role: selectedRole.value },
      { headers: { 'Content-Type': 'application/json' }, withCredentials: true }
    )

    const user = response.data?.user
    const token = response.data?.token

    if (user) {
      try {
        localStorage.setItem('currentUser', JSON.stringify(user))
        if (token) {
          localStorage.setItem('authToken', token)
          axios.defaults.headers.common['Authentication-Token'] = token
        }
      } catch (storageError) {
        console.warn('Unable to cache user details locally', storageError)
      }

      const normalizedSelection = (response.data?.selected_role || selectedRole.value || '').toLowerCase()
      const userRoles = Array.isArray(user.roles) ? user.roles.map(r => (r || '').toLowerCase()) : []
      const employmentRole = (user.employment_role || '').toLowerCase()

      const canActAsRole = (roleName) => {
        switch ((roleName || '').toLowerCase()) {
          case 'hr': return userRoles.includes('hr')
          case 'manager': return employmentRole === 'manager' || userRoles.includes('manager') || userRoles.includes('hr')
          case 'employee': return employmentRole === 'employee' || userRoles.includes('hr')
          default: return false
        }
      }

      const resolveDefaultRole = () => {
        if (canActAsRole('hr')) return 'hr'
        if (canActAsRole('manager')) return 'manager'
        if (user) return 'employee'
        return null
      }

      const destinationByRole = { hr: 'HrDashboard', manager: 'ManagerDashboard', employee: 'EmployeeDashboard' }
      const finalizedRole = canActAsRole(normalizedSelection) ? normalizedSelection : resolveDefaultRole()
      const nextRouteName = destinationByRole[finalizedRole] || 'HomePage'

      try { localStorage.setItem(ROLE_STORAGE_KEY, finalizedRole || 'employee') } catch(e){ console.warn(e) }

      router.push({ name: nextRouteName })
      return
    }

    router.push({ name: 'HomePage' })
  } catch (error) {
    console.error('Login failed:', error)
    errorMessage.value = error.response?.data?.message || error.response?.data?.error || 'Invalid credentials.'
  } finally {
    isLoading.value = false
  }
}

const loginAsDemo = async (role) => {
  if (role === 'hr') {
    email.value = 'hr@example.com'
    password.value = 'hr123'
    selectedRole.value = 'hr'
  } else if (role === 'manager') {
    email.value = 'manager@example.com'
    password.value = 'manager123'
    selectedRole.value = 'manager'
  } else if (role === 'employee') {
    email.value = 'employee@example.com'
    password.value = 'employee123'
    selectedRole.value = 'employee'
  }
  await handleLogin()
}
</script>

<style scoped>
/* fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

:root{
  --bg-dark-1: #062f26;
  --bg-dark-2: #0b4335;
  --accent: #2ea78a;
  --glass: rgba(255,255,255,0.03);
}

/* page shell */
.page-shell{
  min-height:100vh;
  display:flex;
  align-items:center;
  justify-content:center;
  padding:28px;
  background: linear-gradient(180deg, var(--bg-dark-1), var(--bg-dark-2));
  font-family: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, Arial;
  color: #eaf6f1;
  position:relative;
  overflow:hidden;
}

/* background floating bubbles */
.bg-layer{ position:absolute; inset:0; pointer-events:none; z-index:0; }
.bubble{ position:absolute; border-radius:50%; background: rgba(255,255,255,0.03); filter: blur(12px); }
.b1{ width:260px; height:260px; left:6%; top:6%; animation: float1 18s infinite; }
.b2{ width:180px; height:180px; right:8%; top:14%; animation: float2 14s infinite; }
.b3{ width:140px; height:140px; left:22%; bottom:8%; animation: float3 16s infinite; }
.b4{ width:90px; height:90px; right:26%; bottom:22%; animation: float4 12s infinite; }
@keyframes float1 { 0% { transform: translateY(0) } 50% { transform: translateY(-18px) } 100% { transform: translateY(0) } }
@keyframes float2 { 0% { transform: translateY(0) } 50% { transform: translateY(-10px) } 100% { transform: translateY(0) } }
@keyframes float3 { 0% { transform: translateY(0) } 50% { transform: translateY(-14px) } 100% { transform: translateY(0) } }
@keyframes float4 { 0% { transform: translateY(0) } 50% { transform: translateY(-8px) } 100% { transform: translateY(0) } }

/* main card */
.card-frame{
  width:min(1120px, 96%);
  max-width:1120px;
  border-radius:22px;
  overflow:hidden;
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.02));
  box-shadow: 0 26px 90px rgba(2,10,6,0.6);
  display:flex;
  z-index:1;
  position:relative;
}

/* left panel (white area with organic SVG wave) */
.left-panel{
  position:relative;
  width:60%;
  min-width:520px;
  background: transparent;
  display:flex;
  align-items:center;
  justify-content:center;
  padding:42px 36px;
  color:#0a3b34;
}

/* left wave svg sits in background and gives the curved border shape */
.left-wave{
  position:absolute;
  left:0;
  top:0;
  z-index:0;
  width:100%;
  height:100%;
  pointer-events:none;
}

/* brand logo in top-left */
.brand-top{ position:absolute; left:28px; top:18px; z-index:3; transform: translateZ(0); }

/* illustration wrap with tilt + bob transform */
.illustration-wrap{
  z-index:2;
  width:100%;
  max-width:520px;
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:18px;
  transition: transform .18s ease-out;
  will-change: transform;
}

/* illustration card - looks like a glass panel with image centered */
.illustration-card{
  width:420px;
  max-width:86%;
  border-radius:16px;
  background: linear-gradient(180deg, #ffffff, #f6faf8);
  padding:30px 28px;
  display:flex;
  align-items:center;
  justify-content:center;
  position:relative;
  overflow:visible;
  transform-origin:center;
  transition: box-shadow .18s ease, transform .18s ease;
}

/* employee image: centered, responsive */
.employee-img{
  width:360px;
  height:auto;
  display:block;
  border-radius:12px;
  transition: transform .25s cubic-bezier(.2,.9,.2,1), filter .18s;
  will-change: transform;
  transform-origin:center;
  box-shadow: 0 12px 30px rgba(10,45,36,0.06);
}
.employee-img:hover{ transform: translateY(-6px) scale(1.02); filter: saturate(1.05); }

/* accent svg dots overlaid */
.accent-dots{ position:absolute; right:14px; top:12px; width:120px; height:120px; opacity:0.95; pointer-events:none; }

/* caption under illustration */
.illustration-caption{ text-align:center; margin-top:6px; color:#0e3f36; font-weight:700; }
.illustration-caption .sub{ font-weight:500; color:#2d6b5f; font-size:0.92rem; margin-top:6px; }

/* right panel (form) */
.right-panel{
  width:40%;
  min-width:380px;
  padding:40px 36px;
  background: linear-gradient(180deg, rgba(6,38,31,0.98), rgba(8,44,35,0.99));
  display:flex;
  align-items:center;
  justify-content:center;
  color: #eaf6f1;
}

/* form container */
.form-inner{ width:100%; max-width:330px; }

/* headings */
.heading{ margin:0 0 4px; font-size:1.6rem; font-weight:800; color:#f4fbf6; }
.subheading{ margin:0 0 14px; color: rgba(244,251,246,0.78); font-weight:500; }

/* form elements */
.form{ display:flex; flex-direction:column; gap:12px; margin-top:8px; }
.field{ display:flex; flex-direction:column; gap:6px; }
.field-label{ color: rgba(244,251,246,0.78); font-weight:600; font-size:0.92rem; }

/* inputs (frosted glass effect) */
.input{
  border-radius:12px;
  padding:12px 14px;
  border:none;
  background: rgba(255,255,255,0.03);
  color:#f1fbf6;
  outline:none;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
  transition: box-shadow .15s ease, transform .12s, border .12s;
  font-size:0.95rem;
  border: 1px solid rgba(255,255,255,0.04);
}
select.input option{ background:#fff; color:#08322a; }
.input::placeholder{ color: rgba(241,251,246,0.5); }

/* focus & hover micro-interactions */
.input:focus{ transform: translateY(-3px); box-shadow: 0 18px 40px rgba(5,44,36,0.18); border: 1px solid rgba(46,167,138,0.6); }

/* error text */
.error{ color:#ffb4b4; font-size:0.92rem; margin-top:2px; }

/* CTA button */
.cta{
  margin-top:6px;
  padding:12px 14px;
  width:100%;
  border-radius:999px;
  font-weight:700;
  background: linear-gradient(180deg, hwb(24 9% 0%));
  color:#dce4e3;
  border:none;
  cursor:pointer;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:10px;
  box-shadow: 0 12px 34px rgba(38, 27, 8, 0.17);
  transition: transform .12s ease, box-shadow .12s ease;
}
.cta:disabled{ opacity:0.7; cursor:not-allowed; transform:none; box-shadow:none; }
.cta:hover:not(:disabled){ transform: translateY(-3px); box-shadow: 0 22px 50px rgba(8,38,33,0.22); }

/* spinner */
.spinner{
  width:16px; height:16px;
  border-radius:50%;
  border:2px solid rgba(255,255,255,0.35);
  border-top-color: rgba(255,255,255,0.95);
  animation: spin .9s linear infinite;
}
@keyframes spin{ to { transform: rotate(360deg); } }

.wake-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(46, 167, 138, 0.15);
  border: 1px solid rgba(46, 167, 138, 0.4);
  color: #a7f3d0;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.82rem;
  margin-top: 14px;
}
.spinner-small {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid rgba(167, 243, 208, 0.35);
  border-top-color: #a7f3d0;
  animation: spin .9s linear infinite;
}
.demo-section {
  margin-top: 14px;
}
.demo-divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: rgba(244, 251, 246, 0.5);
  font-size: 0.78rem;
  margin-bottom: 10px;
}
.demo-divider::before,
.demo-divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.demo-divider span {
  padding: 0 8px;
}
.demo-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}
.demo-btn {
  padding: 8px 6px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.06);
  color: #eaf6f1;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}
.demo-btn:hover:not(:disabled) {
  background: rgba(46, 167, 138, 0.25);
  border-color: rgba(46, 167, 138, 0.5);
  transform: translateY(-1px);
}
.demo-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* helper row */
.helper-row{ display:flex; justify-content:space-between; align-items:center; margin-top:10px; gap:12px; }
.link-minor{ color: rgba(241,251,246,0.75); text-decoration:none; font-weight:600; font-size:0.92rem; }

/* legal row */
.legal-row{ margin-top:22px; display:flex; justify-content:space-between; align-items:center; color: rgba(241,251,246,0.44); font-size:0.82rem; }

/* responsive */
@media (max-width: 980px) {
  .card-frame{ flex-direction:column; border-radius:14px; }
  .left-panel, .right-panel{ width:100%; min-width:auto; padding:20px; }
  .left-wave{ display:none; }
  .employee-img{ width:80%; }
  .illustration-card{ width:92% }
  .form-inner{ max-width:540px; margin:0 auto; }
}

/* accessibility: reduce motion preference */
@media (prefers-reduced-motion: reduce) {
  .bg-layer .bubble, .employee-img, .illustration-wrap { animation: none !important; transition: none !important; }
  .employee-img:hover { transform: none !important; }
}
</style>
