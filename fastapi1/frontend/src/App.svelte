<script>
  import UserList from './lib/components/UserList.svelte';
</script>

<main>
  <h1>User Management</h1>
  <UserList/>
</main>

<style>
  main {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  h1 {
    text-align: center;
    margin-bottom: 2rem;
  }
</style>