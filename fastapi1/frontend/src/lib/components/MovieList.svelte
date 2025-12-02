<script lang="ts">
  import { onMount } from 'svelte';
  import { authStore } from '../stores/auth.svelte.js';

  let loading = $state(false);
  let error = $state(null);
  let movies = $state<any[]>([]);
  let totalMovies = $state(0);
  let curPage = $state(1);
  let selectedResults = $state("10");
  let perPageResults = $derived(parseInt(selectedResults));
  let totalPages = $derived(totalMovies > 0 ? Math.ceil(totalMovies / perPageResults) : 1);
  let isPrevDisabled = $derived(curPage <= 1);
  let isNextDisabled = $derived(curPage >= totalPages);
  let searchTerm = $state("");
  
  let showForm = $state(false);
  let editingMovie = $state<any>(null);
  let formData = $state({
    name: '',
    altVersions: false,
    quality: '',
    user_id: null,
    service_id: null
  });

  onMount(() => {
    fetchMovies();
  });

  async function fetchMovies() {
    loading = true;
    error = null;
    
    try {
      const response = await fetch(`http://10.120.1.21:8000/api/v1/movies?perPage=${perPageResults}&curPage=${curPage}&searchTerm=${searchTerm}`);
      
      if (!response.ok) throw new Error('Failed to fetch');
      
      const totalCount = response.headers.get('X-Total-Count');
      if (totalCount) {
        totalMovies = parseInt(totalCount);
      }
      
      const data = await response.json();
      movies = data.movies || data.movie || [];
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function deleteMovie(id: number) {
    if(confirm("Are you sure you want to delete this movie?")) {
      try {
        const token = authStore.getToken();
        const response = await fetch(`http://10.120.1.21:8000/api/v1/movies/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!response.ok) throw new Error('Failed to delete');
        
        fetchMovies();
      } catch (e) {
        error = e.message;
      }
    }
  }

  function openAddForm() {
    editingMovie = null;
    formData = {
      name: '',
      altVersions: false,
      quality: '',
      user_id: null,
      service_id: null
    };
    showForm = true;
  }

  function openEditForm(movie: any) {
    editingMovie = movie;
    formData = {
      name: movie.name,
      altVersions: movie.altVersions,
      quality: movie.quality,
      user_id: movie.user_id,
      service_id: movie.service_id
    };
    showForm = true;
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();
    loading = true;
    error = null;

    try {
      const token = authStore.getToken();
      const url = editingMovie 
        ? `http://10.120.1.21:8000/api/v1/movies/${editingMovie.id}`
        : 'http://10.120.1.21:8000/api/v1/movies/';
      
      const method = editingMovie ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) throw new Error('Failed to save movie');

      showForm = false;
      fetchMovies();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function goToPrevious() {
    if (curPage > 1) {
      curPage--;
      fetchMovies();
    }
  }
  
  function goToNext() {
    if (curPage < totalPages) {
      curPage++;
      fetchMovies();
    }
  }
  
  function goToPage(pageNum: number) {
    curPage = pageNum + 1;
    fetchMovies();
  }
  
  function handlePerPageChange() {
    curPage = 1; 
    fetchMovies();
  }

  function search() {
    curPage = 1;
    fetchMovies();
  }
</script>

<div class="movie-management">
  <div class="controls">
    <div class="search-box">
      <label>Search:</label>
      <input type="text" bind:value={searchTerm} oninput={search}>
    </div>
    
    <button class="btn-add" onclick={openAddForm}>+ Add Movie</button>
  </div>

  <div class="pagination-controls">
    <label for="perPage">Results per page: </label>
    <select id="perPage" bind:value={selectedResults} onchange={handlePerPageChange}>
      <option value="10">10</option>
      <option value="25">25</option>
      <option value="50">50</option>
      <option value="100">100</option>
    </select>
    
    <span class="total-info">Total Movies: {totalMovies}</span>
  </div>

  {#if loading}
    <p>Loading Please wait</p>
  {:else if error}
    <p class="error">Error: {error}</p>
  {:else if movies && movies.length > 0}
    <table class="movie-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Quality</th>
          <th>Alt Versions</th>
          <th>User ID</th>
          <th>Service ID</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {#each movies as movie}
          <tr>
            <td>{movie.id}</td>
            <td>{movie.name}</td>
            <td>{movie.quality}</td>
            <td>{movie.altVersions ? 'Yes' : 'No'}</td>
            <td>{movie.user_id || 'N/A'}</td>
            <td>{movie.service_id || 'N/A'}</td>
            <td>
              <button class="btn-edit" onclick={() => openEditForm(movie)}>Edit</button>
              <button class="btn-delete" onclick={() => deleteMovie(movie.id)}>Delete</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {:else}
    <p>No movies found.</p>
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
      <h2>{editingMovie ? 'Edit Movie' : 'Add Movie'}</h2>
      <form onsubmit={handleSubmit}>
        <div class="form-group">
          <label>Name:</label>
          <input type="text" bind:value={formData.name} required />
        </div>
        
        <div class="form-group">
          <label>Quality:</label>
          <input type="text" bind:value={formData.quality} required />
        </div>
        
        <div class="form-group checkbox">
          <label>
            <input type="checkbox" bind:checked={formData.altVersions} />
            Has Alternative Versions
          </label>
        </div>
        
        <div class="form-group">
          <label>User ID:</label>
          <input type="number" bind:value={formData.user_id} />
        </div>
        
        <div class="form-group">
          <label>Service ID:</label>
          <input type="number" bind:value={formData.service_id} />
        </div>
        
        <div class="form-actions">
          <button type="submit" class="btn-save">Save</button>
          <button type="button" class="btn-cancel" onclick={() => showForm = false}>Cancel</button>
        </div>
      </form>
    </div>
  </div>
{/if}