<script lang="ts">
  import { onMount } from 'svelte';
  import { authStore } from '../stores/auth.svelte.js';

  let loading = $state(false);
  let error = $state(null);
  let services = $state<any[]>([]);
  let totalServices = $state(0);
  let curPage = $state(1);
  let selectedResults = $state("10");
  let perPageResults = $derived(parseInt(selectedResults));
  let totalPages = $derived(totalServices > 0 ? Math.ceil(totalServices / perPageResults) : 1);
  let isPrevDisabled = $derived(curPage <= 1);
  let isNextDisabled = $derived(curPage >= totalPages);
  let searchTerm = $state("");
  
  let showForm = $state(false);
  let editingService = $state<any>(null);
  let formData = $state({
    name: ''
  });

  onMount(() => {
    fetchServices();
  });

  async function fetchServices() {
    loading = true;
    error = null;
    
    try {
      const response = await fetch(`http://10.120.1.21:8000/api/v1/services?perPage=${perPageResults}&curPage=${curPage}&searchTerm=${searchTerm}`);
      
      if (!response.ok) throw new Error('Failed to fetch');
      
      const totalCount = response.headers.get('X-Total-Count');
      if (totalCount) {
        totalServices = parseInt(totalCount);
      }
      
      const data = await response.json();
      services = data.services || [];
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function deleteService(id: number) {
    if(confirm("Are you sure you want to delete this service?")) {
      try {
        const token = authStore.getToken();
        const response = await fetch(`http://10.120.1.21:8000/api/v1/services/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!response.ok) throw new Error('Failed to delete');
        
        fetchServices();
      } catch (e) {
        error = e.message;
      }
    }
  }

  function openAddForm() {
    editingService = null;
    formData = { name: '' };
    showForm = true;
  }

  function openEditForm(service: any) {
    editingService = service;
    formData = { name: service.name };
    showForm = true;
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();
    loading = true;
    error = null;

    try {
      const token = authStore.getToken();
      const url = editingService 
        ? `http://10.120.1.21:8000/api/v1/services/${editingService.id}`
        : 'http://10.120.1.21:8000/api/v1/services/';
      
      const method = editingService ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) throw new Error('Failed to save service');

      showForm = false;
      fetchServices();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function goToPrevious() {
    if (curPage > 1) {
      curPage--;
      fetchServices();
    }
  }
  
  function goToNext() {
    if (curPage < totalPages) {
      curPage++;
      fetchServices();
    }
  }
  
  function goToPage(pageNum: number) {
    curPage = pageNum + 1;
    fetchServices();
  }
  
  function handlePerPageChange() {
    curPage = 1; 
    fetchServices();
  }

  function search() {
    curPage = 1;
    fetchServices();
  }
</script>

<div class="service-management">
  <div class="controls">
    <div class="search-box">
      <label>Search:</label>
      <input type="text" bind:value={searchTerm} oninput={search}>
    </div>
    
    <button class="btn-add" onclick={openAddForm}>+ Add Service</button>
  </div>

  <div class="pagination-controls">
    <label for="perPage">Results per page: </label>
    <select id="perPage" bind:value={selectedResults} onchange={handlePerPageChange}>
      <option value="10">10</option>
      <option value="25">25</option>
      <option value="50">50</option>
      <option value="100">100</option>
    </select>
    
    <span class="total-info">Total Services: {totalServices}</span>
  </div>

  {#if loading}
    <p>Loading Please wait</p>
  {:else if error}
    <p class="error">Error: {error}</p>
  {:else if services && services.length > 0}
    <table class="service-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {#each services as service}
          <tr>
            <td>{service.id}</td>
            <td>{service.name}</td>
            <td>
              <button class="btn-edit" onclick={() => openEditForm(service)}>Edit</button>
              <button class="btn-delete" onclick={() => deleteService(service.id)}>Delete</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {:else}
    <p>No services found.</p>
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
      <h2>{editingService ? 'Edit Service' : 'Add Service'}</h2>
      <form onsubmit={handleSubmit}>
        <div class="form-group">
          <label>Service Name:</label>
          <input type="text" bind:value={formData.name} required />
        </div>
        
        <div class="form-actions">
          <button type="submit" class="btn-save">Save</button>
          <button type="button" class="btn-cancel" onclick={() => showForm = false}>Cancel</button>
        </div>
      </form>
    </div>
  </div>
{/if}

