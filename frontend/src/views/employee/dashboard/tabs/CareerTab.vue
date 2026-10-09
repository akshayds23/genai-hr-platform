<template>
  <section
    class="rounded-[28px] border border-[#498528] 
           bg-[#DDEED1]  <!-- was bg-white/80 -->
           shadow-[0_24px_60px_rgba(73,133,40,0.18)]  <!-- tinted towards green -->
           backdrop-blur-xl"
  >
    <!-- HEADER -->
    <div
      class="flex items-start justify-between gap-4 border-b border-[#498528]/30 
             px-6 py-4 bg-gradient-to-r from-slate-50/80 via-white to-emerald-50/70"
    >
      <div>
        <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
          Growth
        </p>
        <h2 class="text-lg font-semibold text-slate-900">Career path planner</h2>
        <p class="text-sm text-slate-500">
          Share your growth goals to get personalised guidance
        </p>
      </div>
      <button
        class="flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 
               text-slate-400 text-lg leading-none transition-all 
               hover:bg-slate-50 hover:text-slate-600"
        type="button"
        @click="ctx.resetCareerForm"
      >
        −
      </button>
    </div>

    <!-- FORM -->
    <form
      class="space-y-4 px-6 py-6"
      @submit.prevent="ctx.submitCareerForm"
    >
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label class="block space-y-2 text-sm">
          <span class="font-medium text-slate-700">Current role</span>
          <input
            v-model="ctx.careerForm.current_role"
            type="text"
            class="w-full rounded-2xl border border-slate-200 bg-white/80 px-3 py-2 
                   text-sm text-slate-700 shadow-sm 
                   focus:border-emerald-400 focus:outline-none 
                   focus:ring-2 focus:ring-emerald-500/30"
          >
        </label>
        <label class="block space-y-2 text-sm">
          <span class="font-medium text-slate-700">Target role</span>
          <input
            v-model="ctx.careerForm.target_role"
            type="text"
            class="w-full rounded-2xl border border-slate-200 bg-white/80 px-3 py-2 
                   text-sm text-slate-700 shadow-sm 
                   focus:border-emerald-400 focus:outline-none 
                   focus:ring-2 focus:ring-emerald-500/30"
          >
        </label>
      </div>

      <label class="block space-y-2 text-sm">
        <span class="font-medium text-slate-700">Strengths</span>
        <textarea
          v-model="ctx.careerForm.strengths"
          rows="2"
          class="w-full rounded-2xl border border-slate-200 bg-white/80 px-3 py-2 
                 text-sm text-slate-700 shadow-sm 
                 focus:border-emerald-400 focus:outline-none 
                 focus:ring-2 focus:ring-emerald-500/30"
        ></textarea>
      </label>

      <label class="block space-y-2 text-sm">
        <span class="font-medium text-slate-700">Focus areas</span>
        <textarea
          v-model="ctx.careerForm.focus_areas"
          rows="2"
          class="w-full rounded-2xl border border-slate-200 bg-white/80 px-3 py-2 
                 text-sm text-slate-700 shadow-sm 
                 focus:border-emerald-400 focus:outline-none 
                 focus:ring-2 focus:ring-emerald-500/30"
        ></textarea>
      </label>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label class="block space-y-2 text-sm">
          <span class="font-medium text-slate-700">Preferred learning style</span>
          <select
            v-model="ctx.careerForm.learning_style"
            class="w-full rounded-2xl border border-slate-200 bg-white/80 px-3 py-2 
                   text-sm text-slate-700 shadow-sm 
                   focus:border-emerald-400 focus:outline-none 
                   focus:ring-2 focus:ring-emerald-500/30"
          >
            <option value="online">Online courses</option>
            <option value="mentorship">Mentorship</option>
            <option value="project">Project-based assignments</option>
            <option value="certification">Certification bootcamps</option>
            <option value="blended">A blended approach</option>
          </select>
        </label>
        <label class="block space-y-2 text-sm">
          <span class="font-medium text-slate-700">Timeline</span>
          <select
            v-model="ctx.careerForm.timeline"
            class="w-full rounded-2xl border border-slate-200 bg-white/80 px-3 py-2 
                   text-sm text-slate-700 shadow-sm 
                   focus:border-emerald-400 focus:outline-none 
                   focus:ring-2 focus:ring-emerald-500/30"
          >
            <option value="0-3">0-3 months</option>
            <option value="3-6">3-6 months</option>
            <option value="6-12">6-12 months</option>
            <option value="12+">12+ months</option>
          </select>
        </label>
      </div>

      <label class="block space-y-2 text-sm">
        <span class="font-medium text-slate-700">What support would help most?</span>
        <textarea
          v-model="ctx.careerForm.guidance_goal"
          rows="3"
          class="w-full rounded-2xl border border-slate-200 bg-white/80 px-3 py-2 
                 text-sm text-slate-700 shadow-sm 
                 focus:border-emerald-400 focus:outline-none 
                 focus:ring-2 focus:ring-emerald-500/30"
          placeholder="Mention projects, mentors, or skills you would like to explore"
        ></textarea>
      </label>

      <p
        v-if="ctx.careerFormError"
        class="text-sm font-medium text-rose-600"
      >
        {{ ctx.careerFormError }}
      </p>

      <div class="flex justify-end gap-3">
        <button
          class="rounded-full border border-slate-200 bg-white/80 px-4 py-2 
                 text-sm font-semibold text-slate-600 
                 transition hover:bg-slate-50"
          type="button"
          @click="ctx.resetCareerForm"
        >
          Clear
        </button>
        <button
          class="rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold 
                 text-white shadow-md transition 
                 hover:bg-emerald-700 hover:shadow-lg 
                 disabled:cursor-not-allowed disabled:opacity-60"
          type="submit"
          :disabled="ctx.submittingCareerForm"
        >
          {{ ctx.submittingCareerForm ? 'Submitting...' : 'Share goals' }}
        </button>
      </div>
    </form>

    <!-- RECOMMENDATION PANEL -->
    <div v-if="ctx.showCareerRecommendation" class="px-6 pb-6">
      <div
        class="rounded-2xl border border-[#498528]/30 bg-[#DDEED1]/70 p-4"
      >
        <div class="mb-4 flex items-start justify-between">
          <h3 class="font-semibold text-[#2F4C1C]">
            Personalised recommendation
          </h3>
          <div class="flex items-center gap-2">
            <button
              class="text-sm text-slate-600 hover:text-slate-800"
              type="button"
              @click="ctx.showCareerRecommendation = false"
            >
              Close
            </button>
            <button
              class="rounded-full border border-slate-300 bg-white px-3 py-1 
                     text-sm font-semibold text-slate-900 transition 
                     hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
              type="button"
              @click="ctx.downloadCareerPdf"
              :disabled="ctx.downloadingCareerPdf"
            >
              {{ ctx.downloadingCareerPdf ? 'Downloading...' : 'Download PDF' }}
            </button>
          </div>
        </div>

        <div
          class="career-recommendation rounded-2xl bg-white p-6 shadow-sm
                text-left leading-relaxed whitespace-pre-line"
          v-html="formattedRecommendation"
        ></div>
      </div>
    </div>
  </section>
</template>



<style scoped>
.career-recommendation {
  color: #334155;
  line-height: 1.75;
}

.career-recommendation :deep(h3) {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  text-align: left;
}

.career-recommendation :deep(h3:first-child) {
  margin-top: 0;
}

.career-recommendation :deep(p) {
  margin-bottom: 1rem;
  color: #475569;
  text-align: left;
}

.career-recommendation :deep(strong) {
  font-weight: 600;
  color: #1e293b;
}

.career-recommendation :deep(ul),
.career-recommendation :deep(ol) {
  margin-bottom: 1rem;
  padding-left: 1.5rem;
  text-align: left;
}

.career-recommendation :deep(li) {
  margin-bottom: 0.5rem;
  color: #475569;
  line-height: 1.625;
  text-align: left;
}

.career-recommendation :deep(ul) {
  list-style-type: disc;
  list-style-position: outside;
}

.career-recommendation :deep(ol) {
  list-style-type: decimal;
  list-style-position: outside;
}

.career-recommendation :deep(ul ul) {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  padding-left: 1.5rem;
}

.career-recommendation :deep(li::marker) {
  color: #64748b;
}
</style>

<script>
export default {
  name: 'CareerTab',
  inject: ['employeeDashboardContext'],
  computed: {
    ctx() {
      return this.employeeDashboardContext;
    },
    formattedRecommendation() {
      if (!this.ctx.careerRecommendation) return '';
      
      // Convert markdown to clean HTML without visible markdown symbols
      let html = this.ctx.careerRecommendation;
      
      // Convert headers (standalone **text** or **text:**) - remove asterisks
      html = html.replace(
        /^\*\*([^*]+)\*\*:?$/gm,
        '<h3 class="text-lg font-bold text-slate-900 mt-6 mb-3">$1</h3>'
      );
      
      // Convert inline bold text **text** - remove asterisks
      html = html.replace(
        /\*\*([^*]+)\*\*/g,
        '<strong class="font-semibold text-slate-900">$1</strong>'
      );

      // 🔹 NEW: Convert *single-star* emphasis to bold
      // This catches things like *Fast.ai “Practical Deep Learning for Coders”*
      html = html.replace(
        /\*([^*\n]+)\*/g,
        '<strong class="font-semibold text-slate-900">$1</strong>'
      ); // ⬅️ NEW
      
      // Convert bullet points starting with * or - (markdown style)
      html = html.replace(
        /^(\s*)[*-]\s+(.+)$/gm,
        (match, indent, content) => {
          return `<li class="text-slate-700 leading-relaxed">${content}</li>`;
        }
      );

      // 🔹 NEW: Convert bullet points starting with "•" (Unicode bullet)
      html = html.replace(
        /^(\s*)[•]\s+(.+)$/gm,
        (match, indent, content) => {
          return `<li class="text-slate-700 leading-relaxed">${content}</li>`;
        }
      ); // ⬅️ NEW
      
      // Wrap consecutive list items in ul tags
      html = html.replace(
        /(<li[^>]*>.*?<\/li>\s*)+/gs,
        '<ul class="list-disc list-inside space-y-2 mb-4">$&</ul>'
      );
      
      // Convert numbered lists - keep numbers but format cleanly
      html = html.replace(
        /^(\d+)\.\s+(.+)$/gm,
        '<li class="text-slate-700 leading-relaxed" value="$1">$2</li>'
      );
      html = html.replace(
        /(<li[^>]*value="\d+"[^>]*>.*?<\/li>\s*)+/gs,
        (match) => {
          return `<ol class="list-decimal list-inside space-y-2 mb-4 ml-4">${match}</ol>`;
        }
      );
      
      // Convert paragraphs (double newlines)
      html = html
        .split(/\n\n+/)
        .map((para) => {
          para = para.trim();
          if (!para) return '';
          if (
            para.startsWith('<h') ||
            para.startsWith('<ul') ||
            para.startsWith('<ol') ||
            para.startsWith('<li')
          ) {
            return para;
          }
          return `<p class="text-slate-700 leading-relaxed mb-4">${para}</p>`;
        })
        .join('\n');
      
      // Convert single newlines to <br> within paragraphs
      html = html.replace(
        /<p([^>]*)>([^<]*(?:<(?!\/p>)[^<]*)*)<\/p>/g,
        (match, attrs, content) => {
          const formatted = content.replace(/\n/g, '<br>');
          return `<p${attrs}>${formatted}</p>`;
        }
      );
      
      // Clean up extra spaces and newlines
      html = html.replace(/\n\s*\n/g, '\n');
      
      return html;
    },
  },
};
</script>
