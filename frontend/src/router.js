import {createRouter, createWebHistory} from 'vue-router'
import axios from 'axios'


import HomeView from './views/HomeView.vue'
import LoginView from './views/LoginView.vue'
import RegisterView from './views/RegisterView.vue'
import ProfileView from './views/employee/profile/ProfileView.vue'
import EmployeeView from './views/employee/dashboard/EmployeeView.vue'
import ManagerView from './views/manager/dashboard/ManagerView.vue'
import HrdashboardView from './views/hr/dashboard/HrdashboardView.vue'
import HrSearch from './views/hr/search/HrSearch.vue'
import HrLetters from './views/hr/letters/HrLetters.vue'


const routes=[
    {name:'HomePage', path:'/', component: HomeView},
    {name:'LoginPage',path:'/login',component: LoginView},
    {name:'RegisterPage',path:'/register',component: RegisterView},
    {name:'ProfilePage', path:'/profile', component: ProfileView},
    {name:'EmployeeDashboard', path:'/employee/dashboard', component: EmployeeView, meta: { requiresAuth: true, employee: true }},
    {name:'ManagerDashboard', path:'/manager/dashboard', component: ManagerView, props: { mode: 'dashboard' }, meta: { requiresAuth: true, manager: true }},
    {name:'ManagerLeaves', path:'/manager/leaves', component: ManagerView, props: { mode: 'leaves' }, meta: { requiresAuth: true, manager: true }},
    { name: 'HrDashboard', path: '/hr/dashboard', alias: ['/superadmin'], component: HrdashboardView, meta: { requiresAuth: true, superAdmin: true } },
    { name: 'HrLetters', path: '/hr/letters', component: HrLetters, meta: { requiresAuth: true, superAdmin: true } },
    { name: 'HrSearch', path: '/hr/search', alias: ['/superadmin-search'], component: HrSearch, meta: { requiresAuth: true, superAdmin: true } },

    
]

const ROLE_STORAGE_KEY = 'activeUserRole'
const normalizeRoleSelection = (value) => {
    const role = (value || '').toLowerCase()
    if (role === 'admin') {
        return 'manager'
    }
    return role
}

const router = createRouter({
    routes:routes,
    history:createWebHistory()
})

// Cache user data to avoid repeated parsing
let cachedUser = null
let lastUserCheck = 0
const USER_CACHE_DURATION = 5000 // 5 seconds

const getCachedUser = () => {
    const now = Date.now()
    if (cachedUser && (now - lastUserCheck) < USER_CACHE_DURATION) {
        return cachedUser
    }
    
    const canUseStorage = typeof window !== 'undefined' && typeof window.localStorage !== 'undefined'
    if (!canUseStorage) {
        cachedUser = null
        lastUserCheck = now
        return null
    }

    const raw = localStorage.getItem('currentUser')
    if (!raw) {
        cachedUser = null
        lastUserCheck = now
        return null
    }
    
    try {
        cachedUser = JSON.parse(raw)
        lastUserCheck = now
        return cachedUser
    } catch (error) {
        console.warn('Unable to parse cached user', error)
        cachedUser = null
        lastUserCheck = now
        return null
    }
}

router.beforeEach((to, from, next) => {
    const user = getCachedUser()
    const roles = Array.isArray(user?.roles) ? user.roles : []
    const normalizedRoles = roles.map((role) => (role || '').toLowerCase())
    const employmentRole = (user?.employment_role || '').toLowerCase()
    const hrRouteNames = ['HrDashboard', 'HrSearch', 'HrLetters']
    const routeByRole = {
        hr: 'HrDashboard',
        manager: 'ManagerDashboard',
        employee: 'EmployeeDashboard',
    }

    // Pre-compute role checks for better performance
    const isSuperAdmin = normalizedRoles.includes('hr')
    const isAdmin = normalizedRoles.includes('manager')
    const isManagerByRole = employmentRole === 'manager'
    const isEmployeeByRole = employmentRole === 'employee'

    const canActAsRole = (roleName) => {
        const normalized = normalizeRoleSelection(roleName)
        switch (normalized) {
            case 'hr':
                return isSuperAdmin
            case 'manager':
                return isManagerByRole || isAdmin || isSuperAdmin
            case 'employee':
                return isEmployeeByRole || isSuperAdmin
            default:
                return false
        }
    }

    const determineActiveRole = () => {
        const canUseStorage = typeof window !== 'undefined' && typeof window.localStorage !== 'undefined'
        const storedRoleValue = canUseStorage ? localStorage.getItem(ROLE_STORAGE_KEY) : null
        const storedRole = normalizeRoleSelection(storedRoleValue)
        if (storedRole && canActAsRole(storedRole)) {
            return storedRole
        }
        const fallbackOrder = ['hr', 'manager', 'employee']
        for (const role of fallbackOrder) {
            if (canActAsRole(role)) {
                return role
            }
        }
        return null
    }

    const activeRole = determineActiveRole()
    const isActiveHr = activeRole === 'hr'
    const isActiveManager = activeRole === 'manager'
    const isActiveEmployee = activeRole === 'employee'

    const getRoleHomeRoute = () => {
        if (routeByRole[activeRole]) {
            return { name: routeByRole[activeRole] }
        }
        if (user) {
            return { name: 'HomePage' }
        }
        return { name: 'LoginPage', query: { redirect: to.fullPath } }
    }

    if (to.meta && to.meta.requiresAuth) {
        if (!user) {
            next({ name: 'LoginPage', query: { redirect: to.fullPath } })
            return
        }
        if (to.meta.superAdmin && !isActiveHr) {
            next(getRoleHomeRoute())
            return
        }
        if (to.meta.manager && !isActiveManager) {
            next(getRoleHomeRoute())
            return
        }
        if (to.meta.employee && !isActiveEmployee) {
            next(getRoleHomeRoute())
            return
        }
    }

    if (to.name === 'LoginPage') {
        const canUseStorage = typeof window !== 'undefined' && typeof window.localStorage !== 'undefined'
        if (canUseStorage) {
            localStorage.removeItem('currentUser')
            localStorage.removeItem('authToken')
            localStorage.removeItem(ROLE_STORAGE_KEY)
        }
        // Clear cache when logging out
        cachedUser = null
        lastUserCheck = 0
        delete axios.defaults.headers.common['Authentication-Token']
        next()
        return
    }

    if (to.name === 'EmployeeDashboard') {
        if (isActiveManager) {
            next({ name: 'ManagerDashboard' })
            return
        }
        if (isActiveHr) {
            next({ name: 'HrDashboard' })
            return
        }
    }

    if (hrRouteNames.includes(to.name) && !isActiveHr) {
        if (isActiveManager || isActiveEmployee) {
            next(getRoleHomeRoute())
            return
        }
        next({ name: 'LoginPage', query: { redirect: to.fullPath } })
        return
    }

    next()
})

export default router
