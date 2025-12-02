<script lang="ts">
  import { authStore } from '../src/lib/stores/auth.svelte.js';
  import UserList from '../src/lib/components/UserList.svelte';
  import MovieList from '../src/lib/components/MovieList.svelte';
  import ServiceList from '../src/lib/components/ServiceList.svelte';

  let selectedModel = $state('users');
  let isAuthenticated = $state(false);

  $effect(() => {
    isAuthenticated = authStore.isAuthenticated;
  });

  function selectModel(model: string) {
    selectedModel = model;
  }
</script>

{#if !isAuthenticated}
  <div class="unauthorized">
    <h1>403 - Unauthorized</h1>
    <p>You must be logged in to access the admin dashboard.</p>
    <a href="#/login" class="btn-login">Go to Login</a>
  </div>
{:else}
  <div class="admin-container">
    <aside class="sidebar">
      <h2>Admin Dashboard</h2>
      <nav class="sidebar-nav">
        <button 
          class="nav-item {selectedModel === 'users' ? 'active' : ''}"
          onclick={() => selectModel('users')}
        >
          Users
        </button>
        <button 
          class="nav-item {selectedModel === 'movies' ? 'active' : ''}"
          onclick={() => selectModel('movies')}
        >
          Movies
        </button>
        <button 
          class="nav-item {selectedModel === 'services' ? 'active' : ''}"
          onclick={() => selectModel('services')}
        >
          Services
        </button>
      </nav>
    </aside>

    <main class="admin-main">
      {#if selectedModel === 'users'}
        <h1>Manage Users</h1>
        <UserList />
      {:else if selectedModel === 'movies'}
        <h1>Manage Movies</h1>
        <MovieList />
      {:else if selectedModel === 'services'}
        <h1>Manage Services</h1>
        <ServiceList />
      {/if}
    </main>
  </div>
{/if}