/* ---------------- ICONS ---------------- */
const ICONS = {
  dashboard: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg>`,
  org: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="5" r="2.5"/><circle cx="5" cy="19" r="2.5"/><circle cx="19" cy="19" r="2.5"/><path d="M12 7.5v4M12 11.5L5 16.5M12 11.5l7 5"/></svg>`,
  assets: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M3 11h18M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>`,
  transfer: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h13l-3-3M20 17H7l3 3"/></svg>`,
  booking: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18M8 2v4M16 2v4"/></svg>`,
  maint: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a4 4 0 0 1-5 5L5 16l2 2 4.7-4.7a4 4 0 0 1 5-5l-2.7 2.7-2-2z"/></svg>`,
  audit: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l2 2 4-4"/><rect x="4" y="3" width="16" height="18" rx="2"/></svg>`,
  reports: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 20V10M12 20V4M20 20v-7"/></svg>`,
  notif: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg>`,
};

const NAV = [
  {id:'dashboard', label:'Dashboard', icon:ICONS.dashboard},
  {id:'org', label:'Organization setup', icon:ICONS.org},
  {id:'assets', label:'Assets', icon:ICONS.assets},
  {id:'transfer', label:'Allocation & Transfer', icon:ICONS.transfer},
  {id:'booking', label:'Resource Booking', icon:ICONS.booking},
  {id:'maint', label:'Maintenance', icon:ICONS.maint},
  {id:'audit', label:'Audit', icon:ICONS.audit},
  {id:'reports', label:'Reports', icon:ICONS.reports},
  {id:'notif', label:'Notifications', icon:ICONS.notif},
];

const TITLES = {
  dashboard:"Dashboard", org:"Organization Setup", assets:"Asset Directory",
  transfer:"Allocation & Transfer", booking:"Resource Booking", maint:"Maintenance Management",
  audit:"Asset Audit", reports:"Reports & Analytics", notif:"Activity Log & Notifications"
};