<template>
  <div id="app" class="min-h-screen bg-gradient-to-br from-blue-900 to-indigo-900 text-gray-900 flex flex-col">
    <nav class="flex justify-between items-center p-4 bg-gray-100">
      <img
        alt="Vue logo"
        src="./assets/logo.png"
        class="h-8 sm:h-10 md:h-12"
      >
      <div class="flex items-center">
        <div
          @click="openSignUpModal"
          class="flex flex-col items-center cursor-pointer group"
        >
          <i class="fas fa-user-circle text-xl sm:text-2xl"></i>
          <span class="text-xs mt-1 group-hover:text-blue-600 hidden md:block lg:block">
            Se connecter
          </span>
        </div>
      </div>
    </nav>
    <h1 class="text-2xl sm:text-3xl md:text-4xl font-bold mt-8 sm:mt-12 md:mt-16 text-center text-white px-4">
      Bienvenue sur la plateforme NoMask
    </h1>
    <SignUp v-if="showSignUpModal" @close="closeSignUpModal" />
  </div>
</template>

<script>
import SignUp from './components/SignUp.vue';

export default {
  name: 'App',
  components: {
    SignUp,
  },
  data() {
    return {
      showSignUpModal: false,
    };
  },
  methods: {
    openSignUpModal() {
      this.showSignUpModal = true;
    },
    closeSignUpModal() {
      this.showSignUpModal = false;
    },
  },
};
</script>