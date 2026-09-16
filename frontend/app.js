// SaaSquatch Leads — Clean, Professional Client Controller
// Integrated Slide-Over Deal Inspector, Pipeline Stage Management & Notes

document.addEventListener('DOMContentLoaded', () => {
  // State
  let leadsData = [];
  let currentLead = null;
  let searchTimeout = null;

  // DOM Elements - Metrics
  const statTotal = document.getElementById('stat-total');
  const statHighPriority = document.getElementById('stat-high-priority');
  const statVerifiedRate = document.getElementById('stat-verified-rate');
  const statAvgScore = document.getElementById('stat-avg-score');

  // DOM Elements - Filters
  const filterSearch = document.getElementById('filter-search');
  const filterIndustry = document.getElementById('filter-industry');
  const filterIcp = document.getElementById('filter-icp');
  const filterStatus = document.getElementById('filter-status');
  const btnResetFilters = document.getElementById('btn-reset-filters');
  const selectSort = document.getElementById('select-sort');
  const leadCount = document.getElementById('lead-count');
  const leadsTbody = document.getElementById('leads-tbody');
  const emptyState = document.getElementById('empty-state');
  const btnEmptyReset = document.getElementById('btn-empty-reset');
  const btnEmptyIngest = document.getElementById('btn-empty-ingest');
  const btnExportCsv = document.getElementById('btn-export-csv');

  // DOM Elements - Scrape Modal
  const modalScrape = document.getElementById('modal-scrape');
  const btnOpenScrapeModal = document.getElementById('btn-open-scrape-modal');
  const btnCloseScrapeModal = document.getElementById('btn-close-scrape-modal');
  const btnCancelScrape = document.getElementById('btn-cancel-scrape');
  const formScrape = document.getElementById('form-scrape');
  const inputScrapeDomain = document.getElementById('input-scrape-domain');
  const scrapeProgress = document.getElementById('scrape-progress');
  const scrapeErrorBox = document.getElementById('scrape-error-box');
  const scrapeErrorText = document.getElementById('scrape-error-text');
  const btnSubmitScrape = document.getElementById('btn-submit-scrape');

  // DOM Elements - Slide-Over Deal Inspector Drawer
  const drawerBackdrop = document.getElementById('drawer-backdrop');
  const btnCloseDrawer = document.getElementById('btn-close-drawer');
  const detailAvatar = document.getElementById('detail-avatar');
  const detailCompanyName = document.getElementById('detail-company-name');
  const detailIcpBadge = document.getElementById('detail-icp-badge');
  const detailDomainLink = document.getElementById('detail-domain-link');
  const drawerCurrentStageText = document.getElementById('drawer-current-stage-text');
  const drawerStageSelect = document.getElementById('drawer-stage-select');
  const detailAiSummary = document.getElementById('detail-ai-summary');
  const detailSignalsList = document.getElementById('detail-signals-list');
  const detailRevenue = document.getElementById('detail-revenue');
  const detailEmployees = document.getElementById('detail-employees');
  const detailIndustry = document.getElementById('detail-industry');
  const detailLocation = document.getElementById('detail-location');
  const detailTechStack = document.getElementById('detail-tech-stack');
  const detailEmail = document.getElementById('detail-email');
  const detailPhone = document.getElementById('detail-phone');
  const detailLinkedin = document.getElementById('detail-linkedin');
  const drawerNotesInput = document.getElementById('drawer-notes-input');
  const btnSaveNotes = document.getElementById('btn-save-notes');

  // Outreach Elements
  const selectOutreachType = document.getElementById('select-outreach-type');
  const btnGenerateOutreach = document.getElementById('btn-generate-outreach');
  const outreachSubject = document.getElementById('outreach-subject');
  const outreachBody = document.getElementById('outreach-body');
  const btnCopyEmail = document.getElementById('btn-copy-email');

  // Toast Container
  const toastContainer = document.getElementById('toast-container');

  // ==========================================
  // Security: XSS Sanitization
  // ==========================================
  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // ==========================================
  // Clean Toast Feedback
  // ==========================================
  function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = 'toast-msg';
    const iconSpan = document.createElement('span');
    iconSpan.style.color = type === 'success' ? '#10b981' : '#f43f5e';
    iconSpan.style.fontWeight = '700';
    iconSpan.textContent = type === 'success' ? '✓' : 'ℹ';

    const textSpan = document.createElement('span');
    textSpan.textContent = ` ${message}`;

    toast.appendChild(iconSpan);
    toast.appendChild(textSpan);
    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(6px)';
      toast.style.transition = 'all 160ms cubic-bezier(0.16, 1, 0.3, 1)';
      setTimeout(() => toast.remove(), 170);
    }, 2800);
  }

  // ==========================================
  // Fetch Summary Stats
  // ==========================================
  async function loadStats() {
    try {
      const res = await fetch('/api/stats');
      if (!res.ok) return;
      const stats = await res.json();
      statTotal.textContent = stats.total_leads;
      statHighPriority.textContent = stats.high_priority_targets;
      const rate = stats.total_leads > 0 
        ? Math.round((stats.verified_leads / stats.total_leads) * 100) 
        : 0;
      statVerifiedRate.textContent = `${rate}%`;
      statAvgScore.textContent = stats.avg_icp_score;
    } catch (e) {
      console.error("Failed to load metrics", e);
    }
  }

  // ==========================================
  // Skeleton Loading Table State
  // ==========================================
  function renderSkeletonTable() {
    emptyState.classList.add('hidden');
    leadsTbody.innerHTML = Array(5).fill(0).map(() => `
      <tr class="skeleton-row">
        <td>
          <div class="col-company">
            <div class="company-avatar-box"><div class="skeleton-shimmer" style="width:16px; height:16px; border-radius:3px;"></div></div>
            <div class="company-text-meta" style="gap:5px;">
              <div class="skeleton-shimmer" style="width:110px;"></div>
              <div class="skeleton-shimmer" style="width:75px; height:9px;"></div>
            </div>
          </div>
        </td>
        <td><div class="skeleton-shimmer" style="width:85px;"></div></td>
        <td>
          <div class="skeleton-shimmer" style="width:90px; margin-bottom:4px;"></div>
          <div class="skeleton-shimmer" style="width:50px; height:9px;"></div>
        </td>
        <td><div class="skeleton-shimmer" style="width:65px;"></div></td>
        <td><div class="skeleton-shimmer" style="width:95px; height:24px; border-radius:4px;"></div></td>
        <td><div class="skeleton-shimmer" style="width:75px; height:20px; border-radius:12px;"></div></td>
        <td style="text-align:right;"><div class="skeleton-shimmer" style="width:55px; height:26px; border-radius:6px;"></div></td>
      </tr>
    `).join('');
  }

  // ==========================================
  // Fetch Leads List
  // ==========================================
  async function loadLeads() {
    const query = filterSearch.value.trim();
    const industry = filterIndustry.value;
    const minIcp = filterIcp.value;
    const status = filterStatus.value;
    const sortBy = selectSort.value;

    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (industry && industry !== 'all') params.append('industry', industry);
    if (minIcp && minIcp !== '0') params.append('min_icp', minIcp);
    if (status && status !== 'all') params.append('verification_status', status);
    if (sortBy) params.append('sort_by', sortBy);

    btnExportCsv.href = `/api/export/csv?${params.toString()}`;
    renderSkeletonTable();

    try {
      const res = await fetch(`/api/leads?${params.toString()}`);
      const data = await res.json();
      leadsData = data.leads || [];
      renderLeadsTable(leadsData);
    } catch (e) {
      console.error("Failed to load leads", e);
      showToast("Error retrieving leads", "error");
    }
  }

  // ==========================================
  // Render Leads Table
  // ==========================================
  function renderLeadsTable(leads) {
    leadsTbody.innerHTML = '';
    leadCount.textContent = leads.length;

    if (leads.length === 0) {
      emptyState.classList.remove('hidden');
      return;
    }
    emptyState.classList.add('hidden');

    leads.forEach(lead => {
      const tr = document.createElement('tr');
      const initial = (lead.company_name || lead.domain).charAt(0).toUpperCase();
      const isHigh = lead.icp_score >= 85;
      const scoreClass = isHigh ? 'score-high-val' : 'score-mid-val';
      const scorePrefix = isHigh ? '<span class="score-star-glyph" aria-hidden="true">★</span> ' : '';
      const stage = lead.pipeline_stage || 'New Target';

      const safeId = parseInt(lead.id, 10);
      const safeIcp = parseInt(lead.icp_score, 10);
      const safeInitial = escapeHtml(initial);
      const safeCompany = escapeHtml(lead.company_name);
      const safeDomain = escapeHtml(lead.domain);
      const safeIndustry = escapeHtml(lead.industry || 'Software');
      const safeRevenue = escapeHtml(lead.estimated_revenue || '$1M - $5M');
      const safeEmployees = escapeHtml(lead.employee_count || '10-50');
      const safeStage = escapeHtml(stage);

      const isVerified = lead.verification_status === 'verified';
      const statusPill = isVerified
        ? `<span class="status-pill status-verified" aria-label="Status: Verified live"><span aria-hidden="true">✓</span> Verified</span>`
        : `<span class="status-pill status-flagged" aria-label="Status: Flagged domain"><span aria-hidden="true">⚠</span> Flagged</span>`;

      tr.innerHTML = `
        <td>
          <div class="col-company">
            <div class="company-avatar-box">${safeInitial}</div>
            <div class="company-text-meta">
              <span class="company-main-name">${safeCompany}</span>
              <span class="company-domain-sub">${safeDomain}</span>
            </div>
          </div>
        </td>
        <td>
          <span class="pill-sector">${safeIndustry}</span>
        </td>
        <td>
          <div style="font-weight:600; color:#fff;">${safeRevenue}</div>
          <div style="font-size:0.75rem; color:var(--text-muted);">${safeEmployees}</div>
        </td>
        <td>
          <span class="score-badge-inline ${scoreClass}">${scorePrefix}${safeIcp} / 100</span>
        </td>
        <td>
          <select class="stage-select-dropdown inline-stage-select" data-id="${safeId}">
            <option value="New Target" ${stage==='New Target'?'selected':''}>New Target</option>
            <option value="Under Review" ${stage==='Under Review'?'selected':''}>Under Review</option>
            <option value="Outreach Sent" ${stage==='Outreach Sent'?'selected':''}>Outreach Sent</option>
            <option value="Qualified Lead" ${stage==='Qualified Lead'?'selected':''}>Qualified Lead</option>
            <option value="Passed" ${stage==='Passed'?'selected':''}>Passed</option>
          </select>
        </td>
        <td>
          ${statusPill}
        </td>
        <td style="text-align: right;">
          <button class="btn btn-secondary btn-sm btn-inspect" data-id="${safeId}">
            Inspect
          </button>
        </td>
      `;

      // Clicking row opens inspector (unless clicking the stage select dropdown)
      tr.addEventListener('click', (e) => {
        if (!e.target.closest('.inline-stage-select')) {
          openDealDrawer(lead.id);
        }
      });

      leadsTbody.appendChild(tr);
    });

    // Inline stage change
    document.querySelectorAll('.inline-stage-select').forEach(sel => {
      sel.addEventListener('change', async (e) => {
        e.stopPropagation();
        const id = parseInt(sel.getAttribute('data-id'), 10);
        const newStage = sel.value;
        await updateDealStage(id, newStage);
      });
    });
  }

  // ==========================================
  // Update Deal Stage
  // ==========================================
  async function updateDealStage(leadId, stage) {
    try {
      const res = await fetch(`/api/leads/${leadId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pipeline_stage: stage })
      });
      if (res.ok) {
        showToast(`Stage updated to "${stage}"`);
        if (currentLead && currentLead.id === leadId) {
          currentLead.pipeline_stage = stage;
          drawerCurrentStageText.textContent = stage;
          drawerStageSelect.value = stage;
        }
      }
    } catch (e) {
      showToast("Failed to update deal stage", "error");
    }
  }

  // ==========================================
  // Open Deal Slide-Over Drawer
  // ==========================================
  async function openDealDrawer(leadId) {
    try {
      const res = await fetch(`/api/leads/${leadId}`);
      if (!res.ok) return;
      const lead = await res.json();
      currentLead = lead;

      detailAvatar.textContent = (lead.company_name || lead.domain).charAt(0).toUpperCase();
      detailCompanyName.textContent = lead.company_name;
      const isHigh = lead.icp_score >= 85;
      detailIcpBadge.className = `score-badge-inline ${isHigh ? 'score-high-val' : 'score-mid-val'}`;
      detailIcpBadge.innerHTML = `${isHigh ? '<span class="score-star-glyph" aria-hidden="true">★</span> ' : ''}${lead.icp_score} ICP Score`;
      detailDomainLink.textContent = lead.domain;
      const cleanTargetDomain = (lead.domain || '').replace(/[^a-zA-Z0-9.-]/g, '');
      detailDomainLink.href = `https://${cleanTargetDomain}`;

      const stage = lead.pipeline_stage || 'New Target';
      drawerCurrentStageText.textContent = stage;
      drawerStageSelect.value = stage;
      drawerNotesInput.value = lead.notes || '';

      detailAiSummary.textContent = lead.ai_summary || lead.description || "No AI summary generated.";

      // Value drivers
      detailSignalsList.innerHTML = '';
      (lead.acquisition_signals || []).forEach(sig => {
        const li = document.createElement('li');
        li.textContent = sig;
        detailSignalsList.appendChild(li);
      });

      detailRevenue.textContent = lead.estimated_revenue || '$1M - $5M';
      detailEmployees.textContent = lead.employee_count || '11-50';
      detailIndustry.textContent = lead.industry || 'B2B SaaS';
      detailLocation.textContent = lead.location || 'United States';

      // Tech Stack
      detailTechStack.innerHTML = '';
      (lead.tech_stack || []).forEach(tech => {
        const chip = document.createElement('span');
        chip.className = 'tech-chip-item';
        chip.textContent = tech;
        detailTechStack.appendChild(chip);
      });
      if (!lead.tech_stack || lead.tech_stack.length === 0) {
        detailTechStack.innerHTML = '<span style="color:var(--text-muted); font-size:0.8rem;">Standard Web Technologies</span>';
      }

      // Contacts
      detailEmail.textContent = lead.contact_email || 'Verified via domain routing';
      detailPhone.textContent = lead.phone || 'Direct line requested';
      if (lead.linkedin_url && (lead.linkedin_url.startsWith('https://') || lead.linkedin_url.startsWith('http://'))) {
        detailLinkedin.href = lead.linkedin_url;
        detailLinkedin.style.display = 'inline';
      } else {
        detailLinkedin.style.display = 'none';
      }

      drawerBackdrop.classList.remove('hidden');

      // Generate cold email copy
      generateOutreach();
    } catch (e) {
      console.error("Error opening deal drawer", e);
      showToast("Error opening deal inspector", "error");
    }
  }

  // Drawer stage change
  drawerStageSelect.addEventListener('change', async () => {
    if (!currentLead) return;
    const stage = drawerStageSelect.value;
    await updateDealStage(currentLead.id, stage);
    loadLeads();
  });

  // Save notes
  btnSaveNotes.addEventListener('click', async () => {
    if (!currentLead) return;
    const notes = drawerNotesInput.value.trim();
    try {
      const res = await fetch(`/api/leads/${currentLead.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes: notes })
      });
      if (res.ok) {
        currentLead.notes = notes;
        showToast("Deal notes saved");
      }
    } catch (e) {
      showToast("Failed to save notes", "error");
    }
  });

  // ==========================================
  // Generate Outreach Copy
  // ==========================================
  async function generateOutreach() {
    if (!currentLead) return;
    const outreachType = selectOutreachType.value;

    outreachSubject.textContent = "Synthesizing strategic angle...";
    outreachBody.value = "Drafting personalized pitch tailored to Caprae Capital's operator-first thesis...";

    try {
      const res = await fetch(`/api/leads/${currentLead.id}/outreach`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lead_id: currentLead.id,
          outreach_type: outreachType
        })
      });
      if (!res.ok) throw new Error("Outreach generation failed");
      const data = await res.json();
      outreachSubject.textContent = data.subject;
      outreachBody.value = data.body;
    } catch (e) {
      outreachSubject.textContent = "Error generating draft";
      outreachBody.value = "Could not connect to outreach intelligence engine.";
    }
  }

  // ==========================================
  // Scrape Ingestion Form Submission
  // ==========================================
  formScrape.addEventListener('submit', async (e) => {
    e.preventDefault();
    const domain = inputScrapeDomain.value.trim();
    if (!domain) return;

    if (scrapeErrorBox) scrapeErrorBox.classList.add('hidden');
    scrapeProgress.classList.remove('hidden');
    btnSubmitScrape.disabled = true;

    try {
      const res = await fetch('/api/leads/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url_or_domain: domain, auto_enrich: true })
      });

      const result = await res.json();
      if (!res.ok) throw new Error(result.detail || "Scraping failed");

      showToast(`Ingested & analyzed ${result.lead.company_name}!`);
      modalScrape.classList.add('hidden');
      formScrape.reset();
      if (scrapeErrorBox) scrapeErrorBox.classList.add('hidden');

      await loadStats();
      await loadLeads();

      if (result.lead && result.lead.id) {
        setTimeout(() => openDealDrawer(result.lead.id), 200);
      }
    } catch (err) {
      if (scrapeErrorBox && scrapeErrorText) {
        scrapeErrorText.textContent = err.message || "Failed to ingest target domain.";
        scrapeErrorBox.classList.remove('hidden');
      }
      showToast(err.message || "Failed to ingest target domain", "error");
    } finally {
      scrapeProgress.classList.add('hidden');
      btnSubmitScrape.disabled = false;
    }
  });

  if (btnEmptyIngest) {
    btnEmptyIngest.addEventListener('click', () => {
      modalScrape.classList.remove('hidden');
      inputScrapeDomain.focus();
    });
  }

  // Sample chips
  document.querySelectorAll('.sample-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      inputScrapeDomain.value = chip.getAttribute('data-domain');
      if (scrapeErrorBox) scrapeErrorBox.classList.add('hidden');
    });
  });

  // Modal / Drawer Toggles
  btnOpenScrapeModal.addEventListener('click', () => {
    modalScrape.classList.remove('hidden');
    inputScrapeDomain.focus();
  });
  btnCloseScrapeModal.addEventListener('click', () => modalScrape.classList.add('hidden'));
  btnCancelScrape.addEventListener('click', () => modalScrape.classList.add('hidden'));

  btnCloseDrawer.addEventListener('click', () => drawerBackdrop.classList.add('hidden'));
  drawerBackdrop.addEventListener('click', (e) => {
    if (e.target === drawerBackdrop) drawerBackdrop.classList.add('hidden');
  });

  // Keyboard shortcuts: '/' focuses search, 'Escape' closes drawer/modal
  window.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement !== filterSearch && !modalScrape.contains(document.activeElement) && !drawerBackdrop.contains(document.activeElement)) {
      e.preventDefault();
      filterSearch.focus();
    } else if (e.key === 'Escape') {
      modalScrape.classList.add('hidden');
      drawerBackdrop.classList.add('hidden');
    }
  });

  // Filter Listeners
  filterSearch.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(loadLeads, 180);
  });

  filterIndustry.addEventListener('change', loadLeads);
  filterIcp.addEventListener('change', loadLeads);
  filterStatus.addEventListener('change', loadLeads);
  selectSort.addEventListener('change', loadLeads);

  function resetAllFilters() {
    filterSearch.value = '';
    filterIndustry.value = 'all';
    filterIcp.value = '0';
    filterStatus.value = 'all';
    selectSort.value = 'icp_score';
    loadLeads();
  }

  btnResetFilters.addEventListener('click', resetAllFilters);
  btnEmptyReset.addEventListener('click', resetAllFilters);

  // Outreach Triggers
  btnGenerateOutreach.addEventListener('click', generateOutreach);
  selectOutreachType.addEventListener('change', generateOutreach);

  // Copy Email to Clipboard
  btnCopyEmail.addEventListener('click', () => {
    const fullText = `Subject: ${outreachSubject.textContent}\n\n${outreachBody.value}`;
    navigator.clipboard.writeText(fullText).then(() => {
      showToast("Email copy copied to clipboard!");
    }).catch(() => {
      showToast("Failed to copy", "error");
    });
  });

  // Initial Load
  loadStats();
  loadLeads();
});
