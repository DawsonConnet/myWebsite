<script lang="ts">
  import { onMount } from 'svelte';
  import { authStore } from '../src/lib/stores/auth.svelte.js';

  interface UserData {
    username: string;
    email: string | null;
    full_name: string | null;
    disabled: boolean | null;
  }

  let user = $state<UserData | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);

  const API_URL = 'http://10.120.1.21:8000/api/v1';

  onMount(() => {
    fetchCurrentUser();
  });

  async function fetchCurrentUser() {
    loading = true;
    error = null;

    try {
      const token = authStore.getToken();
      
      if (!token) {
        error = 'No authentication token found. Please login.';
        loading = false;
        return;
      }

      const response = await fetch(`${API_URL}/users/me/`, {
        headers: { 
          'Authorization': `Bearer ${token}` 
        }
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please login again.');
        }
        throw new Error('Failed to fetch user data');
      }

      const data: UserData = await response.json();
      user = data;
      
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
      // If authentication failed, logout
      if (err instanceof Error && err.message.includes('Authentication failed')) {
        authStore.logout();
      }
    } finally {
      loading = false;
    }
  }
</script>

<div class="profile-container">
  {#if loading}
    <div class="loading">
      <p>Loading your profile...</p>
    </div>
  {:else if error}
    <div class="error-message">
      <h2>Error</h2>
      <p>{error}</p>
      <a href="#/login" class="btn-link">Go to Login</a>
    </div>
  {:else if user}
    <div class="profile-content">
      <h1>Welcome, {user.username}!</h1>
      
      <div class="profile-card">
        <div class="profile-section">
          <h2>Profile Information</h2>
          
          <div class="info-row">
            <span class="info-label">Username:</span>
            <span class="info-value">{user.username}</span>
          </div>
          
          <div class="info-row">
            <span class="info-label">Full Name:</span>
            <span class="info-value">{user.full_name || 'Not provided'}</span>
          </div>
          
          <div class="info-row">
            <span class="info-label">Email:</span>
            <span class="info-value">{user.email || 'Not provided'}</span>
          </div>
          
          <div class="info-row">
            <span class="info-label">Status:</span>
            <span class="info-value status {user.disabled ? 'inactive' : 'active'}">
              {user.disabled ? 'Inactive' : 'Active'}
            </span>
          </div>
        </div>
      </div>
    </div>
  {:else}
    <div class="no-user">
      <p>No user data available.</p>
      <a href="#/login" class="btn-link">Go to Login</a>
    </div>
  {/if}
</div>