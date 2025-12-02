<script lang="ts">
  import { onMount } from 'svelte';
  import { authStore } from '../src/lib/stores/auth.svelte.js';
  import { navigate } from '../router.js';

  interface UserData {
    id: number;
    username: string;
    email: string | null;
    full_name: string | null;
    disabled: boolean | null;
  }

  let user = $state<UserData | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let isEditing = $state(false);
  let isChangingPassword = $state(false);
  
  let editForm = $state({
    username: '',
    email: '',
    full_name: ''
  });

  let passwordForm = $state({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const API_URL = 'http://10.120.1.21:8000/api/v1';

  onMount(() => {
    if (!authStore.isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchCurrentUser();
  });

  async function fetchCurrentUser() {
    loading = true;
    error = null;

    try {
      const token = authStore.getToken();
      
      if (!token) {
        error = 'No authentication token found. Please login.';
        navigate('/login');
        return;
      }

      const response = await fetch(`${API_URL}/users/me/`, {
        headers: { 
          'Authorization': `Bearer ${token}` 
        }
      });

      if (!response.ok) {
        if (response.status === 401) {
          authStore.logout();
          navigate('/login');
          throw new Error('Authentication failed. Please login again.');
        }
        throw new Error('Failed to fetch user data');
      }

      const data: UserData = await response.json();
      user = data;
      
      editForm = {
        username: data.username,
        email: data.email || '',
        full_name: data.full_name || ''
      };
      
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
    } finally {
      loading = false;
    }
  }

  function startEditing() {
    isEditing = true;
    error = null;
  }

  function cancelEditing() {
    isEditing = false;
    if (user) {
      editForm = {
        username: user.username,
        email: user.email || '',
        full_name: user.full_name || ''
      };
    }
  }

  async function handleUpdateProfile(e: Event) {
    e.preventDefault();
    if (!user) return;
    
    loading = true;
    error = null;

    try {
      const token = authStore.getToken();
      
      const response = await fetch(`${API_URL}/users/${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          username: editForm.username,
          email: editForm.email || null,
          full_name: editForm.full_name || null
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update profile');
      }

      await fetchCurrentUser();
      isEditing = false;
      
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
    } finally {
      loading = false;
    }
  }

  async function handleChangePassword(e: Event) {
    e.preventDefault();
    if (!user) return;

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      error = 'New passwords do not match';
      return;
    }

    if (passwordForm.newPassword.length < 6) {
      error = 'Password must be at least 6 characters';
      return;
    }

    loading = true;
    error = null;

    try {
      const token = authStore.getToken();
      
      const formData = new FormData();
      formData.append('grant_type', "password");
      formData.append('username', user.username);
      formData.append('password', passwordForm.currentPassword);

      const verifyResponse = await fetch(`${API_URL}/users/token`, {
        method: 'POST',
        body: formData,
      });

      if (!verifyResponse.ok) {
        throw new Error('Current password is incorrect');
      }

      const updateResponse = await fetch(`${API_URL}/users/${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          password: passwordForm.newPassword
        })
      });

      if (!updateResponse.ok) {
        const errorData = await updateResponse.json();
        throw new Error(errorData.detail || 'Failed to update password');
      }

      passwordForm = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      };
      isChangingPassword = false;
      error = null;
      alert('Password changed successfully!');
      
    } catch (err) {
      error = err instanceof Error ? err.message : 'An error occurred';
    } finally {
      loading = false;
    }
  }
</script>

<div class="profile-container">
  {#if loading && !user}
    <div class="loading">
      <p>Loading your profile...</p>
    </div>
  {:else if error && !user}
    <div class="error-message">
      <h2>Error</h2>
      <p>{error}</p>
      <a href="#/login" class="btn-link">Go to Login</a>
    </div>
  {:else if user}
    <div class="profile-content">
      <h1>Welcome, {user.username}!</h1>
      
      {#if error}
        <div class="error-banner">
          {error}
        </div>
      {/if}

      <div class="profile-card">
        {#if isEditing}
          <form onsubmit={handleUpdateProfile} class="edit-form">
            <h2>Edit Profile</h2>
            
            <div class="form-group">
              <label>Username:</label>
              <input type="text" bind:value={editForm.username} required />
            </div>
            
            <div class="form-group">
              <label>Full Name:</label>
              <input type="text" bind:value={editForm.full_name} />
            </div>
            
            <div class="form-group">
              <label>Email:</label>
              <input type="email" bind:value={editForm.email} />
            </div>
            
            <div class="form-actions">
              <button type="submit" class="btn-save" disabled={loading}>
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
              <button type="button" class="btn-cancel" onclick={cancelEditing}>
                Cancel
              </button>
            </div>
          </form>
        {:else}
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

            <div class="button-group">
              <button class="btn-edit" onclick={startEditing}>Edit Profile</button>
              <button class="btn-password" onclick={() => isChangingPassword = !isChangingPassword}>
                Change Password
              </button>
            </div>
          </div>
        {/if}
      </div>

      {#if isChangingPassword}
        <div class="profile-card">
          <form onsubmit={handleChangePassword} class="password-form">
            <h2>Change Password</h2>
            
            <div class="form-group">
              <label>Current Password:</label>
              <input 
                type="password" 
                bind:value={passwordForm.currentPassword} 
                required 
              />
            </div>
            
            <div class="form-group">
              <label>New Password:</label>
              <input 
                type="password" 
                bind:value={passwordForm.newPassword} 
                required 
                minlength="6"
              />
            </div>
            
            <div class="form-group">
              <label>Confirm New Password:</label>
              <input 
                type="password" 
                bind:value={passwordForm.confirmPassword} 
                required 
                minlength="6"
              />
            </div>
            
            <div class="form-actions">
              <button type="submit" class="btn-save" disabled={loading}>
                {loading ? 'Changing...' : 'Change Password'}
              </button>
              <button 
                type="button" 
                class="btn-cancel" 
                onclick={() => {
                  isChangingPassword = false;
                  passwordForm = {currentPassword: '', newPassword: '', confirmPassword: ''};
                }}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      {/if}
    </div>
  {:else}
    <div class="no-user">
      <p>No user data available.</p>
      <a href="#/login" class="btn-link">Go to Login</a>
    </div>
  {/if}
</div>