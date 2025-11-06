<script lang="ts">
    import { onMount } from 'svelte';
    import User from './User.svelte'; //Import our user component

    let loading = $state(false); //Controls whether or not the loading message is dispalyed or not
    let error = $state(null); //Controls if error message displayed
    
    let users: any[];
    //could also be this javascript
    //let users = [];

    //When our page loads call fetch users
    onMount(() => {
		fetchUsers();
	});

    
    async function fetchUsers() {
        loading = true; //Tell user we're loading! Notice that this will automatically update on becaause it's reactive.
        error = null;
        
        try {
            //Your url may be different than mine
            const response = await fetch('http://10.120.1.21:8000/api/v1/users');

            if (!response.ok) throw new Error('Failed to fetch');
                users = await response.json();
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

</script>


<h1>Users</h1>
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

<button onclick={fetchUsers}>Refresh Users</button>