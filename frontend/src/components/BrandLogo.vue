<template>
  <div :class="brandClasses">
    <img :src="logoSrc" alt="Alveon logo mark" class="brand-logo__icon" />
    <span v-if="!props.hideText" class="brand-logo__text">ALVEON</span>
  </div>
</template>

<script setup>
/* global defineProps */
import { computed } from 'vue'
import logoSrc from '@/assets/alveon-logo.svg'

const props = defineProps({
  size: {
    type: String,
    default: 'md', // sm, md, lg
  },
  stacked: {
    type: Boolean,
    default: false,
  },
  muted: {
    type: Boolean,
    default: false,
  },
  hideText: {
    type: Boolean,
    default: false,
  },
})

const brandClasses = computed(() => ({
  'brand-logo': true,
  [`brand-logo--${props.size}`]: true,
  'brand-logo--stacked': props.stacked,
  'brand-logo--muted': props.muted,
}))
</script>

<style scoped>
.brand-logo {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  font-family: 'Inter', 'Segoe UI', sans-serif;
  font-weight: 700;
  color: #000;
  text-transform: uppercase;
  letter-spacing: 0.24em;
}

.brand-logo--stacked {
  flex-direction: column;
  gap: 0.4rem;
  letter-spacing: 0.18em;
}

.brand-logo--muted {
  color: rgba(255, 255, 255, 0.92);
}

.brand-logo__icon {
  display: block;
  width: 52px;
  height: 52px;
}

.brand-logo--sm .brand-logo__icon {
  width: 36px;
  height: 36px;
}

.brand-logo--lg .brand-logo__icon {
  width: 68px;
  height: 68px;
}

.brand-logo__text {
  font-size: 1.25rem;
  letter-spacing: 0.2em;
}

.brand-logo--sm .brand-logo__text {
  font-size: 0.95rem;
  letter-spacing: 0.18em;
}

.brand-logo--lg .brand-logo__text {
  font-size: 1.6rem;
  letter-spacing: 0.26em;
}

.brand-logo--muted .brand-logo__icon {
  opacity: 0.92;
}
</style>
