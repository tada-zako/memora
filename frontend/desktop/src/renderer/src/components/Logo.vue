<template>
  <img
    class="transition-all duration-300 ease-in-out"
    :class="[{ invert: isDark }]"
    src="../assets/icon.png"
    alt="Memora Logo"
  />
</template>

<script setup lang="ts">
import { inject } from 'vue'

const isDark = inject<Boolean>('isDark', false)
</script>
