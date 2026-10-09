<template>
  <span class="inline-flex items-center justify-center">
    <component
      :is="iconComponent"
      class="h-5 w-5"
      aria-hidden="true"
    />
  </span>
</template>

<script>
import {
  ArrowTrendingUpIcon,
  CalendarDaysIcon,
  ChartBarIcon,
  ChatBubbleOvalLeftEllipsisIcon,
  CheckCircleIcon,
  CircleStackIcon,
  BellAlertIcon,
  DocumentTextIcon,
  EnvelopeOpenIcon,
  FlagIcon,
  FolderIcon,
  GiftIcon,
  HomeIcon,
  LifebuoyIcon,
  PencilSquareIcon,
  QuestionMarkCircleIcon,
  SparklesIcon,
  UsersIcon,
} from '@heroicons/vue/24/outline'
import PersonExitIcon from '@/components/PersonExitIcon.vue'

const ICON_MAP = {
  overview: HomeIcon,
  projects: FolderIcon,
  team: UsersIcon,
  people: UsersIcon,
  userManagement: UsersIcon,
  users: UsersIcon,
  leave: CalendarDaysIcon,
  support: LifebuoyIcon,
  chatbot: SparklesIcon,
  career: ArrowTrendingUpIcon,
  feedback: ChatBubbleOvalLeftEllipsisIcon,
  notifications: BellAlertIcon,
  faqs: QuestionMarkCircleIcon,
  resign: PersonExitIcon,
  leaveInsights: ChartBarIcon,
  approvals: CheckCircleIcon,
  questions: QuestionMarkCircleIcon,
  resumes: DocumentTextIcon,
  jdMaker: PencilSquareIcon,
  letters: EnvelopeOpenIcon,
  birthdays: GiftIcon,
  offboarding: FlagIcon,
  default: CircleStackIcon,
}

export default {
  name: 'SidebarIcon',
  props: {
    name: {
      type: String,
      required: true,
    },
  },
  computed: {
    iconComponent() {
      return ICON_MAP[this.name] || ICON_MAP.default
    },
  },
}
</script>
