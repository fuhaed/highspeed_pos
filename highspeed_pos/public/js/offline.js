export function saveOfflineInvoice(entry) {
  const key = 'offline_invoices';
  let entries = [];
  try {
    entries = JSON.parse(localStorage.getItem(key)) || [];
  } catch(e) {
    entries = [];
  }
  entries.push(entry);
  try {
    localStorage.setItem(key, JSON.stringify(entries));
  } catch(e) {
    console.error('Failed to save offline invoice', e);
  }
}

export function isOffline() {
  if (typeof window !== 'undefined' && typeof window.serverOnline === 'boolean') {
    return !navigator.onLine || !window.serverOnline;
  }
  return !navigator.onLine;
}

export function getOfflineInvoices() {
  try {
    return JSON.parse(localStorage.getItem('offline_invoices')) || [];
  } catch(e) {
    return [];
  }
}

export function clearOfflineInvoices() {
  localStorage.removeItem('offline_invoices');
}

export function getPendingOfflineInvoiceCount() {
  return getOfflineInvoices().length;
}

export function setLastSyncTotals(totals) {
  try {
    localStorage.setItem('pos_last_sync_totals', JSON.stringify(totals));
  } catch (e) {
    console.error('Failed to persist last sync totals', e);
  }
}

export function getLastSyncTotals() {
  try {
    return JSON.parse(localStorage.getItem('pos_last_sync_totals')) || { pending: 0, synced: 0, drafted: 0 };
  } catch (e) {
    return { pending: 0, synced: 0, drafted: 0 };
  }
}

export async function syncOfflineInvoices() {
  const invoices = getOfflineInvoices();
  if (!invoices.length) {
    // No invoices to sync; keep previously stored totals
    return getLastSyncTotals();
  }
  if (isOffline()) {
    // When offline just return the pending count without attempting a sync
    return { pending: invoices.length, synced: 0, drafted: 0 };
  }

  const failures = [];
  let synced = 0;
  let drafted = 0;

  for (const inv of invoices) {
    try {
      await frappe.call({
        method: 'highspeed_pos.highspeed_pos.api.hsposapp.submit_invoice',
        args: inv
      });
      synced += 1;
    } catch (err) {
      console.error('Failed to submit invoice, saving as draft', err);
      try {
        await frappe.call({
          method: 'highspeed_pos.highspeed_pos.api.hsposapp.update_invoice',
          args: { data: inv.invoice }
        });
        drafted += 1;
      } catch (draftErr) {
        console.error('Failed to save invoice as draft', draftErr);
        failures.push(inv);
      }
    }
  }

  const pendingLeft = failures.length;

  if (pendingLeft) {
    localStorage.setItem('offline_invoices', JSON.stringify(failures));
  } else {
    clearOfflineInvoices();
  }

  const totals = { pending: pendingLeft, synced, drafted };
  setLastSyncTotals(totals);
  return totals;
}

// IndexedDB Caching Helpers for HIGHSPEED POS
const DB_NAME = 'highspeed_pos_db';
const DB_VERSION = 1;
const STORE_NAME = 'items_cache';

function getDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME);
      }
    };
    request.onsuccess = (event) => resolve(event.target.result);
    request.onerror = (event) => reject(event.target.error);
  });
}

export async function cacheItems(key, items) {
  try {
    const db = await getDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORE_NAME], 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      const plainItems = JSON.parse(JSON.stringify(items));
      const request = store.put(plainItems, key);
      request.onsuccess = () => resolve(true);
      request.onerror = (event) => reject(event.target.error);
    });
  } catch (e) {
    console.error('Failed to cache items in IndexedDB', e);
    return false;
  }
}

export async function getCachedItems(key) {
  try {
    const db = await getDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORE_NAME], 'readonly');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.get(key);
      request.onsuccess = (event) => resolve(event.target.result);
      request.onerror = (event) => reject(event.target.error);
    });
  } catch (e) {
    console.error('Failed to retrieve cached items from IndexedDB', e);
    return null;
  }
}

