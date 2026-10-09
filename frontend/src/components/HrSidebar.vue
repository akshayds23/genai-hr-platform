<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="brand-copy">
        <h1>{{ title }}</h1>
        <p class="tagline">{{ subtitle }}</p>
      </div>
    </div>
    
    <nav class="sidebar-nav">
      <button
        v-for="item in navItems"
        :key="item.value"
        class="nav-item"
        :class="{ active: activeTab === item.value }"
        type="button"
        @click="$emit('tab-change', item.value)"
      >
        {{ item.label }}
        <span v-if="item.badge && item.badge()" class="badge">{{ item.badge() }}</span>
      </button>
    </nav>
    
    <div class="sidebar-footer">
      <div class="user-chip">
        <span class="initials">{{ initials }}</span>
        <div class="user-info">
          <span class="name">{{ displayName }}</span>
          <span class="role">{{ userRole }}</span>
        </div>
      </div>
      <button class="logout-btn" type="button" @click="$emit('logout')">Logout</button>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'HrSidebar',
  props: {
    title: {
      type: String,
      default: 'Dashboard'
    },
    subtitle: {
      type: String,
      default: 'Control center'
    },
    navItems: {
      type: Array,
      required: true
    },
    activeTab: {
      type: String,
      required: true
    },
    displayName: {
      type: String,
      default: 'User'
    },
    userRole: {
      type: String,
      default: 'User'
    }
  },
  emits: ['tab-change', 'logout'],
  computed: {
    initials() {
      const parts = (this.displayName || '').trim().split(/\s+/)
      return parts.slice(0, 2).map((p) => p.charAt(0).toUpperCase()).join('') || 'U'
    }
  }
}
</script>

<style scoped>
.sidebar {
  width: 280px;
  min-height: 100vh;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.94), rgba(30, 64, 175, 0.88));
  color: #f8fafc;
  display: flex;
  flex-direction: column;
  box-shadow: 4px 0 20px rgba(15, 23, 42, 0.15);
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-copy h1 {
  font-size: 1.1rem;
  margin: 0;
  line-height: 1;
  color: #fff;
}

.brand-copy .tagline {
  margin: 4px 0 0;
  font-size: 0.8rem;
  color: rgba(226, 232, 240, 0.78);
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.4) transparent;
}

.sidebar-nav::-webkit-scrollbar {
  width: 6px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.45);
  border-radius: 999px;
}

.nav-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border: none;
  background: transparent;
  color: rgba(226, 232, 240, 0.92);
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  font-size: 0.95rem;
  text-align: left;
  width: 100%;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-left-color: rgba(255, 255, 255, 0.3);
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border-left-color: #fff;
  font-weight: 600;
}

.badge {
  min-width: 24px;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.22);
  font-size: 0.75rem;
  font-weight: 600;
  text-align: center;
  color: #fff;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 12px;
}

.initials {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #0f172a;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.05;
}

.user-info .name {
  font-weight: 600;
  color: #fff;
  font-size: 0.95rem;
}

.role {
  font-size: 0.78rem;
  color: rgba(226, 232, 240, 0.7);
}

.logout-btn {
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

@media (max-width: 880px) {
  .sidebar {
    width: 240px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
}
</style>
