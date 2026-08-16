/**
 * Matchpoint Frontend Interactivity & API Handlers
 */

document.addEventListener('DOMContentLoaded', () => {
  
  // ==========================================
  // STEP 2: Add Skill Modal & AJAX Handling
  // ==========================================
  const modal = document.getElementById('add-skill-modal');
  const btnOpenModal = document.getElementById('btn-open-add-skill');
  const btnCloseModal = document.getElementById('btn-close-modal');
  const addSkillForm = document.getElementById('add-skill-form');
  const skillsContainer = document.getElementById('skills-container');

  if (btnOpenModal && modal) {
    btnOpenModal.addEventListener('click', () => {
      modal.classList.add('open');
      const input = document.getElementById('modal_skill_name');
      if (input) input.focus();
    });
  }

  if (btnCloseModal && modal) {
    btnCloseModal.addEventListener('click', () => {
      modal.classList.remove('open');
    });
  }

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('open');
      }
    });
  }

  if (addSkillForm) {
    addSkillForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const skillName = document.getElementById('modal_skill_name').value.trim();
      const projectName = document.getElementById('modal_project_name').value.trim();
      const projectUrl = document.getElementById('modal_project_url').value.trim();

      if (!skillName || !projectName || !projectUrl) {
        alert('Please provide skill name, project title, and a valid GitHub or website URL.');
        return;
      }

      try {
        const response = await fetch('/api/skills', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            skill_name: skillName,
            project_name: projectName,
            project_url: projectUrl,
            status: 'CHECKING'
          })
        });

        if (response.ok) {
          const data = await response.json();
          
          // Append new card into DOM
          const card = document.createElement('div');
          card.className = 'skill-card';
          card.setAttribute('data-id', data.id);
          card.innerHTML = `
            <div class="skill-card-left">
              <div class="skill-icon-wrap">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                </svg>
              </div>
              <div class="skill-info">
                <span class="skill-title">${data.skill_name}</span>
                <span class="skill-project">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"></path>
                  </svg>
                  <a href="${data.project_url}" target="_blank" style="color: inherit; text-decoration: underline;">${data.project_name}</a>
                </span>
              </div>
            </div>
            <div>
              <span class="badge-status badge-checking">CHECKING</span>
            </div>
          `;
          skillsContainer.appendChild(card);

          // Reset and close
          addSkillForm.reset();
          modal.classList.remove('open');
        }
      } catch (err) {
        console.error('Error adding skill:', err);
      }
    });
  }

  // ==========================================
  // STEP 3: File Upload & Drag and Drop
  // ==========================================
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const uploadPrompt = document.getElementById('upload-prompt');
  const filePreview = document.getElementById('file-preview');
  const previewFilename = document.getElementById('preview-filename');
  const previewFilesize = document.getElementById('preview-filesize');
  const btnRemoveFile = document.getElementById('btn-remove-file');
  const btnSubmitDocs = document.getElementById('btn-submit-docs');

  function formatBytes(bytes, decimals = 1) {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
  }

  function handleFileSelection(file) {
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      alert('File size exceeds 10MB limit.');
      return;
    }

    if (previewFilename && previewFilesize && filePreview && uploadPrompt && btnSubmitDocs) {
      previewFilename.textContent = file.name;
      previewFilesize.textContent = formatBytes(file.size);
      uploadPrompt.style.display = 'none';
      filePreview.classList.add('active');
      btnSubmitDocs.disabled = false;
      btnSubmitDocs.classList.remove('disabled');
    }
  }

  if (dropZone && fileInput) {
    dropZone.addEventListener('click', (e) => {
      if (e.target !== btnRemoveFile && !e.target.closest('#btn-remove-file')) {
        fileInput.click();
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (fileInput.files && fileInput.files[0]) {
        handleFileSelection(fileInput.files[0]);
      }
    });

    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('dragover');
      }, false);
    });

    dropZone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files && files[0]) {
        fileInput.files = files;
        handleFileSelection(files[0]);
      }
    });
  }

  if (btnRemoveFile && fileInput) {
    btnRemoveFile.addEventListener('click', (e) => {
      e.stopPropagation();
      fileInput.value = '';
      filePreview.classList.remove('active');
      uploadPrompt.style.display = 'block';
      
      btnSubmitDocs.disabled = true;
      btnSubmitDocs.classList.add('disabled');
    });
  }

});
