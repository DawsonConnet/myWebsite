<script lang="ts">
  import { authStore } from '../src/lib/stores/auth.svelte.js';

  interface Token {
    access_token: string;
    token_type: string;
  }

  interface LoginError {
    detail: string;
  }

  let isLoggedIn = $state(false);
  let username = $state('');
  let password = $state('');
  let loading = $state(false);
  let error = $state<string | null>(null);
  let token = $state<Token | null>(null);
 
  const API_URL = 'http://10.120.1.21:8000/api/v1';

  $effect(() => {
    isLoggedIn = authStore.isAuthenticated;
  });

  async function handleSubmit(e: Event) {
    e.preventDefault();
    loading = true;
    error = null;
    token = null;

    try {
      const formData = new FormData();
      formData.append('grant_type', "password");
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch(`${API_URL}/users/token`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData: LoginError = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data: Token = await response.json();
      token = data;
      
      authStore.login(data.access_token, null);
      
      username = '';
      password = '';
      
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
    } finally {
      loading = false;
    }
  }

  function logout() {
    token = null;
    authStore.logout();
  }
</script>

<div class="login-container">
  <h1>Login</h1>
  
  {#if token}
    <div class="success-message">
      <h2>Login Successful!</h2>
      <p><strong>Token Type:</strong> {token.token_type}</p>
      <p><strong>Access Token:</strong> {token.access_token.substring(0, 50)}...</p>
      <button onclick={logout} class="btn-logout">Logout</button>
      <p><a href="#/profile">Go to Profile</a></p>
    </div>
  {:else}
    <form onsubmit={handleSubmit} class="login-form">
      <div class="form-group">
        <label for="username">Username:</label>
        <input 
          type="text" 
          id="username" 
          bind:value={username}
          disabled={loading}
          required
          placeholder="Enter your username"
        />
      </div>

      <div class="form-group">
        <label for="password">Password:</label>
        <input 
          type="password" 
          id="password" 
          bind:value={password}
          disabled={loading}
          required
          placeholder="Enter your password"
        />
      </div>

      {#if error}
        <div class="error-message">
          {error}
        </div>
      {/if}

      <button 
        type="submit" 
        class="btn-submit" 
        disabled={loading}
      >
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  {/if}
</div>
