<template>
  <div class="collapsible-group" :class="{ collapsed: !open }">
    <div
      class="collapsible-header"
      role="button"
      tabindex="0"
      :aria-expanded="open"
      @click="toggle"
      @keydown.enter.prevent="toggle"
      @keydown.space.prevent="toggle"
    >
      <div class="collapsible-title">
        <span class="collapsible-title-text">{{ title }}</span>
        <slot name="title-extra"></slot>
      </div>
      <div class="collapsible-summary" v-if="!open">
        <slot name="summary">
          <span>{{ summary }}</span>
        </slot>
      </div>
      <div class="collapsible-actions">
        <slot name="actions"></slot>
        <span class="collapsible-toggle">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </span>
      </div>
    </div>
    <transition name="collapse">
      <div v-show="open" class="collapsible-body">
        <slot></slot>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  summary?: string;
  open: boolean;
}>();

const emit = defineEmits<{
  (e: 'toggle'): void;
}>();

function toggle() {
  emit('toggle');
}
</script>
