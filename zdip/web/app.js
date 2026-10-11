// Zytor Sovereign Frontend Engine Controller (v1.2.0)
let ws = null;
let currentAnalysis = null;
let activeTab = 'active'; // 'active' or 'completed'
let mediaFilter = 'all'; // 'all', 'video', 'audio', 'image'
let currentView = 'big-grid'; // 'big-grid', 'small-grid', 'list'

let selectedFormat = 'best';
let isAudioOnly = false;
let selectedAudioFormat = 'mp3';
let selectedStorageMode = 'local'; // 'local', 'sync_copy', 'direct_stream'
let useTor = false;
let useTurboBolt = true;
let remotesList = [];
let allJobs = {};

// DOM Elements
const urlInput = document.getElementById('url-input');
const btnAnalyze = document.getElementById('btn-analyze');
const chipTurboBolt = document.getElementById('chip-turbobolt');
const chipTor = document.getElementById('chip-tor');

const downloadModal = document.getElementById('download-modal');
const closeDownloadModal = document.getElementById('close-download-modal');
const modalThumb = document.getElementById('modal-thumb');
const modalTitle = document.getElementById('modal-title');
const modalUploader = document.getElementById('modal-uploader');
const modalOnionBadge = document.getElementById('modal-onion-badge');
const videoQualitiesRow = document.getElementById('video-qualities-row');
const audioQualitiesRow = document.getElementById('audio-qualities-row');
const storageRemoteSelect = document.getElementById('storage-remote-select');
const storageModeGroup = document.getElementById('storage-mode-group');
const modeSyncChip = document.getElementById('mode-sync-chip');
const modeDirectChip = document.getElementById('mode-direct-chip');
const modalToggleTurbo = document.getElementById('modal-toggle-turbobolt');
const modalToggleTor = document.getElementById('modal-toggle-tor');
const btnStartDownload = document.getElementById('btn-start-download');

// Official Zytor Formats & Embedding
const videoContainerSelect = document.getElementById('video-container-select');
const videoCodecSelect = document.getElementById('video-codec-select');
const checkEmbedMetadata = document.getElementById('check-embed-metadata');
const checkEmbedThumbnail = document.getElementById('check-embed-thumbnail');
const checkEmbedSubs = document.getElementById('check-embed-subs');

// Dashboard Elements
const jobsContainer = document.getElementById('jobs-container');
const emptyState = document.getElementById('empty-state');
const activeCount = document.getElementById('active-count');
const completedCount = document.getElementById('completed-count');
const btnClearCompleted = document.getElementById('btn-clear-completed');

// Remotes Modal Elements
const remotesModal = document.getElementById('remotes-modal');
const openRemotesModalBtn = document.getElementById('open-remotes-modal-btn');
const closeRemotesModal = document.getElementById('close-remotes-modal');
const cloudVaultBtn = document.getElementById('cloud-vault-btn');
const remotesCountText = document.getElementById('remotes-count-text');
const tabConnectedRemotes = document.getElementById('tab-connected-remotes');
const tabAddRemote = document.getElementById('tab-add-remote');
const tabAddCrypt = document.getElementById('tab-add-crypt');
const tabRawConfig = document.getElementById('tab-raw-config');
const remotesListView = document.getElementById('remotes-list-view');
const addRemoteView = document.getElementById('add-remote-view');
const addCryptView = document.getElementById('add-crypt-view');
const rawConfigView = document.getElementById('raw-config-view');
const remotesCardsContainer = document.getElementById('remotes-cards-container');
const newRemoteType = document.getElementById('new-remote-type');
const newRemoteName = document.getElementById('new-remote-name');
const remoteCustomFields = document.getElementById('remote-custom-fields');
const btnSaveRemote = document.getElementById('btn-save-remote');
const btnImportSystemRemotes = document.getElementById('btn-import-system-remotes');
const rawConfigTextarea = document.getElementById('raw-config-textarea');
const btnSaveRawConfig = document.getElementById('btn-save-raw-config');
const btnReloadRawConfig = document.getElementById('btn-reload-raw-config');

const cryptVaultName = document.getElementById('crypt-vault-name');
const cryptBaseRemote = document.getElementById('crypt-base-remote');
const cryptBasePath = document.getElementById('crypt-base-path');
const cryptPassword = document.getElementById('crypt-password');
const cryptSalt = document.getElementById('crypt-salt');
const btnCreateCrypt = document.getElementById('btn-create-crypt');

// Tor Modal Elements
const torStatusPill = document.getElementById('tor-status-pill');
const torIndicator = document.getElementById('tor-indicator');
const torStatusText = document.getElementById('tor-status-text');
const torModal = document.getElementById('tor-modal');
const closeTorModal = document.getElementById('close-tor-modal');
const torModalStatusDetail = document.getElementById('tor-modal-status-detail');
const torClearnetIp = document.getElementById('tor-clearnet-ip');
const torExitIp = document.getElementById('tor-exit-ip');
const btnRotateCircuit = document.getElementById('btn-rotate-circuit');

// TurboBolt Modal Elements
const openTurboboltBtn = document.getElementById('open-turbobolt-settings-btn');
const turboboltModal = document.getElementById('turbobolt-modal');
const closeTurboboltModal = document.getElementById('close-turbobolt-modal');
const settingSegments = document.getElementById('setting-segments');
const valSegments = document.getElementById('val-segments');
const settingConnections = document.getElementById('setting-connections');
const valConnections = document.getElementById('val-connections');
const btnSaveTurboSettings = document.getElementById('btn-save-turbobolt-settings');

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
  initWebSocket();
  fetchTorStatus();
  fetchRemotes();
  setupEventListeners();
});

// --- WebSocket Connection ---
function initWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log('[Zytor WS] Connected');
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      if (msg.type === 'init') {
        msg.jobs.forEach(job => { allJobs[job.job_id] = job; });
        renderJobs();
      } else if (msg.type === 'job_update') {
        allJobs[msg.data.job_id] = msg.data;
        renderJobs();
      }
    } catch (e) {
      console.error('[Zytor WS] Parse error:', e);
    }
  };

  ws.onclose = () => {
    setTimeout(initWebSocket, 2000);
  };
}

// --- Event Listeners ---
function setupEventListeners() {
  // Hero Toggles
  chipTurboBolt.addEventListener('click', () => {
    useTurboBolt = !useTurboBolt;
    chipTurboBolt.classList.toggle('active-turbobolt', useTurboBolt);
  });

  chipTor.addEventListener('click', () => {
    useTor = !useTor;
    chipTor.classList.toggle('active-tor', useTor);
  });

  // URL Analyze
  btnAnalyze.addEventListener('click', triggerAnalyze);
  urlInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') triggerAnalyze();
  });

  // Close Modals
  closeDownloadModal.addEventListener('click', () => downloadModal.classList.remove('open'));
  closeRemotesModal.addEventListener('click', () => remotesModal.classList.remove('open'));
  closeTorModal.addEventListener('click', () => torModal.classList.remove('open'));
  closeTurboboltModal.addEventListener('click', () => turboboltModal.classList.remove('open'));

  // Open Modals
  openRemotesModalBtn.addEventListener('click', () => openRemotesDialog('list'));
  cloudVaultBtn.addEventListener('click', () => openRemotesDialog('list'));
  openTurboboltBtn.addEventListener('click', () => turboboltModal.classList.add('open'));

  torStatusPill.addEventListener('click', () => {
    torModal.classList.add('open');
    fetchTorStatus(true);
  });

  // Tor Circuit Rotate
  btnRotateCircuit.addEventListener('click', rotateTorCircuit);

  // Tabs in Remotes Modal
  tabConnectedRemotes.addEventListener('click', () => switchRemotesTab('list'));
  tabAddRemote.addEventListener('click', () => switchRemotesTab('add'));
  tabAddCrypt.addEventListener('click', () => switchRemotesTab('crypt'));
  tabRawConfig.addEventListener('click', () => switchRemotesTab('raw'));

  newRemoteType.addEventListener('change', renderRemoteCustomFields);
  btnSaveRemote.addEventListener('click', saveNewRemote);
  btnCreateCrypt.addEventListener('click', createCryptVault);
  btnImportSystemRemotes.addEventListener('click', importSystemRemotes);
  btnSaveRawConfig.addEventListener('click', saveRawConfig);
  btnReloadRawConfig.addEventListener('click', loadRawConfig);

  // TurboBolt Sliders
  settingSegments.addEventListener('input', () => { valSegments.textContent = settingSegments.value; });
  settingConnections.addEventListener('input', () => { valConnections.textContent = settingConnections.value; });
  btnSaveTurboSettings.addEventListener('click', () => {
    turboboltModal.classList.remove('open');
    alert(`TurboBolt preferences updated: ${settingSegments.value} Segments, ${settingConnections.value} Connections/host.`);
  });

  // Media Type Filter (Official Zytor)
  document.querySelectorAll('.filter-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      mediaFilter = pill.dataset.filter;
      renderJobs();
    });
  });

  // View Mode Switcher (Big Grid, Small Grid, List)
  document.getElementById('view-big-grid').addEventListener('click', () => switchView('big-grid'));
  document.getElementById('view-small-grid').addEventListener('click', () => switchView('small-grid'));
  document.getElementById('view-list').addEventListener('click', () => switchView('list'));

  // Dashboard Tab Switching (Active vs Completed)
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeTab = btn.dataset.tab;
      renderJobs();
    });
  });

  btnClearCompleted.addEventListener('click', async () => {
    await fetch('/api/downloads/clear', { method: 'POST' });
    Object.keys(allJobs).forEach(id => {
      if (['COMPLETED', 'CANCELLED', 'FAILED'].includes(allJobs[id].status)) {
        delete allJobs[id];
      }
    });
    renderJobs();
  });

  // Storage Target Selection in Download Drawer
  storageRemoteSelect.addEventListener('change', () => {
    const val = storageRemoteSelect.value;
    if (val) {
      storageModeGroup.style.display = 'block';
      selectedStorageMode = 'sync_copy';
      modeSyncChip.classList.add('selected');
      modeDirectChip.classList.remove('selected');
    } else {
      storageModeGroup.style.display = 'none';
      selectedStorageMode = 'local';
    }
  });

  modeSyncChip.addEventListener('click', () => {
    selectedStorageMode = 'sync_copy';
    modeSyncChip.classList.add('selected');
    modeDirectChip.classList.remove('selected');
  });

  modeDirectChip.addEventListener('click', () => {
    selectedStorageMode = 'direct_stream';
    modeDirectChip.classList.add('selected');
    modeSyncChip.classList.remove('selected');
  });

  modalToggleTurbo.addEventListener('click', () => {
    useTurboBolt = !useTurboBolt;
    modalToggleTurbo.classList.toggle('selected', useTurboBolt);
    chipTurboBolt.classList.toggle('active-turbobolt', useTurboBolt);
  });

  modalToggleTor.addEventListener('click', () => {
    useTor = !useTor;
    modalToggleTor.classList.toggle('selected-violet', useTor);
    chipTor.classList.toggle('active-tor', useTor);
  });

  btnStartDownload.addEventListener('click', executeDownloadJob);
}

function switchView(view) {
  currentView = view;
  document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
  if (view === 'big-grid') document.getElementById('view-big-grid').classList.add('active');
  if (view === 'small-grid') document.getElementById('view-small-grid').classList.add('active');
  if (view === 'list') document.getElementById('view-list').classList.add('active');

  jobsContainer.className = `jobs-${view}`;
  renderJobs();
}

// --- Analyze URL ---
async function triggerAnalyze() {
  const url = urlInput.value.trim();
  if (!url) {
    alert('Please enter a media URL, magnet link, or .onion link.');
    return;
  }

  btnAnalyze.textContent = 'Probing...';
  btnAnalyze.disabled = true;

  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, use_tor: useTor })
    });
    const data = await res.json();

    if (!data.success) {
      alert(`Analysis error: ${data.error || 'Could not analyze URL'}`);
      return;
    }

    currentAnalysis = data;
    showDownloadDrawer(data);
  } catch (err) {
    alert(`Request failed: ${err.message}`);
  } finally {
    btnAnalyze.textContent = 'Analyze Link';
    btnAnalyze.disabled = false;
  }
}

// --- Show Download Drawer ---
function showDownloadDrawer(data) {
  modalTitle.textContent = data.title || 'Untitled Stream';
  modalUploader.textContent = data.uploader || 'Universal Platform';
  modalThumb.src = data.thumbnail || 'https://zytor.vercel.app/icon.png';

  if (data.is_onion) {
    modalOnionBadge.style.display = 'inline-block';
    useTor = true;
    modalToggleTor.classList.add('selected-violet');
    chipTor.classList.add('active-tor');
  } else {
    modalOnionBadge.style.display = 'none';
  }

  // Render Video Quality Chips
  videoQualitiesRow.innerHTML = '';
  selectedFormat = 'best';
  isAudioOnly = false;

  const defaultBestChip = document.createElement('div');
  defaultBestChip.className = 'select-chip selected';
  defaultBestChip.textContent = '🔥 Best Available (Auto 4K/FHD)';
  defaultBestChip.onclick = () => {
    document.querySelectorAll('#video-qualities-row .select-chip, #audio-qualities-row .select-chip').forEach(c => c.classList.remove('selected'));
    defaultBestChip.classList.add('selected');
    selectedFormat = 'best';
    isAudioOnly = false;
  };
  videoQualitiesRow.appendChild(defaultBestChip);

  if (data.video_qualities && data.video_qualities.length > 0) {
    data.video_qualities.forEach(q => {
      const chip = document.createElement('div');
      chip.className = 'select-chip';
      const sizeMb = q.filesize ? ` (~${Math.round(q.filesize / 1024 / 1024)}MB)` : '';
      chip.textContent = `${q.label}${sizeMb}`;
      chip.onclick = () => {
        document.querySelectorAll('#video-qualities-row .select-chip, #audio-qualities-row .select-chip').forEach(c => c.classList.remove('selected'));
        chip.classList.add('selected');
        selectedFormat = q.format_id;
        isAudioOnly = false;
      };
      videoQualitiesRow.appendChild(chip);
    });
  }

  // Render Audio Formats (FLAC, MP3, WAV, ALAC, OPUS)
  audioQualitiesRow.innerHTML = '';
  const audioFormats = [
    { label: 'MP3 (320kbps High)', ext: 'mp3' },
    { label: 'FLAC (Lossless Studio)', ext: 'flac' },
    { label: 'M4A (AAC High)', ext: 'm4a' },
    { label: 'WAV (Uncompressed PCM)', ext: 'wav' },
    { label: 'OPUS (Low Latency)', ext: 'opus' }
  ];
  audioFormats.forEach(af => {
    const chip = document.createElement('div');
    chip.className = 'select-chip';
    chip.textContent = `🎵 ${af.label}`;
    chip.onclick = () => {
      document.querySelectorAll('#video-qualities-row .select-chip, #audio-qualities-row .select-chip').forEach(c => c.classList.remove('selected'));
      chip.classList.add('selected');
      isAudioOnly = true;
      selectedAudioFormat = af.ext;
    };
    audioQualitiesRow.appendChild(chip);
  });

  // Populate Remotes
  updateStorageDropdown();

  downloadModal.classList.add('open');
}

function updateStorageDropdown() {
  storageRemoteSelect.innerHTML = '<option value="">💾 Local Storage (downloads/)</option>';
  remotesList.forEach(r => {
    const icon = r.is_crypt ? '🔒' : '☁️';
    const label = `${icon} ${r.name} (${r.type.toUpperCase()}${r.is_crypt ? ' AES-256 Encrypted' : ''})`;
    const opt = document.createElement('option');
    opt.value = r.name;
    opt.textContent = label;
    storageRemoteSelect.appendChild(opt);
  });
}

// --- Execute Download Job ---
async function executeDownloadJob() {
  if (!currentAnalysis) return;

  const remote = storageRemoteSelect.value;
  const storageMode = remote ? selectedStorageMode : 'local';

  const payload = {
    url: currentAnalysis.url,
    title: currentAnalysis.title,
    format_id: selectedFormat,
    is_audio_only: isAudioOnly,
    audio_format: selectedAudioFormat,
    storage_mode: storageMode,
    dest_remote: remote,
    dest_folder: 'ZytorMedia',
    delete_local_after_sync: false,
    use_tor: useTor,
    segments: useTurboBolt ? parseInt(settingSegments.value || '64') : 8,
    embed_metadata: checkEmbedMetadata.checked,
    embed_thumbnail: checkEmbedThumbnail.checked,
    embed_subtitles: checkEmbedSubs.checked,
    subtitle_lang: 'en.*',
    video_codec: videoCodecSelect.value,
    media_type: isAudioOnly ? 'audio' : 'video'
  };

  btnStartDownload.textContent = 'Launching TurboBolt...';
  btnStartDownload.disabled = true;

  try {
    const res = await fetch('/api/downloads', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const job = await res.json();
    allJobs[job.job_id] = job;
    downloadModal.classList.remove('open');
    urlInput.value = '';
    renderJobs();
  } catch (err) {
    alert(`Failed to start download: ${err.message}`);
  } finally {
    btnStartDownload.textContent = 'Start TurboBolt Download';
    btnStartDownload.disabled = false;
  }
}

// --- Render Jobs ---
function renderJobs() {
  const jobs = Object.values(allJobs);
  const activeJobs = jobs.filter(j => ['QUEUED', 'DOWNLOADING', 'STREAMING_TO_CLOUD', 'SYNCING_TO_CLOUD'].includes(j.status));
  const completedJobs = jobs.filter(j => ['COMPLETED', 'CANCELLED', 'FAILED'].includes(j.status));

  activeCount.textContent = activeJobs.length;
  completedCount.textContent = completedJobs.length;

  let displayList = activeTab === 'active' ? activeJobs : completedJobs;

  // Apply Media Type Filter
  if (mediaFilter !== 'all') {
    displayList = displayList.filter(j => (j.media_type || 'video') === mediaFilter);
  }

  if (displayList.length === 0) {
    emptyState.style.display = 'block';
    jobsContainer.innerHTML = '';
    jobsContainer.appendChild(emptyState);
    return;
  }

  emptyState.style.display = 'none';
  jobsContainer.innerHTML = '';

  displayList.reverse().forEach(job => {
    const card = document.createElement('div');
    card.className = 'job-card glass-panel';

    let badgeClass = 'badge-downloading';
    if (job.status === 'STREAMING_TO_CLOUD') badgeClass = 'badge-streaming';
    if (job.status === 'SYNCING_TO_CLOUD') badgeClass = 'badge-syncing';
    if (job.status === 'COMPLETED') badgeClass = 'badge-completed';
    if (job.status === 'FAILED') badgeClass = 'badge-failed';

    const storageIcon = job.storage_mode === 'direct_stream' ? '☁️ Zero-Disk' : (job.dest_remote ? '☁️ Staged Sync' : '💾 Local');
    const torPill = job.use_tor ? '<span style="color:var(--accent-violet); margin-left:8px;">🧅 Tor</span>' : '';

    if (currentView === 'list') {
      // Clean single-line list row
      card.style.cssText = 'padding:12px 18px; display:flex; justify-content:space-between; align-items:center; gap:16px;';
      card.innerHTML = `
        <div style="flex:1; min-width:0;">
          <div style="font-weight:600; color:#fff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${job.title}</div>
          <div style="font-size:12px; color:var(--text-secondary); margin-top:2px;">
            <span>⚡ ${job.speed || '0 KB/s'}</span> • <span>${job.progress}%</span> • <span>${storageIcon}</span> ${torPill}
          </div>
        </div>
        <div style="width:140px;">
          <div class="progress-container" style="margin-bottom:0;"><div class="progress-bar" style="width:${job.progress}%;"></div></div>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="job-badge ${badgeClass}">${job.status.replace(/_/g, ' ')}</span>
          ${job.status === 'DOWNLOADING' ? `<button class="btn-card-action" onclick="cancelJob('${job.job_id}')">Cancel</button>` : ''}
        </div>
      `;
    } else {
      // Grid view (Big or Small)
      const isBig = currentView === 'big-grid';
      
      let segmentsHtml = '';
      const totalSegs = Math.min(job.segments || 16, 64);
      const activeSegs = job.status === 'DOWNLOADING' ? Math.max(1, Math.round((totalSegs * (job.progress || 10)) / 100)) : 0;
      for (let i = 0; i < totalSegs; i++) {
        segmentsHtml += `<div class="segment-block ${i < activeSegs ? 'active' : ''}"></div>`;
      }

      const mediaBannerHtml = (isBig && currentAnalysis && currentAnalysis.thumbnail) ? 
        `<img src="${currentAnalysis.thumbnail}" class="card-media-banner" alt="Thumbnail">` : '';

      card.innerHTML = `
        ${mediaBannerHtml}
        <div class="job-header">
          <h4 class="job-title" title="${job.title}">${job.title}</h4>
          <span class="job-badge ${badgeClass}">${job.status.replace(/_/g, ' ')}</span>
        </div>

        <div class="progress-container">
          <div class="progress-bar" style="width: ${job.progress}%;"></div>
        </div>

        <div class="segments-map" title="TurboBolt Parallel Segments Activity">
          ${segmentsHtml}
        </div>

        <div class="job-meta">
          <div class="meta-stats">
            <span>⚡ ${job.speed || '0 KB/s'}</span>
            <span>⏱️ ${job.eta || '--:--'}</span>
            <span>${job.progress}%</span>
            <span>${storageIcon}</span>
            ${torPill}
          </div>
          <div class="job-actions">
            ${job.status === 'DOWNLOADING' ? `<button class="btn-card-action" onclick="cancelJob('${job.job_id}')">Cancel</button>` : ''}
            ${job.cloud_filepath ? `<span style="color:var(--accent-cyan); font-size:11px;" title="${job.cloud_filepath}">Uploaded to Cloud</span>` : ''}
          </div>
        </div>
      `;
    }

    jobsContainer.appendChild(card);
  });
}

async function cancelJob(jobId) {
  await fetch(`/api/downloads/${jobId}`, { method: 'DELETE' });
}

// --- Tor Status & Anonymity ---
async function fetchTorStatus(forceRefresh = false) {
  try {
    const res = await fetch(`/api/tor/status?refresh=${forceRefresh}`);
    const data = await res.json();

    if (data.tor_running) {
      torIndicator.className = 'status-indicator tor';
      torStatusText.textContent = `Tor Active (${data.tor_exit_ip || 'Tunnel Ready'})`;
      torModalStatusDetail.textContent = `Tor SOCKS5 Proxy active at ${data.socks_proxy}`;
    } else {
      torIndicator.className = 'status-indicator';
      torStatusText.textContent = 'Tor Offline';
      torModalStatusDetail.textContent = 'Tor daemon not detected on port 9050/9150. Clearnet active.';
    }

    torClearnetIp.textContent = data.clearnet_ip || 'Unknown';
    torExitIp.textContent = data.tor_exit_ip || 'None (Clearnet)';
  } catch (err) {
    console.warn('Failed to fetch Tor status:', err);
  }
}

async function rotateTorCircuit() {
  btnRotateCircuit.textContent = 'Rotating Circuit (NEWNYM)...';
  try {
    const res = await fetch('/api/tor/rotate', { method: 'POST' });
    const data = await res.json();
    alert(data.message);
    fetchTorStatus(true);
  } catch (err) {
    alert(`Rotation error: ${err.message}`);
  } finally {
    btnRotateCircuit.textContent = '🔄 Acquire New Tor Identity / Circuit (NEWNYM)';
  }
}

// --- Remotes Management ---
async function fetchRemotes() {
  try {
    const res = await fetch('/api/remotes');
    remotesList = await res.json();
    remotesCountText.textContent = `${remotesList.length} Connected`;
    renderRemotesList();
    updateStorageDropdown();
  } catch (err) {
    console.warn('Failed to fetch remotes:', err);
  }
}

function openRemotesDialog(tab) {
  remotesModal.classList.add('open');
  switchRemotesTab(tab);
}

function switchRemotesTab(tab) {
  remotesListView.style.display = tab === 'list' ? 'block' : 'none';
  addRemoteView.style.display = tab === 'add' ? 'block' : 'none';
  addCryptView.style.display = tab === 'crypt' ? 'block' : 'none';
  rawConfigView.style.display = tab === 'raw' ? 'block' : 'none';

  tabConnectedRemotes.style.opacity = tab === 'list' ? '1' : '0.6';
  tabAddRemote.style.opacity = tab === 'add' ? '1' : '0.6';
  tabAddCrypt.style.opacity = tab === 'crypt' ? '1' : '0.6';
  tabRawConfig.style.opacity = tab === 'raw' ? '1' : '0.6';

  if (tab === 'add') renderRemoteCustomFields();
  if (tab === 'crypt') populateCryptBaseRemotes();
  if (tab === 'raw') loadRawConfig();
}

function renderRemotesList() {
  remotesCardsContainer.innerHTML = '';
  if (remotesList.length === 0) {
    remotesCardsContainer.innerHTML = `
      <div style="text-align:center; padding:30px; color:var(--text-muted);">
        No cloud storage remotes connected.<br>
        Click <strong>"+ Connect Provider"</strong> to add Terabox, AList, Mega, S3, or click <strong>"Auto-Import System rclone.conf"</strong>.
      </div>
    `;
    return;
  }

  remotesList.forEach(r => {
    const card = document.createElement('div');
    card.style.cssText = 'display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.04); border:1px solid var(--border-color); border-radius:14px; padding:12px 16px;';
    
    const icon = r.is_crypt ? '🔒' : '☁️';
    const subInfo = r.is_crypt ? `Target: ${r.remote} • AES-256 Encrypted` : `Type: ${r.type.toUpperCase()}`;

    card.innerHTML = `
      <div>
        <div style="font-weight:700; color:#fff; font-size:15px;">${icon} ${r.name}</div>
        <div style="font-size:12px; color:var(--text-secondary); margin-top:2px;">${subInfo}</div>
      </div>
      <div style="display:flex; gap:8px;">
        <button class="btn-card-action" onclick="testRemoteConnection('${r.name}')">Test</button>
        <button class="btn-card-action" onclick="browseRemoteFiles('${r.name}')">Browse</button>
        <button class="btn-card-action" style="color:var(--danger);" onclick="deleteRemote('${r.name}')">Delete</button>
      </div>
    `;
    remotesCardsContainer.appendChild(card);
  });
}

function renderRemoteCustomFields() {
  const type = newRemoteType.value;
  let fieldsHtml = '';

  if (type === 'terabox') {
    fieldsHtml = `
      <label class="config-label">Terabox Cookie (ndus value)</label>
      <input type="text" id="param-cookie" class="form-input" placeholder="Paste ndus=... cookie from browser session">
      <small style="color:var(--text-muted); display:block; margin-top:4px;">Log in to Terabox in browser -> inspect cookie 'ndus' -> paste here.</small>
    `;
  } else if (type === 'alist') {
    fieldsHtml = `
      <label class="config-label">AList Server URL</label>
      <input type="text" id="param-url" class="form-input" placeholder="https://alist.yourserver.com">
      <label class="config-label" style="margin-top:10px;">Password / Admin Token</label>
      <input type="password" id="param-password" class="form-input" placeholder="Password or token">
    `;
  } else if (type === 'teldrive') {
    fieldsHtml = `
      <label class="config-label">TelDrive API Host</label>
      <input type="text" id="param-api_host" class="form-input" placeholder="https://teldrive.yourserver.com">
      <label class="config-label" style="margin-top:10px;">JWT Access Token</label>
      <input type="password" id="param-jwt_token" class="form-input" placeholder="JWT Token">
    `;
  } else if (type === 'mega') {
    fieldsHtml = `
      <label class="config-label">Mega Account Email / Username</label>
      <input type="text" id="param-user" class="form-input" placeholder="user@example.com">
      <label class="config-label" style="margin-top:10px;">Mega Password</label>
      <input type="password" id="param-pass" class="form-input" placeholder="Password">
    `;
  } else if (type === 'webdav') {
    fieldsHtml = `
      <label class="config-label">WebDAV Server URL</label>
      <input type="text" id="param-url" class="form-input" placeholder="https://nextcloud.example.com/remote.php/dav/files/user/">
      <label class="config-label" style="margin-top:10px;">Username</label>
      <input type="text" id="param-user" class="form-input" placeholder="Username">
      <label class="config-label" style="margin-top:10px;">Password / App Password</label>
      <input type="password" id="param-pass" class="form-input" placeholder="Password">
      <label class="config-label" style="margin-top:10px;">Vendor (Optional)</label>
      <input type="text" id="param-vendor" class="form-input" placeholder="nextcloud, owncloud, other">
    `;
  } else if (type === 's3') {
    fieldsHtml = `
      <label class="config-label">S3 Provider (AWS, Cloudflare, Minio, Wasabi)</label>
      <input type="text" id="param-provider" class="form-input" placeholder="AWS, Cloudflare, Minio, Wasabi">
      <label class="config-label" style="margin-top:10px;">Access Key ID</label>
      <input type="text" id="param-access_key_id" class="form-input" placeholder="Access Key">
      <label class="config-label" style="margin-top:10px;">Secret Access Key</label>
      <input type="password" id="param-secret_access_key" class="form-input" placeholder="Secret Key">
      <label class="config-label" style="margin-top:10px;">Endpoint URL (required for Cloudflare R2 / MinIO)</label>
      <input type="text" id="param-endpoint" class="form-input" placeholder="https://<account>.r2.cloudflarestorage.com">
    `;
  } else if (type === 'local') {
    fieldsHtml = `
      <label class="config-label">External Drive / Folder Path</label>
      <input type="text" id="param-path" class="form-input" placeholder="D:\\MediaBackups or E:\\">
    `;
  } else {
    // Google Drive, OneDrive, Dropbox
    fieldsHtml = `
      <label class="config-label">OAuth2 Token JSON</label>
      <textarea id="param-token" class="form-input" style="height:100px; font-family:monospace; font-size:12px;" placeholder="Paste JSON token or leave blank if using service account"></textarea>
      <label class="config-label" style="margin-top:10px;">Service Account JSON Path (Optional)</label>
      <input type="text" id="param-service_account_file" class="form-input" placeholder="C:\\path\\to\\credentials.json">
    `;
  }

  remoteCustomFields.innerHTML = fieldsHtml;
}

async function saveNewRemote() {
  const name = newRemoteName.value.trim();
  const type = newRemoteType.value;
  if (!name) {
    alert('Please provide a remote name.');
    return;
  }

  const params = {};
  document.querySelectorAll('#remote-custom-fields input, #remote-custom-fields textarea').forEach(input => {
    const key = input.id.replace('param-', '');
    if (input.value.trim()) {
      params[key] = input.value.trim();
    }
  });

  btnSaveRemote.textContent = 'Saving Remote...';
  try {
    const res = await fetch('/api/remotes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, backend_type: type, parameters: params })
    });
    const result = await res.json();
    if (result.success) {
      alert(`Remote '${name}' configured successfully!`);
      newRemoteName.value = '';
      await fetchRemotes();
      switchRemotesTab('list');
    } else {
      alert(`Error saving remote: ${result.stderr || result.error || 'Check fields'}`);
    }
  } catch (err) {
    alert(`Request error: ${err.message}`);
  } finally {
    btnSaveRemote.textContent = 'Save Cloud Remote';
  }
}

async function importSystemRemotes() {
  btnImportSystemRemotes.textContent = 'Importing...';
  try {
    const res = await fetch('/api/remotes/import-system', { method: 'POST' });
    const data = await res.json();
    alert(data.message);
    await fetchRemotes();
  } catch (err) {
    alert(`Import error: ${err.message}`);
  } finally {
    btnImportSystemRemotes.textContent = '📥 Auto-Import System rclone.conf';
  }
}

async function loadRawConfig() {
  try {
    const res = await fetch('/api/remotes/raw');
    const data = await res.json();
    rawConfigTextarea.value = data.config_text;
  } catch (err) {
    alert(`Failed to load raw config: ${err.message}`);
  }
}

async function saveRawConfig() {
  btnSaveRawConfig.textContent = 'Saving...';
  try {
    const res = await fetch('/api/remotes/raw', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ config_text: rawConfigTextarea.value })
    });
    const data = await res.json();
    alert(data.message || 'Configuration saved successfully!');
    await fetchRemotes();
  } catch (err) {
    alert(`Save error: ${err.message}`);
  } finally {
    btnSaveRawConfig.textContent = 'Save bclone.conf';
  }
}

function populateCryptBaseRemotes() {
  cryptBaseRemote.innerHTML = '';
  const nonCryptRemotes = remotesList.filter(r => !r.is_crypt);
  if (nonCryptRemotes.length === 0) {
    cryptBaseRemote.innerHTML = '<option value="">No base cloud remotes available (add one first)</option>';
    return;
  }
  nonCryptRemotes.forEach(r => {
    const opt = document.createElement('option');
    opt.value = r.name;
    opt.textContent = `${r.name} (${r.type.toUpperCase()})`;
    cryptBaseRemote.appendChild(opt);
  });
}

async function createCryptVault() {
  const vaultName = cryptVaultName.value.trim();
  const baseRemote = cryptBaseRemote.value;
  const basePath = cryptBasePath.value.trim() || 'EncryptedVault';
  const password = cryptPassword.value;
  const salt = cryptSalt.value;

  if (!vaultName || !baseRemote || !password) {
    alert('Vault Name, Base Remote, and Password are required.');
    return;
  }

  btnCreateCrypt.textContent = 'Initializing Crypt Vault...';
  try {
    const res = await fetch('/api/remotes/crypt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        vault_name: vaultName,
        base_remote: baseRemote,
        base_path: basePath,
        password: password,
        salt: salt,
        filename_encryption: 'standard',
        directory_name_encryption: true
      })
    });
    const result = await res.json();
    if (result.success) {
      alert(`Encrypted Crypt Vault '${vaultName}' created! Any files sent here will be client-side encrypted before upload.`);
      cryptVaultName.value = '';
      cryptPassword.value = '';
      cryptSalt.value = '';
      await fetchRemotes();
      switchRemotesTab('list');
    } else {
      alert(`Could not create Crypt vault: ${result.stderr || 'Error'}`);
    }
  } catch (err) {
    alert(`Crypt creation error: ${err.message}`);
  } finally {
    btnCreateCrypt.textContent = 'Initialize AES-256 Crypt Vault';
  }
}

async function testRemoteConnection(name) {
  try {
    const res = await fetch('/api/remotes/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ remote_name: name })
    });
    const data = await res.json();
    alert(`[${name}] ${data.message}`);
  } catch (err) {
    alert(`Test error: ${err.message}`);
  }
}

async function browseRemoteFiles(name) {
  try {
    const res = await fetch(`/api/remotes/${name}/files`);
    const files = await res.json();
    if (files.length === 0) {
      alert(`[${name}] No files or directory is empty.`);
    } else {
      const names = files.map(f => `${f.IsDir ? '📁' : '📄'} ${f.Name} (${f.Size ? Math.round(f.Size / 1024 / 1024) + 'MB' : 'folder'})`).join('\n');
      alert(`Files in [${name}]:\n\n${names}`);
    }
  } catch (err) {
    alert(`Browse error: ${err.message}`);
  }
}

async function deleteRemote(name) {
  if (!confirm(`Are you sure you want to delete remote '${name}'?`)) return;
  try {
    await fetch(`/api/remotes/${name}`, { method: 'DELETE' });
    await fetchRemotes();
  } catch (err) {
    alert(`Delete error: ${err.message}`);
  }
}
