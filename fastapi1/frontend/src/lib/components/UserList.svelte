<script lang="ts">
    import { onMount } from 'svelte';
    import { authStore } from '../stores/auth.svelte.js';

    let loading = $state(false);
    let error = $state(null);
    let users = $state<any[]>([]);
    let totalUsers = $state(0);
    let curPage = $state(1);
    let selectedResults = $state("10");
    let perPageResults = $derived(parseInt(selectedResults));
    let totalPages = $derived(totalUsers > 0 ? Math.ceil(totalUsers / perPageResults) : 1);
    let isPrevDisabled = $derived(curPage <= 1);
    let isNextDisabled = $derived(curPage >= totalPages);
    let searchTerm = $state("");
    
    let showForm = $state(false);
    let editingUser = $state<any>(null);
    let formData = $state({
        username: '',
        email: '',
        full_name: '',
        password: '',
        disabled: false
    });

    onMount(() => {
        fetchUsers();
    });

    async function fetchUsers() {
        loading = true;
        error = null;
        
        try {
            const response = await fetch(`http://10.120.1.21:8000/api/v1/users?perPage=${perPageResults}&curPage=${curPage}&searchTerm=${searchTerm}`);

            if (!response.ok) throw new Error('Failed to fetch');
            
            const totalCount = response.headers.get('X-Total-Count');
            if (totalCount) {
                totalUsers = parseInt(totalCount);
            }
            
            const data = await response.json();
            users = data.users;
        } catch (e) {
            error = e.message;
        } finally {
            loading = false;
        }
    }

    async function deleteUser(id) {
        if(confirm("Are you sure you want to delete?")) {
            try {
                const token = authStore.getToken();
                const response = await fetch(`http://10.120.1.21:8000/api/v1/users/${id}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (!response.ok) throw new Error('Failed to delete');
                
                fetchUsers();
            } catch (e) {
                error = e.message;
            }
        }
    }

    function openAddForm() {
        editingUser = null;
        formData = {
            username: '',
            email: '',
            full_name: '',
            password: '',
            disabled: false
        };
        showForm = true;
    }

    function openEditForm(user: any) {
        editingUser = user;
        formData = {
            username: user.username,
            email: user.email || '',
            full_name: user.full_name || '',
            password: '',
            disabled: user.disabled || false
        };
        showForm = true;
    }

    async function handleSubmit(e: Event) {
        e.preventDefault();
        loading = true;
        error = null;

        try {
            const token = authStore.getToken();
            const url = editingUser 
                ? `http://10.120.1.21:8000/api/v1/users/${editingUser.id}`
                : 'http://10.120.1.21:8000/api/v1/users/';
            
            const method = editingUser ? 'PUT' : 'POST';
            
            let payload: any = {
                username: formData.username,
                email: formData.email || null,
                full_name: formData.full_name || null,
                disabled: formData.disabled
            };
            
            if (!editingUser) {
                payload.password = formData.password;
            } else if (editingUser && formData.password) {
                payload.password = formData.password;
            } else {
                payload.hashed_password = editingUser.hashed_password;
            }

            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to save user');
            }

            showForm = false;
            fetchUsers();
        } catch (e) {
            error = e.message;
        } finally {
            loading = false;
        }
    }

    function goToPrevious() {
        if (curPage > 1) {
            curPage--;
            fetchUsers();
        }
    }
    
    function goToNext() {
        if (curPage < totalPages) {
            curPage++;
            fetchUsers();
        }
    }
    
    function goToPage(pageNum: number) {
        curPage = pageNum + 1;
        fetchUsers();
    }
    
    function handlePerPageChange() {
        curPage = 1; 
        fetchUsers();
    }

    function search(){
        curPage=1;
        fetchUsers();
    }
</script>

<div class="user-management">
    <div class="controls">
        <div class="search-box">
            <label>Search:</label>
            <input type="text" bind:value={searchTerm} oninput={search}>
        </div>
        
        <button class="btn-add" onclick={openAddForm}>+ Add User</button>
    </div>

    <div class="pagination-controls">
        <label for="perPage">Results per page: </label>
        <select id="perPage" bind:value={selectedResults} onchange={handlePerPageChange}>
            <option value="10">10</option>
            <option value="25">25</option>
            <option value="50">50</option>
            <option value="100">100</option>
        </select>
        
        <span class="total-info">Total Users: {totalUsers}</span>
    </div>

    {#if loading}
        <p>Loading Please wait</p>
    {:else if error}
        <p class="error">Error: {error}</p>
    {:else if users && users.length > 0}
        <table class="user-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Full Name</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {#each users as user}
                    <tr>
                        <td>{user.id}</td>
                        <td>{user.username}</td>
                        <td>{user.email || 'N/A'}</td>
                        <td>{user.full_name || 'N/A'}</td>
                        <td>
                            <span class="status {user.disabled ? 'inactive' : 'active'}">
                                {user.disabled ? 'Inactive' : 'Active'}
                            </span>
                        </td>
                        <td>
                            <button class="btn-edit" onclick={() => openEditForm(user)}>Edit</button>
                            <button class="btn-delete" onclick={() => deleteUser(user.id)}>Delete</button>
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>
    {:else}
        <p>No users found.</p>
    {/if}

    <div class="pagination">
        <button 
            class="pagination-btn" 
            onclick={goToPrevious} 
            disabled={isPrevDisabled}
        >
            Previous
        </button>
        
        <ul class="pagination-numbers">
            {#each Array(totalPages).fill(0) as _, i}
                <li class:active={curPage === i + 1}>
                    <button onclick={() => goToPage(i)}>{i + 1}</button>
                </li>
            {/each}
        </ul>
        
        <button 
            class="pagination-btn" 
            onclick={goToNext} 
            disabled={isNextDisabled}
        >
            Next
        </button>
    </div>
</div>

{#if showForm}
    <div class="modal-overlay" onclick={() => showForm = false}>
        <div class="modal" onclick={(e) => e.stopPropagation()}>
            <h2>{editingUser ? 'Edit User' : 'Add User'}</h2>
            <form onsubmit={handleSubmit}>
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" bind:value={formData.username} required />
                </div>
                
                <div class="form-group">
                    <label>Email:</label>
                    <input type="email" bind:value={formData.email} />
                </div>
                
                <div class="form-group">
                    <label>Full Name:</label>
                    <input type="text" bind:value={formData.full_name} />
                </div>
                
                <div class="form-group">
                    <label>Password: {editingUser ? '(leave blank to keep current)' : ''}</label>
                    <input 
                        type="password" 
                        bind:value={formData.password} 
                        required={!editingUser}
                        minlength="6"
                    />
                </div>
                
                <div class="form-group checkbox">
                    <label>
                        <input type="checkbox" bind:checked={formData.disabled} />
                        Account Disabled
                    </label>
                </div>
                
                {#if error}
                    <div class="form-error">{error}</div>
                {/if}
                
                <div class="form-actions">
                    <button type="submit" class="btn-save" disabled={loading}>
                        {loading ? 'Saving...' : 'Save'}
                    </button>
                    <button type="button" class="btn-cancel" onclick={() => showForm = false}>Cancel</button>
                </div>
            </form>
        </div>
    </div>
{/if}
