<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
</script>

<template>
  <div class="app-layout">
    <nav class="navbar">
      <div class="container navbar-content">
        <RouterLink to="/" class="navbar-brand">
          <span class="brand-icon">🏥</span>
          PA Co-Pilot
        </RouterLink>
        <div class="navbar-nav">
          <RouterLink to="/" class="nav-link">
            <span class="nav-icon">📋</span> Cases
          </RouterLink>
          <RouterLink to="/metrics" class="nav-link">
            <span class="nav-icon">📊</span> Metrics
          </RouterLink>
        </div>
        <span class="navbar-text">
          🛡️ AI-Powered Clinical Decision Support
        </span>
      </div>
    </nav>

    <div v-if="appStore.demoMode" class="demo-banner">
      <div class="container">
        <span class="info-icon">ℹ️</span>
        <strong>Demo Mode:</strong> Running with simulated AI responses. Add your OpenAI API key for full AI-powered analysis.
      </div>
    </div>

    <main class="main-content container">
      <slot></slot>
    </main>

    <footer class="footer">
      <div class="container text-center">
        <small>PA Co-Pilot - AI Clinical Decision Support System | For demonstration purposes only</small>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.navbar-brand {
  font-weight: 700;
  font-size: 1.4rem;
  color: white;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.brand-icon {
  font-size: 1.5rem;
}

.navbar-nav {
  display: flex;
  gap: 1rem;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: white;
  background-color: rgba(255, 255, 255, 0.1);
}

.navbar-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
}

.demo-banner {
  background-color: #cff4fc;
  border-bottom: 1px solid #b6effb;
  color: #055160;
  padding: 0.75rem 0;
}

.info-icon {
  margin-right: 0.5rem;
}

.main-content {
  flex: 1;
  padding: 2rem 1rem;
}

.footer {
  background-color: #212529;
  color: #adb5bd;
  padding: 1rem 0;
  margin-top: auto;
}
</style>
