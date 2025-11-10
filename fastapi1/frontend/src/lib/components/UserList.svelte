<script lang="ts">
    import { onMount } from 'svelte';
    import User from './User.svelte'; //Import our user component

    let loading = $state(false); //Controls whether or not the loading message is dispalyed or not
    let error = $state(null); //Controls if error message displayed
    
    let users: any[];
    let totalUsers = $state(0);
    let curPage = $state(1);
    let selectedResults = $state("10");
    let perPageResults = $derived(parseInt(selectedResults));
    let totalPages = $derived(totalUsers > 0 ? Math.ceil(totalUsers / perPageResults) : 1);
    let isPrevDisabled = $derived(curPage <= 1);
    let isNextDisabled = $derived(curPage >= totalPages);

    //When our page loads call fetch users
    onMount(() => {
		fetchUsers();
	});

    
    async function fetchUsers() {
        loading = true;
        error = null;
        
        try {
            const response = await fetch(`http://10.120.1.21:8000/api/v1/users?perPage=${perPageResults}&curPage=${curPage}`);

            if (!response.ok) throw new Error('Failed to fetch');
            
            const totalCount = response.headers.get('X-Total-Count');
            console.log('X-Total-Count header:', totalCount);
            if (totalCount) {
                totalUsers = parseInt(totalCount);
                console.log('Total users set to:', totalUsers);
            }
            
            const data = await response.json();
            users = data.users;
            console.log('Users fetched:', users.length, 'Total users:', totalUsers, 'Total pages:', totalPages);
        } catch (e) {
            error = e.message;
        } finally {
            loading = false;
        }
    }

    async function deleteUser(id) {
        if(confirm("Are you sure you want to delete?")) {
            try {
                const response = await fetch(`http://10.120.1.21:8000/api/v1/users/${id}`, {
                    method: 'DELETE',
                });
                
                if (!response.ok) throw new Error('Failed to delete');
                
            } catch (e) {
                error = e.message;
            } finally {
                // Refresh the list after deletion
                fetchUsers();
            }
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
    
    function goToPage(e: Event, pageNum: number) {
        e.preventDefault();
        curPage = pageNum + 1;
        fetchUsers();
    }
    
    function handlePerPageChange() {
        curPage = 1; 
        fetchUsers();
    }

</script>


<h1>Users</h1>
<!-- Pagination Controls - Results per page -->
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
    <p>Error {error} Please try to refresh</p>
{:else if users && users.length > 0}
    {#each users as user}
        <User 
            username={user.username} 
            full_name={user.full_name} 
            movies={user.movies} 
            email={user.email} 
            id={user.id}
            onDelete={deleteUser}
        />
    {/each}
{:else}
    <p>No users found.</p>
{/if}
<!-- Pagination Controls - Page Navigation -->
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
                <a href="#" onclick={(e) => goToPage(e, i)}>{i + 1}</a>
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

<button onclick={fetchUsers}>Refresh Users</button>
<style>
    .pagination-controls {
        margin: 20px 0;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .pagination-controls label {
        font-weight: bold;
    }
    
    .pagination-controls select {
        padding: 5px 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 14px;
    }
    
    .total-info {
        margin-left: auto;
        font-weight: bold;
        color: #555;
    }
    
    .pagination {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 20px 0;
    }
    
    .pagination-btn {
        padding: 8px 16px;
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
    }
    
    .pagination-btn:hover:not(:disabled) {
        background-color: #0056b3;
    }
    
    .pagination-btn:disabled {
        background-color: #ccc;
        cursor: not-allowed;
        opacity: 0.6;
    }
    
    .pagination-numbers {
        display: flex;
        list-style: none;
        padding: 0;
        margin: 0;
        gap: 5px;
    }
    
    .pagination-numbers li {
        display: inline-block;
    }
    
    .pagination-numbers li a {
        display: block;
        padding: 8px 12px;
        background-color: #f0f0f0;
        color: #333;
        text-decoration: none;
        border: 1px solid #ddd;
        border-radius: 4px;
        transition: background-color 0.2s;
    }
    
    .pagination-numbers li a:hover {
        background-color: #007bff;
        color: white;
    }
    
    .pagination-numbers li.active a {
        background-color: #007bff;
        color: white;
        font-weight: bold;
    }
</style>