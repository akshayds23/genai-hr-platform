<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
/* global defineOptions */
defineOptions({ name: 'LandingPageFooter' })
import { ref } from 'vue'
import logo from '@/assets/alveon-logo.svg'

const currentYear = new Date().getFullYear()

const footerLinks = {
  product: {
    title: 'Product',
    links: [
      { name: 'Features', id: 'features', type: 'anchor' },
      { name: 'Product Showcase', id: 'product', type: 'anchor' },
      { name: 'Testimonials', id: 'testimonials', type: 'anchor' },
      { name: 'FAQs', id: 'faqs', type: 'anchor' },
    ],
  },
}

const activeSection = ref('')

const handleScroll = (link) => {
  if (link.type === 'external') {
    window.open(link.id, '_blank', 'noopener')
    return
  }
  const element = document.getElementById(link.id)
  if (element) {
    const offset = element.offsetTop - 20
    window.scrollTo({
      top: offset,
      behavior: 'smooth',
    })
    activeSection.value = link.id
  }
}
</script>

<template>
  <footer class="relative bg-[#052659] text-white overflow-hidden">
    <div class="container">
      <div class="relative container pb-14 px-6 sm:px-16">
        <div
          class="flex sm:flex-row flex-col justify-between items-start gap-8 py-2 pb-10"
        >
          <div class="flex items-center gap-4">
            <div class="bg-[#073773] shadow-sm rounded-full p-3 border border-white/10">
              <img
                class="w-[72px] h-[72px]"
                :src="logo"
                alt="Brand logo"
              />
            </div>
            <div>
              <p class="text-sm uppercase tracking-[0.3em] text-slate-300">Alveon</p>
              <p class="text-slate-200 max-w-md">
                Build HR experiences that feel modern, kind, and reliable for every team.
              </p>
            </div>
          </div>

          <div class="flex justify-between sm:w-[30%] w-full">
            <div
              v-for="(section, key) in footerLinks"
              :key="key"
              class="space-y-6 px-2"
            >
              <h4 class="font-bold text-lg text-white">{{ section.title }}</h4>
              <ul class="space-y-4">
                <li v-for="link in section.links" :key="link.name">
                  <button
                    @click="handleScroll(link)"
                    class="text-slate-200 hover:text-white flex items-center gap-2 transition-colors group"
                  >
                    <span
                      class="inline-flex h-2 w-2 rounded-full bg-slate-400 group-hover:bg-white"
                    ></span>
                    {{ link.name }}
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="pt-8 flex flex-col md:flex-row justify-start items-center gap-4">
          <div class="gradient-text">ALVEON</div>
          <div class="flex items-center gap-2 sm:mb-14 mb-32">
            <span class="text-slate-200"
              >(c) {{ currentYear }}. Built to keep people work simple and bold.</span
            >
          </div>
        </div>

        <div
          class="absolute bottom-16 sm:bottom-4 text-slate-300 text-sm text-center hover:text-white transition-colors easter"
        >
          Crafted with focus, caffeine, and a lot of empathy for HR teams.
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.container {
  max-width: 1800px;
  margin: 0 auto;
}

img {
  user-select: none;
  pointer-events: none;
}

/* Updated to match dark background */
.gradient-text {
  background: linear-gradient(70deg, #ffffffcc, #7fb6ff, #bcd9ff);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-family: 'Golos Text', 'Instrument Serif', serif;
  font-size: 230px;
  position: absolute;
  right: -20px;
  bottom: -140px;
  user-select: none;
  pointer-events: none;
  opacity: 0.08;
}

@media (max-width: 768px) {
  .gradient-text {
    font-size: 145px;
    left: 0px;
    bottom: -150px;
  }

  footer {
    padding-bottom: 120px;
  }

  .easter {
    right: 2px;
  }
}

button {
  position: relative;
  width: fit-content;
  cursor: pointer;
}

/* underline hover */
button::after {
  content: '';
  position: absolute;
  width: 0;
  height: 2.2px;
  bottom: -2.2px;
  left: 0;
  background: linear-gradient(to right, #ffffff, #7fb6ff);
  transition: width 0.3s ease;
}

button:hover::after {
  width: 100%;
}

input:focus {
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.25);
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

footer::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.15),
    transparent
  );
}

.easter {
  font-family: Inter, 'Golos Text', sans-serif;
  font-size: 18px;
  transition: all 0.3s ease;
}

.easter:hover {
  color: #ffffff;
}
</style>
