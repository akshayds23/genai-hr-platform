<script setup>
import { ref } from 'vue'

const items = [
  {
    question: 'Is it really free?',
    answer: 'Yes. The core workspace ships free so you can roll it out quickly.',
  },
  {
    question: 'How do we invite managers?',
    answer:
      'Add them as users, set their role, and they immediately see the manager dashboard without extra setup.',
  },
  {
    question: 'What if someone forgets a password?',
    answer:
      'Use the reset flow on the login page. Tokens expire quickly to keep access safe.',
  },
  {
    question: 'Can we customize letters and offers?',
    answer:
      'Yes. HR can edit templates, add variables, and generate letters with a couple of clicks.',
  },
  {
    question: 'Is our data secure?',
    answer:
      'Data is role-gated with audit-friendly logs. We keep authentication tokens short-lived and scoped.',
  },
  {
    question: 'Do you support approvals?',
    answer:
      'Manager and HR approval paths are built in for leaves, offers, and key changes.',
  },
]

const openItemIndex = ref(null)

const toggleItem = (index) => {
  openItemIndex.value = openItemIndex.value === index ? null : index
}
</script>

<template>
  <div
    id="faqs"
    class="text-slate-900 bg-white py-[72px] sm:py-24 bg-gradient-to-t from-[#eef3fb] to-white"
  >
    <div class="container">
      <h2 class="text-5xl font-bold tracking-tighter text-center sm:text-6xl">
        Frequently asked questions
      </h2>
      <div class="max-w-xl mx-auto">
        <p class="mt-5 text-xl text-center text-slate-700">
          Everything you need to know before rolling the workspace out to your
          team.
        </p>
      </div>
      <div class="max-w-2xl mx-auto mt-12">
        <div
          v-for="(item, index) in items"
          :key="index"
          class="border-b py-7 border-slate-200 cursor-pointer"
          @click="toggleItem(index)"
        >
          <div class="flex items-center justify-between mt-4">
            <h3 class="text-lg font-bold">{{ item.question }}</h3>
            <p class="text-2xl text-[#0f2738]" v-if="openItemIndex === index">-</p>
            <p class="text-2xl text-[#0f2738]" v-else>+</p>
          </div>
          <transition
            name="accordion"
            enter-active-class="transition-all duration-300 ease-out"
            leave-active-class="transition-all duration-300 ease-out"
          >
            <div
              v-show="openItemIndex === index"
              class="mt-4 text-slate-600 overflow-hidden"
            >
              {{ item.answer }}
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
#faqs {
  font-family: Inter, 'Golos Text', sans-serif;
}

.container {
  max-width: 1800px;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .container {
    padding: 0 0.5rem;
  }
}

.accordion-enter-from,
.accordion-leave-to {
  height: 0;
  opacity: 0;
  margin-top: 0;
}

.accordion-enter-to,
.accordion-leave-from {
  height: auto;
  opacity: 1;
  margin-top: 16px;
}
</style>
