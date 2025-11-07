<script lang="ts">
  	//You may have more props than this!
	let {username, full_name, movies, id, email, onDelete} = $props();
</script>
<h2>Username: {username}</h2>
<p>id: {id}</p>
<p>email: {email}</p>
<button class="delete-btn" onclick={() => onDelete(id)}>Delete</button>

<style>
    .delete-btn {
        background-color: #ff4444;
        color: white;
    }
    
    .delete-btn:hover {
        background-color: #cc0000;
    }
</style>